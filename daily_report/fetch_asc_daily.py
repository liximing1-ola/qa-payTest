import sys
import time

import jwt
import requests
import gzip
import io
import json
from datetime import date, timedelta
import os
from dotenv import load_dotenv
import pandas as pd
from PIL import Image, ImageDraw

# 表格渲染与企微推送工具（三条日报共用）
from report_common import (
    ALERT_DOWNLOAD_THRESHOLD, C_ALERT_TEXT, C_TEXT, C_TITLE, C_WARN,
    draw_table, load_font, report_failure, save_local, send_wecom_image,
)

# 显式指向脚本同目录的 .env（计划任务/任意 CWD 下均能找到配置）
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

# ========= 配置读取 =========
ISSUER_ID = os.getenv("ISSUER_ID")
KEY_ID = os.getenv("KEY_ID")
VENDOR_NUMBER = os.getenv("VENDOR_NUMBER")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")
WECOM_WEBHOOK = os.getenv("WECOM_WEBHOOK")
APP_LIST = json.loads(os.getenv("APP_LIST"))

# 密钥相对路径按脚本目录解析（本机 Windows / GitHub Actions runner 同一份 .env 通用）
if PRIVATE_KEY_PATH and not os.path.isabs(PRIVATE_KEY_PATH):
    PRIVATE_KEY_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), PRIVATE_KEY_PATH)

# 生成ASC JWT Token
def get_asc_token():
    with open(PRIVATE_KEY_PATH, 'r') as f:
        private_key = f.read()
    payload = {
        "iss": ISSUER_ID,
        "exp": int(time.time()) + 1200,
        "aud": "appstoreconnect-v1"
    }
    token = jwt.encode(payload, private_key, algorithm="ES256", headers={"kid": KEY_ID})
    return token

# 获取销售日报gz文件并解析TSV（token 传入可复用，7 日循环只签名一次）
def get_asc_daily_report(report_date: date, token: str = None):
    if token is None:
        token = get_asc_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "filter[frequency]": "DAILY",
        "filter[reportType]": "SALES",
        "filter[reportSubType]": "SUMMARY",
        "filter[reportDate]": report_date.strftime("%Y-%m-%d"),
        "filter[vendorNumber]": VENDOR_NUMBER
    }
    url = "https://api.appstoreconnect.apple.com/v1/salesReports"
    # 404（数据未生成）直接抛给上层回退；其他错误（网络/限流）重试 3 次
    for attempt in range(3):
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        if resp.status_code == 200 or resp.status_code == 404:
            break
        time.sleep(5)
    if resp.status_code != 200:
        raise Exception(f"ASC接口请求失败，code:{resp.status_code}, msg:{resp.text}")
    # 解压gz
    buffer = io.BytesIO(resp.content)
    with gzip.GzipFile(fileobj=buffer) as f:
        raw = f.read().decode("utf-8")
    rows = [line.split("\t") for line in raw.splitlines() if line.strip()]
    df = pd.DataFrame(rows[1:], columns=rows[0])
    return df

# 取最近 N 日销售日报（ASC 数据延迟 1~3 天，未生成日期自动跳过）
def get_recent_reports(days: int = 7):
    token = get_asc_token()
    reports = {}
    for offset in range(1, days + 1):
        report_date = date.today() - timedelta(days=offset)
        try:
            reports[report_date] = get_asc_daily_report(report_date, token)
        except Exception as e:
            # 404 = 该日期报告未生成（无销售数据），跳过继续
            if 'code:404' in str(e):
                continue
            raise
    if not reports:
        raise Exception(f"最近 {days} 天均无销售报告（Apple 数据延迟）")
    return reports

# 补齐 [start_d, end_d] 区间内缺失日期的报表（404 = 该日无数据，跳过；其余错误照常抛）
def backfill_reports(reports: dict, start_d: date, end_d: date):
    token = get_asc_token()
    d = start_d
    while d <= end_d:
        if d not in reports:
            try:
                reports[d] = get_asc_daily_report(d, token)
            except Exception as e:
                if 'code:404' not in str(e):
                    raise
        d += timedelta(days=1)
    return reports

# 常见结算币种对 CNY 的近似折算率（日报统一以人民币（元）展示，精确对账以 ASC 财务报告为准；
# 表外币种按 1.0 计，新币种出现时需及时补表）
CNY_RATES = {
    'CNY': 1.0, 'EUR': 7.80, 'USD': 7.20, 'JPY': 0.048, 'HKD': 0.92,
    'SGD': 5.40, 'TWD': 0.23, 'AUD': 4.80, 'MYR': 1.55, 'IDR': 0.00045,
    'GBP': 9.20, 'CAD': 5.30, 'NZD': 4.35, 'KRW': 0.0052, 'BRL': 1.30,
    'MXN': 0.40, 'PHP': 0.126, 'VND': 0.000285, 'TRY': 0.21, 'AED': 1.96,
    'SAR': 1.92, 'DKK': 1.05, 'HUF': 0.020, 'KZT': 0.0145, 'NGN': 0.0047,
    'ZAR': 0.40, 'EGP': 0.148,
}

def _total_cny(amount_by_currency: dict) -> float:
    """多币种商品销售额折算为人民币总额（两位小数展示；未知币种按 1.0 计）"""
    cny = sum(CNY_RATES.get(code, 1.0) * amount
              for code, amount in amount_by_currency.items())
    return round(cny, 2)

def summarize_day(df, aids):
    """单日统计：监控清单内各 App 的新下载（type1）与历史安装（type3）、
    商品销售额与退款（顾客支付口径 = 单价×数量，按 App 分列，折算人民币）；
    退款即报表中 Units 为负的冲抵行（ASC 无独立退款字段），金额为负值、件数为正数。
    主 App（aids[0] = 不夜星球）吸收账号下其余历史包（家族马甲）的销售额与退款
    ——账号实际在营仅两个 App，马甲包收入退款业务上均归属不夜星球；
    下载类仍按 aid 严格分列（马甲零下载）。
    返回 (per_app, 全账号销售额, 全账号退款金额(负值), 全账号退款件数)"""
    price = pd.to_numeric(df['Customer Price'], errors='coerce').fillna(0.0)
    units_num = pd.to_numeric(df['Units'], errors='coerce').fillna(0)
    df = df.assign(_g=price * units_num, _u=units_num)

    def _agg(sub):
        gross = sub.groupby('Customer Currency')['_g'].sum().to_dict()
        neg = sub[sub['_u'] < 0]
        neg_gross = neg.groupby('Customer Currency')['_g'].sum().to_dict()
        return _total_cny(gross), _total_cny(neg_gross), int(-neg['_u'].sum())

    per_app = {}
    for aid in aids:
        app_df = df[df['Apple Identifier'] == aid]
        sales, refund_amt, refund_cnt = _agg(app_df)
        per_app[aid] = {
            'new': int(app_df.loc[app_df['Product Type Identifier'] == '1', '_u'].sum()),
            'redownload': int(app_df.loc[app_df['Product Type Identifier'] == '3', '_u'].sum()),
            'sales': sales, 'refund_amt': refund_amt, 'refund_cnt': refund_cnt,
        }
    total_sales, total_refund_amt, total_refund_cnt = _agg(df)
    # 账号下其余历史包（不在监控清单的马甲家族）的销售额与退款并入主 App，
    # 使分项之和与全账号合计自洽（业务口径：马甲归不夜星球）
    per_app[aids[0]]['sales'] += total_sales - sum(p['sales'] for p in per_app.values())
    per_app[aids[0]]['refund_amt'] += total_refund_amt - sum(p['refund_amt'] for p in per_app.values())
    per_app[aids[0]]['refund_cnt'] += total_refund_cnt - sum(p['refund_cnt'] for p in per_app.values())
    return per_app, total_sales, total_refund_amt, total_refund_cnt

def render_report_image(days_sorted, per_day, day_sales, day_refund_amt, day_refund_cnt,
                        app_list, m_start, warning=None) -> bytes:
    """渲染近 7 日日报表格图片：每个 App 逐日下载量（底部自然月累计）+ 全账号
    自然月商品销售额（顾客支付口径 = 单价×数量，人民币展示）及月退款（负 Units 冲抵行）"""
    f_title = load_font(26, bold=True)
    f_block = load_font(21, bold=True)
    f_cell = load_font(19)
    f_cell_b = load_font(19, bold=True)
    f_sales = load_font(24, bold=True)
    f_note = load_font(15)

    W, X, TOP = 640, 30, 26
    canvas = Image.new('RGB', (W, 1600), 'white')
    draw = ImageDraw.Draw(canvas)
    start, end = days_sorted[0], days_sorted[-1]
    # 自然月累计覆盖的日历日（月初 1 号当天即上月整月）
    m_days = [m_start + timedelta(days=i) for i in range((end - m_start).days + 1)]

    y = TOP
    draw.text((X, y), f"App Store 近7日日报  {start:%m-%d} ~ {end:%m-%d}（{end:%Y}年）",
              font=f_title, fill=C_TITLE)
    y += 44
    if warning:
        draw.text((X, y), f"注：{warning}", font=f_note, fill=C_WARN)
        y += 26

    no_stat = {'new': 0, 'redownload': 0}
    for app in app_list:
        aid = str(app['app_id'])
        draw.text((X, y), f"■ {app['name']}", font=f_block, fill=C_TITLE)
        y += 34
        rows = []
        for d in days_sorted:
            stat = per_day.get(d, {}).get(aid, no_stat)
            day_total = stat['new'] + stat['redownload']
            rows.append(((f"{d:%m-%d}", f"{stat['new']:,}",
                          f"{stat['redownload']:,}"), False,
                         day_total > ALERT_DOWNLOAD_THRESHOLD))
        m_new = sum(per_day.get(d, {}).get(aid, no_stat)['new'] for d in m_days)
        m_re = sum(per_day.get(d, {}).get(aid, no_stat)['redownload'] for d in m_days)
        rows.append(((f"{m_start.month}月累计", f"{m_new:,}", f"{m_re:,}"), True))
        y = draw_table(draw, X, y, ("日期", "新下载", "历史安装"),
                        rows, f_cell, f_cell_b, ('left', 'right', 'right'))
        y += 22

    # 商品销售额（顾客支付口径，自然月累计，人民币；分 App 列示，退款并入金额行同显，均为负 Units 冲抵行）
    m_sales = sum(day_sales.get(d, 0) for d in m_days)
    m_refund_amt = sum(day_refund_amt.get(d, 0) for d in m_days)
    m_refund_cnt = sum(day_refund_cnt.get(d, 0) for d in m_days)
    draw.text((X, y), f"■ {m_start.month}月商品销售额（自然月，人民币）",
              font=f_block, fill=C_TITLE)
    y += 40

    def _sales_row(name, amt, r_cnt, r_amt):
        nonlocal y
        draw.text((X + 12, y + 5), name, font=f_cell_b, fill=C_TEXT)
        amt_txt = f"{amt:,.2f}"
        draw.text((X + 150, y), amt_txt, font=f_sales, fill=C_TEXT)
        amt_w = draw.textlength(amt_txt, font=f_sales)
        # 退款额度标红（无退款时保持默认色）
        refund_fill = C_ALERT_TEXT if r_amt != 0 else C_TEXT
        draw.text((X + 150 + amt_w + 12, y + 9),
                  f"(退款 {r_cnt:,} 件 / {abs(r_amt):,.2f} 元)",
                  font=f_note, fill=refund_fill)
        y += 44

    for app in app_list:
        aid = str(app['app_id'])
        a_sales = sum(per_day.get(d, {}).get(aid, {}).get('sales', 0) for d in m_days)
        a_ramt = sum(per_day.get(d, {}).get(aid, {}).get('refund_amt', 0) for d in m_days)
        a_rcnt = sum(per_day.get(d, {}).get(aid, {}).get('refund_cnt', 0) for d in m_days)
        _sales_row(app['name'], a_sales, a_rcnt, a_ramt)
    # 马甲家族的销售额/退款已在统计层（summarize_day）并入不夜星球，
    # 分项之和与合计天然自洽，无需“其他应用”差额行
    _sales_row("合计", m_sales, m_refund_cnt, m_refund_amt)
    y += 6

    buf = io.BytesIO()
    canvas.crop((0, 0, W, int(y))).save(buf, format='PNG')
    return buf.getvalue()

if __name__ == "__main__":
    yesterday = date.today() - timedelta(days=1)
    try:
        # 拉取窗口放宽到 10 天，取最近 7 个有数据的日期（昨日缺报时往前补齐）
        reports = get_recent_reports(10)
        days_sorted = sorted(reports)[-7:]
        # 自然月累计窗口：最新数据日所在月 1 号 ~ 最新数据日（月初 1 号当天即上月整月）
        m_start = days_sorted[-1].replace(day=1)
        # 以两个窗口的更早日为起点补拉缺失日期（Apple 数据延迟 1~3 天，月初时月首日可能在近 10 天外）
        span_start = min(days_sorted[0], m_start)
        backfill_reports(reports, span_start, days_sorted[-1])
        # 逐日统计：监控 App 各自下载量 + 全账号当日销售总额（覆盖近7日与月累计两个窗口）
        aids = [str(app['app_id']) for app in APP_LIST]
        span_days = [d for d in reports if span_start <= d <= days_sorted[-1]]
        stats = {d: summarize_day(reports[d], aids) for d in span_days}
        per_day = {d: stats[d][0] for d in span_days}
        day_sales = {d: stats[d][1] for d in span_days}
        day_refund_amt = {d: stats[d][2] for d in span_days}
        day_refund_cnt = {d: stats[d][3] for d in span_days}

        warning = None
        if yesterday not in reports:
            # Apple 销售日报延迟 1~3 天，10:30 时昨日报告常未生成
            warning = f"昨日({yesterday:%m-%d})报告尚未生成，以下为近7日已可得数据"
        png = render_report_image(days_sorted, per_day, day_sales, day_refund_amt, day_refund_cnt, APP_LIST, m_start, warning)
        # 本地留档一份（排查渲染问题用）
        save_local(png, 'asc_daily_report.png')
        send_wecom_image(WECOM_WEBHOOK, png)
        print("任务执行成功，表格图已推企业微信")
    except Exception as e:
        report_failure(WECOM_WEBHOOK, "App Store日报任务异常",
                       f"日期:{yesterday}\n错误信息:{str(e)}")
        # 非零退出：workflow 记为失败，check 幂等不锁定当天，后续触发点可重试补发
        sys.exit(1)
