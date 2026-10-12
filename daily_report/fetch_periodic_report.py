# -*- coding: utf-8 -*-
"""周期汇总报表（周报/月报）：复用两条日报的数据通路，聚合后带环比推送企微。

- 每周一：汇总上周（周一~周日）iOS（App Store）与鸿蒙（AGC+IAP）核心数据
- 每月 1 号：汇总上月整月数据；其余日期静默退出（check job 已提前拦截）
- 环比 = 与前一同期（上上周 / 上上月）对比

手动测试/补发：PERIODIC_FORCE=week|month 指定周期；PERIODIC_NO_PUSH=true 只渲染不推送。
"""
import os
import sys
import io
from datetime import date, datetime, timedelta, timezone

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 表格渲染与企微推送工具（三条日报共用）
from report_common import (
    C_ALERT_TEXT, C_TITLE, C_WARN, draw_table, load_font,
    report_failure, save_local, send_wecom_image,
)
import fetch_asc_daily as asc
import fetch_harmony_daily as hm

CST = timezone(timedelta(hours=8))
FORCE = os.getenv("PERIODIC_FORCE", "").lower()      # week|month（手动指定，用于测试/补发）
NO_PUSH = os.getenv("PERIODIC_NO_PUSH", "").lower() == "true"


def resolve_period(today: date):
    """按北京日期定报表周期，返回 ((本期起,本期止), (上期起,上期止), kind, label)；非周期日返回 None"""
    if FORCE in ("week", "month"):
        kind = FORCE
    elif today.day == 1:
        kind = "month"
    elif today.weekday() == 0:
        kind = "week"
    else:
        return None
    if kind == "week":
        end = today - timedelta(days=1)                # 昨天 = 周日
        start = end - timedelta(days=6)                # 上周一
        label = "周报"
    else:
        end = today - timedelta(days=1)                # 上月末日
        start = end.replace(day=1)                     # 上月 1 号
        label = "月报"
    p_end = start - timedelta(days=1)                  # 上一周期的末日
    p_start = p_end - timedelta(days=(end - start).days)
    return (start, end), (p_start, p_end), kind, label


def asc_period(start: date, end: date) -> dict:
    """iOS 周期汇总：逐日拉销售报表聚合（404 视为当日无销售跳过），
    含全账号合计与分 App（销售/退款/新下载）两级维度"""
    aids = [str(a['app_id']) for a in asc.APP_LIST]
    apps = {aid: {'new': 0, 'sales': 0.0, 'refund_amt': 0.0, 'refund_cnt': 0}
            for aid in aids}
    new = redownload = refund_cnt = 0
    sales = refund_amt = 0.0
    days = 0
    d = start
    while d <= end:
        try:
            df = asc.get_asc_daily_report(d)
        except Exception as e:
            if 'code:404' not in str(e):
                raise
            d += timedelta(days=1)
            continue
        per_app, s, ra, rc = asc.summarize_day(df, aids)
        for aid, st in per_app.items():
            apps[aid]['new'] += st['new']
            apps[aid]['sales'] += st['sales']
            apps[aid]['refund_amt'] += st['refund_amt']
            apps[aid]['refund_cnt'] += st['refund_cnt']
            new += st['new']
            redownload += st['redownload']
        sales += s
        refund_amt += ra
        refund_cnt += rc
        days += 1
        d += timedelta(days=1)
    for a in apps.values():
        a['sales'] = round(a['sales'], 2)
        a['refund_amt'] = round(abs(a['refund_amt']), 2)
    # 账号下其余 App（不在监控清单）的差额：全账号 - 监控 App 之和，保证分项自洽
    apps['_other'] = {
        'new': 0,
        'sales': round(sales - sum(a['sales'] for a in apps.values()), 2),
        'refund_amt': round(round(abs(refund_amt), 2)
                            - sum(a['refund_amt'] for a in apps.values()), 2),
        'refund_cnt': refund_cnt - sum(a['refund_cnt'] for a in apps.values()),
    }
    return {"new": new, "redownload": redownload,
            "sales": round(sales, 2), "refund_amt": round(abs(refund_amt), 2),
            "refund_cnt": refund_cnt, "days": days, "apps": apps}


def hm_period(start: date, end: date) -> dict:
    """鸿蒙周期汇总：下载报表区间一次拉取 + IAP 订单分段拉取后整期聚合"""
    dl = hm.summarize_downloads(hm.get_download_report(start, end))
    start_ms = int(datetime(start.year, start.month, start.day, tzinfo=CST).timestamp() * 1000)
    # 窗口取 [起始日 00:00, 结束日+1 00:00) 北京时间，与日报口径一致
    end_ms = int(datetime(end.year, end.month, end.day, tzinfo=CST).timestamp() * 1000) \
        + 24 * 3600 * 1000
    summary = hm.summarize_orders(hm.query_iap_orders_range(start_ms, end_ms))
    nd = ni = un = 0
    d = start
    while d <= end:
        st = dl.get(f"{d:%Y%m%d}")
        if st:
            nd += st["new_download"]
            ni += st["new_install"]
            un += st["uninstall"]
        d += timedelta(days=1)
    return {"new_download": nd, "new_install": ni, "uninstall": un,
            "iap_count": summary["purchase_count"], "iap_amount": summary["purchase_amount"],
            "refund_count": summary["refund_count"], "refund_amount": summary["refund_amount"]}


def _trend(cur, prev):
    """环比格式化：↑涨 ↓降；波动超过 ±50% 标红加粗；基数为 0 时 0→'—'、有值→'新增'
    返回 str（默认样式）或 (text, fill, bold) 富样式元组"""
    if prev == 0:
        return "—" if cur == 0 else "新增"
    pct = (cur - prev) / prev * 100
    arrow = "↑" if pct > 0 else ("↓" if pct < 0 else "→")
    txt = f"{arrow}{abs(pct):.1f}%"
    return (txt, C_ALERT_TEXT, True) if abs(pct) > 50 else txt


def render_period_image(label, start, end, p_start, p_end,
                        ios: dict, ios_p: dict, hmc: dict, hm_p: dict) -> bytes:
    """渲染周期汇总：iOS / 鸿蒙两个区块，各指标带前一期环比"""
    f_title = load_font(24, bold=True)
    f_block = load_font(21, bold=True)
    f_cell = load_font(19)
    f_cell_b = load_font(19, bold=True)
    f_note = load_font(15)

    W, X, TOP = 640, 30, 26
    canvas = Image.new('RGB', (W, 1100), 'white')
    draw = ImageDraw.Draw(canvas)
    y = TOP
    draw.text((X, y), f"App Store & 鸿蒙 {label}  {start:%m-%d} ~ {end:%m-%d}（{end:%Y}年）",
              font=f_title, fill=C_TITLE)
    y += 40
    draw.text((X, y), f"注：环比前一周期 {p_start:%m-%d} ~ {p_end:%m-%d}；"
                      f"iOS 销售额按 App 分列（顾客支付口径，人民币，含账号下其他应用）",
              font=f_note, fill=C_WARN)
    y += 30

    def block(title, rows):
        nonlocal y
        draw.text((X, y), title, font=f_block, fill=C_TITLE)
        y += 34
        y = draw_table(draw, X, y, ("指标", "本期", "环比"),
                       rows, f_cell, f_cell_b, ('left', 'right', 'right'))
        y += 22

    num = lambda v: f"{v:,}"
    money = lambda v: f"{v:,.2f}"
    ios_rows = []
    for app in asc.APP_LIST:
        aid = str(app['app_id'])
        cur, prev = ios["apps"][aid], ios_p["apps"][aid]
        name = app['name']
        ios_rows += [
            ((f"{name}·新下载", num(cur['new']), _trend(cur['new'], prev['new'])), False),
            ((f"{name}·商品销售额", money(cur['sales']), _trend(cur['sales'], prev['sales'])), False),
            ((f"{name}·退款件数", num(cur['refund_cnt']), _trend(cur['refund_cnt'], prev['refund_cnt'])), False),
            ((f"{name}·退款金额", money(cur['refund_amt']), _trend(cur['refund_amt'], prev['refund_amt'])), False),
        ]
    ios_rows += [
        (("其他应用·商品销售额", money(ios["apps"]["_other"]['sales']),
          _trend(ios["apps"]["_other"]['sales'], ios_p["apps"]["_other"]['sales'])), False),
        (("其他应用·退款件数", num(ios["apps"]["_other"]['refund_cnt']),
          _trend(ios["apps"]["_other"]['refund_cnt'], ios_p["apps"]["_other"]['refund_cnt'])), False),
        (("其他应用·退款金额", money(ios["apps"]["_other"]['refund_amt']),
          _trend(ios["apps"]["_other"]['refund_amt'], ios_p["apps"]["_other"]['refund_amt'])), False),
    ]
    block("■ iOS（App Store）", ios_rows)
    block("■ 鸿蒙", [
        (("新下载成功", num(hmc["new_download"]), _trend(hmc["new_download"], hm_p["new_download"])), False),
        (("新安装成功", num(hmc["new_install"]), _trend(hmc["new_install"], hm_p["new_install"])), False),
        (("卸载", num(hmc["uninstall"]), _trend(hmc["uninstall"], hm_p["uninstall"])), False),
        (("内购订单数", num(hmc["iap_count"]), _trend(hmc["iap_count"], hm_p["iap_count"])), False),
        (("内购金额(元)", money(hmc["iap_amount"]), _trend(hmc["iap_amount"], hm_p["iap_amount"])), False),
        (("退款笔数", num(hmc["refund_count"]), _trend(hmc["refund_count"], hm_p["refund_count"])), False),
        (("退款金额(元)", money(hmc["refund_amount"]), _trend(hmc["refund_amount"], hm_p["refund_amount"])), False),
    ])

    buf = io.BytesIO()
    canvas.crop((0, 0, W, int(y))).save(buf, format='PNG')
    return buf.getvalue()


if __name__ == "__main__":
    today = datetime.now(CST).date()
    try:
        period = resolve_period(today)
        if period is None:
            print(f"{today} 非周期日（非周一且非 1 号），静默退出")
            sys.exit(0)
        (start, end), (p_start, p_end), kind, label = period
        print(f"周期：{label} {start} ~ {end}（环比 {p_start} ~ {p_end}）")
        ios = asc_period(start, end)
        ios_p = asc_period(p_start, p_end)
        hmc = hm_period(start, end)
        hm_prev = hm_period(p_start, p_end)
        png = render_period_image(label, start, end, p_start, p_end, ios, ios_p, hmc, hm_prev)
        save_local(png, 'periodic_report.png')
        if NO_PUSH:
            print("NO_PUSH 模式：已渲染留档，不推送")
            sys.exit(0)
        send_wecom_image(asc.WECOM_WEBHOOK, png)
        print("任务执行成功，周期报表已推企业微信")
    except Exception as e:
        report_failure(asc.WECOM_WEBHOOK, "周期报表任务异常",
                       f"日期:{today}\n错误信息:{str(e)[:400]}")
        # 非零退出：workflow 记为失败，check 幂等不锁定当天，后续触发点可重试补发
        sys.exit(1)
