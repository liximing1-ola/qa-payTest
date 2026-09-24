# -*- coding: utf-8 -*-
"""HarmonyOS 数据采集：AGC 下载安装报表（按天）+ IAP 服务端订单查询。
配置来源：脚本同目录 .env.harmony（本机手填 / 云端由 workflow 从 Secrets 写入）。

探测模式：环境变量 HARMONY_PROBE=true 时拉取最近数据并打印样例，用于验证接口连通性。
"""

import sys
import time
import csv
import io
import json
import hashlib
import base64
import os
from datetime import date, datetime, timedelta, timezone

import jwt
import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

# 显式指向脚本同目录的 .env.harmony（任意 CWD 下均能找到配置）
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env.harmony'))

# ========= 配置读取 =========
CLIENT_ID = os.getenv("HARMONY_CLIENT_ID")
CLIENT_SECRET = os.getenv("HARMONY_CLIENT_SECRET")
APP_ID = os.getenv("HARMONY_APP_ID")
IAP_KEY_ID = os.getenv("HARMONY_IAP_KEY_ID")
IAP_ISSUER_ID = os.getenv("HARMONY_IAP_ISSUER_ID")
IAP_KEY_PATH = os.getenv("HARMONY_IAP_KEY_PATH")

# 密钥相对路径按脚本目录解析（本机 Windows / GitHub Actions runner 同一份配置通用）
if IAP_KEY_PATH and not os.path.isabs(IAP_KEY_PATH):
    IAP_KEY_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), IAP_KEY_PATH)

AGC_BASE = "https://connect-api.cloud.huawei.com"   # AppGallery Connect API
IAP_BASE = "https://iap.cloud.huawei.com"           # IAP 服务端（中国站点）

PROBE = os.getenv("HARMONY_PROBE", "").lower() == "true"
# 本地预览不推送：HARMONY_NO_PUSH=true（只渲染留档，不发企微）
NO_PUSH = os.getenv("HARMONY_NO_PUSH", "").lower() == "true"
# 手动强推（workflow force 输入）：绕过就绪检测，无条件发送
FORCE = os.getenv("HARMONY_FORCE", "").lower() == "true"

# 企微 webhook：优先 .env.harmony；缺省回退同目录 .env（与苹果日报同群可复用，无需重复配置）
WECOM_WEBHOOK = os.getenv("WECOM_WEBHOOK")
if not WECOM_WEBHOOK:
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
    WECOM_WEBHOOK = os.getenv("WECOM_WEBHOOK")

# 北京时间（AGC 后台页面口径：销售分析按北京日聚合）
CST = timezone(timedelta(hours=8))

# 日元对人民币近似折算率（1 日元 = 0.048 元，即 1 元 ≈ 20.83 日元；与苹果日报折算表一致）
JPY_CNY_RATE = 0.048


# ========= AGC 授权（API客户端方式）=========
def get_agc_token() -> str:
    """获取 access_token（client_credentials，有效期 48 小时）"""
    resp = requests.post(f"{AGC_BASE}/api/oauth2/v1/token", json={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    token = data.get("access_token")
    if not token:
        raise Exception(f"AGC token 获取失败：{str(data)[:300]}")
    return token


# ========= 下载安装报表 =========
def get_download_report(start_d: date, end_d: date, token: str = None) -> str:
    """获取 AGC 下载安装报表 → 返回 CSV 文本（日期区间 ≤180 天）"""
    if token is None:
        token = get_agc_token()
    url = f"{AGC_BASE}/api/report/harmony-report/v1/harmony/appDownloadAnalysisExport/{APP_ID}"
    headers = {
        "Authorization": f"Bearer {token}",
        "client_id": CLIENT_ID,
        "appId": APP_ID,
    }
    params = {
        "startTime": start_d.strftime("%Y%m%d"),
        "endTime": end_d.strftime("%Y%m%d"),
        "timeType": "day",
        "language": "zh-CN",
        "exportType": "CSV",
    }
    resp = requests.get(url, headers=headers, params=params, timeout=60)
    if resp.status_code != 200:
        raise Exception(f"AGC 报表接口失败 code:{resp.status_code} msg:{resp.text[:300]}")
    data = resp.json()
    ret = data.get("ret") or {}
    if str(ret.get("code")) != "0":
        raise Exception(f"AGC 报表接口返回失败：{str(data)[:300]}")
    file_url = data.get("fileURL")
    if not file_url:
        raise Exception(f"AGC 报表未返回 fileURL：{str(data)[:300]}")
    csv_resp = requests.get(file_url, timeout=60)
    csv_resp.raise_for_status()
    return csv_resp.content.decode("utf-8-sig")


def summarize_downloads(csv_text: str) -> dict:
    """按日期汇总报表：{日期: {'new_download','new_install','uninstall'}}（多维度行自动累加）"""
    by_day = {}
    for row in csv.DictReader(io.StringIO(csv_text)):
        d = (row.get("日期") or "").strip()
        if not d:
            continue

        def num(key):
            v = (row.get(key) or "0").replace(",", "").strip()
            return int(float(v)) if v else 0

        agg = by_day.setdefault(d, {"new_download": 0, "new_install": 0, "uninstall": 0})
        agg["new_download"] += num("新下载成功次数")
        agg["new_install"] += num("新安装成功次数")
        agg["uninstall"] += num("卸载次数")
    return by_day


def agc_not_ready(per_day: dict, end_d: date) -> bool:
    """AGC 昨日下载报表未就绪判定：整行缺失，或"新下载>0 且 新安装=0"。
    报表各列独立管道分批刷出（曝光/卸载先出，"新下载"居中，"新安装"最慢），
    "新安装"是最后一个出的列；若昨日新下载本身为 0 则视为就绪（不等了）。"""
    last = per_day.get(f"{end_d:%Y%m%d}")
    return last is None or (last["new_download"] > 0 and last["new_install"] == 0)


# ========= IAP 服务端（JWT 鉴权 + 订单查询）=========
def _iap_private_key() -> str:
    with open(IAP_KEY_PATH, 'r') as f:
        return f.read()


def get_iap_jwt(body_str: str) -> str:
    """按华为规范生成 ES256 JWT，digest = Body 字符串的 SHA-256（hex）"""
    now = int(time.time())
    payload = {
        "iss": IAP_ISSUER_ID,
        "aud": "iap-v1",
        "iat": now,
        "exp": now + 3600,          # 有效期不得超过 1 小时
        "aid": APP_ID,
        "digest": hashlib.sha256(body_str.encode("utf-8")).hexdigest(),
    }
    return jwt.encode(payload, _iap_private_key(), algorithm="ES256",
                      headers={"kid": IAP_KEY_ID})


def query_iap_orders(start_ms: int, end_ms: int) -> list:
    """查询 [start_ms, end_ms) 内付款/退款订单（窗口 ≤48 小时，自动翻页）"""
    orders = []
    body = {"startTime": start_ms, "endTime": end_ms}
    while True:
        # 固定分隔符序列化，保证 digest 与发送内容逐字节一致
        body_str = json.dumps(body, separators=(",", ":"))
        resp = requests.post(
            f"{IAP_BASE}/order/harmony/v1/application/trade/orders/query",
            data=body_str.encode("utf-8"),
            headers={
                "Authorization": f"Bearer {get_iap_jwt(body_str)}",
                "Content-Type": "application/json;charset=UTF-8",
            },
            timeout=60,
        )
        if resp.status_code != 200:
            raise Exception(f"IAP 订单接口失败 code:{resp.status_code} msg:{resp.text[:300]}")
        data = resp.json()
        if str(data.get("responseCode")) != "0":
            raise Exception(f"IAP 订单接口返回失败：{str(data)[:300]}")
        orders.extend(data.get("orderInfoList") or [])
        continuation = data.get("continuationToken")
        if not continuation:
            break
        body["continuationToken"] = continuation
    return orders


def query_iap_orders_range(start_ms: int, end_ms: int) -> list:
    """查询任意长度区间：按 47 小时切段依次查询后合并（接口单窗口上限 48 小时）"""
    orders = []
    seg_start = start_ms
    while seg_start < end_ms:
        seg_end = min(seg_start + 47 * 3600 * 1000, end_ms)
        orders.extend(query_iap_orders(seg_start, seg_end))
        seg_start = seg_end
    return orders


def summarize_orders(orders: list) -> dict:
    """汇总订单：支付笔数/金额、退款笔数/金额、净额（仅统计 tradeState=0 成功单）"""
    summary = {"purchase_count": 0, "purchase_amount": 0.0,
               "refund_count": 0, "refund_amount": 0.0, "net_amount": 0.0}
    for o in orders:
        if o.get("tradeState") != 0:
            continue
        if o.get("tradeType") == "REFUND":
            summary["refund_count"] += 1
            summary["refund_amount"] += float(o.get("refundMoney") or 0)
        else:
            summary["purchase_count"] += 1
            summary["purchase_amount"] += float(o.get("payMoney") or 0)
    summary["purchase_amount"] = round(summary["purchase_amount"], 2)
    summary["refund_amount"] = round(summary["refund_amount"], 2)
    summary["net_amount"] = round(summary["purchase_amount"] - summary["refund_amount"], 2)
    return summary


def summarize_orders_by_day(orders: list) -> dict:
    """按北京时间日汇总订单：{YYYYMMDD: {count, amount, refund_count, refund_amount}}（仅 tradeState=0）"""
    by_day = {}
    for o in orders:
        if o.get("tradeState") != 0:
            continue
        ts = o.get("tradeTime") or o.get("orderTime") or 0
        d = datetime.fromtimestamp(ts / 1000, tz=CST).strftime("%Y%m%d")
        agg = by_day.setdefault(d, {"count": 0, "amount": 0.0,
                                    "refund_count": 0, "refund_amount": 0.0})
        if o.get("tradeType") == "REFUND":
            agg["refund_count"] += 1
            agg["refund_amount"] += float(o.get("refundMoney") or 0)
        else:
            agg["count"] += 1
            agg["amount"] += float(o.get("payMoney") or 0)
    for agg in by_day.values():
        agg["amount"] = round(agg["amount"], 2)
        agg["refund_amount"] = round(agg["refund_amount"], 2)
    return by_day


# ========= 表格图片渲染（企微 text/markdown 均不渲染表格，走 image 消息）=========
_FONT_DIR = r'C:\Windows\Fonts'
# 渲染配色（雅黑字体不含彩色 emoji，图标一律用安全字符 ■/▶ 等）
_C_TITLE = (28, 62, 120)
_C_WARN = (190, 110, 10)
_C_TEXT = (45, 45, 45)
_C_GRID = (165, 165, 165)
_C_HEADER_BG = (226, 232, 240)
_C_TOTAL_BG = (243, 246, 252)


def _load_font(size, bold=False):
    for name in (('msyhbd.ttc' if bold else 'msyh.ttc'), 'simsun.ttc'):
        try:
            return ImageFont.truetype(os.path.join(_FONT_DIR, name), size)
        except OSError:
            continue
    return ImageFont.load_default()


def _cell_x(draw, text, font, col_x, col_w, align):
    """按对齐方式计算单元格文本横坐标"""
    w = draw.textlength(text, font=font)
    if align == 'right':
        return col_x + col_w - 12 - w
    if align == 'center':
        return col_x + (col_w - w) / 2
    return col_x + 12


def _draw_table(draw, x, y, headers, rows, font, bold_font, aligns):
    """绘制带表头/网格线的表格。rows: [(单元格元组, 是否合计行)]，返回底部 y"""
    widths = []
    for i, h in enumerate(headers):
        w = draw.textlength(h, font=bold_font)
        for row in rows:
            w = max(w, draw.textlength(row[0][i], font=font))
        widths.append(int(w) + 24)
    row_h = font.size + 18
    total_w = sum(widths)

    # 表头
    draw.rectangle([x, y, x + total_w, y + row_h], fill=_C_HEADER_BG)
    cy = y + (row_h - font.size) / 2
    cx = x
    for i, h in enumerate(headers):
        draw.text((_cell_x(draw, h, bold_font, cx, widths[i], 'left'), cy),
                  h, font=bold_font, fill=_C_TEXT)
        cx += widths[i]
    y += row_h

    # 数据行（合计行加粗 + 浅蓝底）
    for cells, is_total in rows:
        row_font = bold_font if is_total else font
        if is_total:
            draw.rectangle([x, y, x + total_w, y + row_h], fill=_C_TOTAL_BG)
        cy = y + (row_h - font.size) / 2
        cx = x
        for i, cell in enumerate(cells):
            draw.text((_cell_x(draw, cell, row_font, cx, widths[i], aligns[i]), cy),
                      cell, font=row_font, fill=_C_TEXT)
            cx += widths[i]
        # 行分隔线
        draw.line([x, y, x + total_w, y], fill=_C_GRID, width=1)
        y += row_h
    # 竖线与外框
    cx = x
    for w in widths:
        draw.line([cx, y - row_h * (len(rows) + 1), cx, y], fill=_C_GRID, width=1)
        cx += w
    draw.line([x, y, x + total_w, y], fill=_C_GRID, width=1)
    draw.rectangle([x, y - row_h * (len(rows) + 1), x + total_w, y],
                   outline=_C_GRID, width=1)
    return y


def render_report_image(days_sorted, per_day, iap_by_day, m_start) -> bytes:
    """渲染近 7 日日报：逐日 新下载/新安装/卸载 + 逐日内购（订单数/金额/退款）；
    表格底部合计行为自然月累计（m_start ~ 最新数据日）"""
    f_title = _load_font(26, bold=True)
    f_block = _load_font(21, bold=True)
    f_cell = _load_font(19)
    f_cell_b = _load_font(19, bold=True)
    f_note = _load_font(15)

    W, X, TOP = 640, 30, 26
    canvas = Image.new('RGB', (W, 1200), 'white')
    draw = ImageDraw.Draw(canvas)
    start, end = days_sorted[0], days_sorted[-1]

    y = TOP
    draw.text((X, y), f"鸿蒙 近7日日报  {start:%m-%d} ~ {end:%m-%d}（{end:%Y}年）",
              font=f_title, fill=_C_TITLE)
    y += 40
    draw.text((X, y), "注：口径与 AGC 后台一致，当日数据次日更新（不含今日）", font=f_note, fill=_C_WARN)
    y += 30

    # 下载安装（新下载 / 新安装 / 卸载）
    no_dl = {"new_download": 0, "new_install": 0, "uninstall": 0}
    draw.text((X, y), "■ 下载安装（AGC 报表）", font=f_block, fill=_C_TITLE)
    y += 34
    rows = []
    for d in days_sorted:
        stat = per_day.get(f"{d:%Y%m%d}", no_dl)
        rows.append(((f"{d:%m-%d}", f"{stat['new_download']:,}",
                      f"{stat['new_install']:,}", f"{stat['uninstall']:,}"), False))
    # 合计行为自然月累计（1 号 ~ 最新数据日；月初 1 号当天即上月整月）
    m_days = [m_start + timedelta(days=i) for i in range((end - m_start).days + 1)]
    s_dl = s_in = s_un = 0
    for d in m_days:
        stat = per_day.get(f"{d:%Y%m%d}", no_dl)
        s_dl += stat["new_download"]
        s_in += stat["new_install"]
        s_un += stat["uninstall"]
    rows.append(((f"{m_start.month}月累计", f"{s_dl:,}", f"{s_in:,}", f"{s_un:,}"), True))
    y = _draw_table(draw, X, y, ("日期", "新下载成功次数", "新安装成功次数", "卸载次数"),
                    rows, f_cell, f_cell_b, ('left', 'right', 'right', 'right'))
    y += 22

    # 内购（逐日：订单数 / 金额 / 退款；金额统一折算 JPY 展示）
    no_iap = {"count": 0, "amount": 0.0, "refund_count": 0, "refund_amount": 0.0}
    draw.text((X, y), "■ 内购（IAP 服务端，JPY）", font=f_block, fill=_C_TITLE)
    y += 34
    rows = []
    for d in days_sorted:
        stat = iap_by_day.get(f"{d:%Y%m%d}", no_iap)
        amt_jpy = int(round(stat["amount"] / JPY_CNY_RATE))
        refund_jpy = int(round(stat["refund_amount"] / JPY_CNY_RATE))
        rows.append(((f"{d:%m-%d}", f"{stat['count']:,}", f"{amt_jpy:,.0f}",
                      f"{stat['refund_count']:,}", f"{refund_jpy:,.0f}"), False))
    # 合计行为自然月累计（金额先整月合并再折算 JPY，避免逐日四舍五入累积误差）
    t_cnt, t_amt_cny, t_rc, t_ra_cny = 0, 0.0, 0, 0.0
    for d in m_days:
        stat = iap_by_day.get(f"{d:%Y%m%d}", no_iap)
        t_cnt += stat["count"]
        t_amt_cny += stat["amount"]
        t_rc += stat["refund_count"]
        t_ra_cny += stat["refund_amount"]
    t_amt = int(round(t_amt_cny / JPY_CNY_RATE))
    t_ra = int(round(t_ra_cny / JPY_CNY_RATE))
    rows.append(((f"{m_start.month}月累计", f"{t_cnt:,}", f"{t_amt:,.0f}", f"{t_rc:,}", f"{t_ra:,.0f}"), True))
    y = _draw_table(draw, X, y, ("日期", "订单数", "金额(JPY)", "退款笔数", "退款金额(JPY)"),
                    rows, f_cell, f_cell_b, ('left', 'right', 'right', 'right', 'right'))
    y += 10

    buf = io.BytesIO()
    canvas.crop((0, 0, W, int(y))).save(buf, format='PNG')
    return buf.getvalue()


# 企业微信图片消息推送（表格截图）
def send_wecom_image(png_bytes: bytes):
    payload = {
        "msgtype": "image",
        "image": {
            "base64": base64.b64encode(png_bytes).decode(),
            "md5": hashlib.md5(png_bytes).hexdigest(),
        }
    }
    r = requests.post(WECOM_WEBHOOK, json=payload, timeout=10)
    print("企微图片推送结果：", r.json())


# 企业微信文本消息推送（异常通知用）
def send_wecom_msg(content: str):
    payload = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    r = requests.post(WECOM_WEBHOOK, json=payload, timeout=10)
    print("企微推送结果：", r.json())


# ========= 主流程 =========
if __name__ == "__main__":
    try:
        now = datetime.now(timezone.utc)

        # ---------- 探测模式：拉数打印样例（不推送）----------
        if PROBE:
            # AGC 下载报表（权限/接口问题不影响下方 IAP 探测）
            try:
                token = get_agc_token()
                print("[probe] AGC token 获取成功")
                start_d, end_d = (now - timedelta(days=7)).date(), now.date()
                csv_text = get_download_report(start_d, end_d, token)
                print(f"[probe] 下载报表区间：{start_d} ~ {end_d}，CSV 前 1200 字符：")
                print(csv_text[:1200])
                print("[probe] 下载汇总：", json.dumps(summarize_downloads(csv_text), ensure_ascii=False))
            except Exception as e:
                print("[probe] 下载报表失败：", e)

            # IAP 订单
            try:
                start_ms = int((now - timedelta(hours=24)).timestamp() * 1000)
                end_ms = int(now.timestamp() * 1000)
                orders = query_iap_orders(start_ms, end_ms)
                print(f"[probe] IAP 近24小时(UTC)订单数：{len(orders)}")
                for o in orders[:3]:
                    print("[probe] 订单样例：", json.dumps(o, ensure_ascii=False))
                print("[probe] IAP 汇总：", json.dumps(summarize_orders(orders), ensure_ascii=False))
            except Exception as e:
                print("[probe] IAP 订单查询失败：", e)
            sys.exit(0)

        # ---------- 正式日报 ----------
        # 统计窗口：最近 7 个完整日（截止昨天；日期口径与 AGC 后台页面一致）
        end_d = datetime.now(CST).date() - timedelta(days=1)
        start_d = end_d - timedelta(days=6)
        days_sorted = [start_d + timedelta(days=i) for i in range(7)]
        # 自然月累计窗口：end_d 所在月 1 号 ~ end_d（月初 1 号时即上月整月）
        m_start = end_d.replace(day=1)
        # 报表请求区间取两者更早日，保证 7 日明细与月累计来自同一批数据
        fetch_start = min(start_d, m_start)

        token = get_agc_token()
        csv_text = get_download_report(fetch_start, end_d, token)
        per_day = summarize_downloads(csv_text)

        # ---------- AGC 就绪检测 ----------
        # 北京 15 点前未就绪则放弃本次（exit 1 → run failure，check 幂等不锁定，
        # 等下一触发点重试）；15 点后强制发送保底（当天必达优先于数据完美）。
        # NO_PUSH 预览跳过检测（预览的目的就是看当前真实状态）；FORCE 手动强推绕过。
        if not NO_PUSH and not FORCE and agc_not_ready(per_day, end_d) \
                and datetime.now(CST).hour < 15:
            last_stat = per_day.get(f"{end_d:%Y%m%d}") or {"new_download": 0}
            print(f"AGC 昨日({end_d})报表未就绪（新下载 {last_stat['new_download']}，"
                  f"新安装仍为 0），本次不发送，等待后续触发点重试")
            sys.exit(1)

        # 内购窗口：北京时间 [fetch_start 00:00, end_d+1 00:00)，与后台"每日销售额"对齐
        start_ms = int(datetime(fetch_start.year, fetch_start.month, fetch_start.day,
                                tzinfo=CST).timestamp() * 1000)
        end_ms = int(datetime(end_d.year, end_d.month, end_d.day,
                              tzinfo=CST).timestamp() * 1000) + 24 * 3600 * 1000
        orders = query_iap_orders_range(start_ms, end_ms)
        iap_by_day = summarize_orders_by_day(orders)

        png = render_report_image(days_sorted, per_day, iap_by_day, m_start)
        # 本地留档一份（排查渲染问题用）
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'harmony_daily_report.png'), 'wb') as f:
            f.write(png)
        if NO_PUSH:
            print("本地预览模式（HARMONY_NO_PUSH=true），已渲染未推送")
        else:
            if not WECOM_WEBHOOK:
                raise Exception("WECOM_WEBHOOK 未配置（.env.harmony 或 .env，云端需写入 HARMONY_ENV_FILE）")
            send_wecom_image(png)
            print("任务执行成功，日报图已推企业微信")
    except Exception as e:
        err_msg = f"【鸿蒙日报任务异常】\n日期:{date.today()}\n错误信息:{str(e)}"
        try:
            if WECOM_WEBHOOK:
                send_wecom_msg(err_msg)
        except Exception:
            pass
        print(err_msg)
        sys.exit(1)
