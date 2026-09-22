import sys
import time

import jwt
import requests
import gzip
import io
import json
import base64
import hashlib
from datetime import date, datetime, timedelta, timezone
import os
from dotenv import load_dotenv
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

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

# ========= App Analytics 实时接口（analytics.apple.com，与后台"过去24小时"页同源）=========
ANALYTICS_BASE = "https://analytics.apple.com"
# 产品销量（Product Sales）= 首次下载口径，与后台"产品销量"列一致
ANALYTICS_METRIC = "prodSales"


def get_analytics_session_token(asc_token: str) -> str:
    """ASC JWT 换取 analytics 站点会话 token（后台页面同款 /auth/auth/v2）"""
    resp = requests.post(
        f"{ANALYTICS_BASE}/auth/auth/v2",
        headers={"Authorization": f"Bearer {asc_token}"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    for key in ("token", "accessToken", "sessionToken"):
        if data.get(key):
            return data[key]
    raise Exception(f"analytics 会话响应未识别：{list(data.keys())}")


def get_recent_24h_downloads(asc_token: str = None, verbose: bool = False):
    """最近 24 小时（UTC）监控清单内各 App 产品销量合计。
    返回 (统计窗口描述, {app_id 字符串: 下载数})"""
    if asc_token is None:
        asc_token = get_asc_token()
    session = get_analytics_session_token(asc_token)
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=24)
    body = {
        "startTime": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endTime": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "group": "hour",
        "metric": ANALYTICS_METRIC,
        "adamIds": [int(a["app_id"]) for a in APP_LIST],
    }
    headers = {"Authorization": f"Bearer {session}"}
    url = f"{ANALYTICS_BASE}/api/v2/data/timeseries"
    resp = None
    for attempt in range(2):
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        if resp.status_code in (401, 403) and attempt == 0:
            # 会话 token 短时过期则换新重试一次
            session = get_analytics_session_token(asc_token)
            headers["Authorization"] = f"Bearer {session}"
            continue
        break
    if resp.status_code != 200:
        raise Exception(f"analytics 接口失败 code:{resp.status_code} msg:{resp.text[:300]}")
    data = resp.json()
    if verbose:
        print("[analytics] timeseries 响应样例：", json.dumps(data, ensure_ascii=False)[:2000])
    per_app = {}
    for item in data.get("results", []):
        aid = str(item.get("adamId") or item.get("adamID") or "")
        total = sum(int(float(b.get("value") or 0)) for b in item.get("data", []))
        if aid:
            per_app[aid] = per_app.get(aid, 0) + total
    window = f"{start:%m-%d %H:%M} ~ {now:%m-%d %H:%M}（UTC）"
    return window, per_app

# 常见结算币种对 CNY 的近似折算率（仅用于日报展示，精确对账以 ASC 财务报告为准）
CNY_RATES = {
    'CNY': 1.0, 'EUR': 7.80, 'USD': 7.20, 'JPY': 0.048, 'HKD': 0.92,
    'SGD': 5.40, 'TWD': 0.23, 'AUD': 4.80, 'MYR': 1.55, 'IDR': 0.00045,
}

def _total_cny(proceeds_by_currency: dict) -> float:
    """多币种销售额折算为人民币总额（未知币种按 1.0 计）"""
    return round(sum(CNY_RATES.get(code, 1.0) * amount
                     for code, amount in proceeds_by_currency.items()), 2)

def summarize_day(df, aids):
    """单日统计：监控清单内各 App 的新下载（type1）与历史安装（type3），
    与全账号折算 CNY 销售总额（不分 App，当日一个总数）"""
    per_app = {}
    for aid in aids:
        app_df = df[df['Apple Identifier'] == aid]

        def units(t):
            return int(app_df[app_df['Product Type Identifier'] == t]
                       ['Units'].astype(int).sum())

        per_app[aid] = {'new': units('1'), 'redownload': units('3')}
    proceeds = (df.assign(_p=df['Developer Proceeds'].astype(float))
                  .groupby('Currency of Proceeds')['_p'].sum().to_dict())
    return per_app, _total_cny(proceeds)

# ========= 表格图片渲染（企微 text/markdown 均不渲染表格，走 image 消息）=========
_FONT_DIR = r'C:\Windows\Fonts'
# 渲染配色（雅黑字体不含彩色 emoji，图标一律用安全字符 ■/▶ 等）
_C_TITLE = (28, 62, 120)
_C_WARN = (190, 110, 10)
_C_TEXT = (45, 45, 45)
_C_GRID = (165, 165, 165)
_C_HEADER_BG = (226, 232, 240)
_C_TOTAL_BG = (243, 246, 252)
# 当日下载超标行：红字 + 浅红底
ALERT_DOWNLOAD_THRESHOLD = 1500
_C_ALERT_TEXT = (205, 25, 25)
_C_ALERT_BG = (253, 230, 230)

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

    # 数据行（rows 元素可为二元组或 (cells, is_total, is_alert) 三元组）
    for row in rows:
        cells, is_total = row[0], row[1]
        is_alert = row[2] if len(row) > 2 else False
        row_font = bold_font if is_total else font
        if is_total:
            draw.rectangle([x, y, x + total_w, y + row_h], fill=_C_TOTAL_BG)
        elif is_alert:
            draw.rectangle([x, y, x + total_w, y + row_h], fill=_C_ALERT_BG)
        text_fill = _C_ALERT_TEXT if is_alert and not is_total else _C_TEXT
        cy = y + (row_h - font.size) / 2
        cx = x
        for i, cell in enumerate(cells):
            draw.text((_cell_x(draw, cell, row_font, cx, widths[i], aligns[i]), cy),
                      cell, font=row_font, fill=text_fill)
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

def render_report_image(days_sorted, per_day, day_sales, app_list, warning=None, h24=None) -> bytes:
    """渲染近 7 日日报表格图片：24小时实时下载 + 每个 App 逐日下载量 + 全账号当日销售额汇总"""
    f_title = _load_font(26, bold=True)
    f_block = _load_font(21, bold=True)
    f_cell = _load_font(19)
    f_cell_b = _load_font(19, bold=True)
    f_note = _load_font(15)

    W, X, TOP = 640, 30, 26
    canvas = Image.new('RGB', (W, 1600), 'white')
    draw = ImageDraw.Draw(canvas)
    start, end = days_sorted[0], days_sorted[-1]

    y = TOP
    draw.text((X, y), f"App Store 近7日日报  {start:%m-%d} ~ {end:%m-%d}（{end:%Y}年）",
              font=f_title, fill=_C_TITLE)
    y += 44
    if warning:
        draw.text((X, y), f"注：{warning}", font=f_note, fill=_C_WARN)
        y += 26

    # 最近 24 小时下载（App Analytics 实时口径，与后台"过去24小时"页一致）
    draw.text((X, y), "■ 最近24小时下载（产品销量口径）", font=f_block, fill=_C_TITLE)
    y += 34
    if h24:
        window24, data24 = h24
        draw.text((X, y), f"统计窗口：{window24}", font=f_note, fill=_C_TEXT)
        y += 24
        rows24, total24 = [], 0
        for app in app_list:
            aid = str(app['app_id'])
            v = int(data24.get(aid, 0))
            total24 += v
            rows24.append(((app['name'], f"{v:,}"), False))
        rows24.append((("合计", f"{total24:,}"), True))
        y = _draw_table(draw, X, y, ("App", "24小时下载"),
                        rows24, f_cell, f_cell_b, ('left', 'right'))
    else:
        draw.text((X, y), "（24小时数据获取失败，下方日粒度报表不受影响）",
                  font=f_note, fill=_C_WARN)
        y += 24
    y += 22

    no_stat = {'new': 0, 'redownload': 0}
    for app in app_list:
        aid = str(app['app_id'])
        draw.text((X, y), f"■ {app['name']}", font=f_block, fill=_C_TITLE)
        y += 34
        rows, app_new, app_re = [], 0, 0
        for d in days_sorted:
            stat = per_day[d].get(aid, no_stat)
            app_new += stat['new']
            app_re += stat['redownload']
            day_total = stat['new'] + stat['redownload']
            rows.append(((f"{d:%m-%d}", f"{stat['new']:,}",
                          f"{stat['redownload']:,}"), False,
                         day_total > ALERT_DOWNLOAD_THRESHOLD))
        rows.append((("7日小计", f"{app_new:,}", f"{app_re:,}"), True))
        y = _draw_table(draw, X, y, ("日期", "新下载", "历史安装"),
                        rows, f_cell, f_cell_b, ('left', 'right', 'right'))
        y += 22

    # 销售额汇总（全账号当日总数，不分 App）
    draw.text((X, y), "■ 销售额汇总（全账号）", font=f_block, fill=_C_TITLE)
    y += 34
    rows, total_sales = [], 0.0
    for d in days_sorted:
        v = day_sales[d]
        total_sales += v
        rows.append(((f"{d:%m-%d}", f"{v:,.2f}"), False))
    rows.append((("7日小计", f"{total_sales:,.2f}"), True))
    y = _draw_table(draw, X, y, ("日期", "销售额(¥)"),
                    rows, f_cell, f_cell_b, ('left', 'right'))
    y += 22

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

if __name__ == "__main__":
    yesterday = date.today() - timedelta(days=1)
    # 探测模式：只打印 analytics 24h 接口响应样例，不推送（云端调试验证接口格式用）
    if os.getenv("ASC_PROBE", "").lower() == "true":
        window24, data24 = get_recent_24h_downloads(verbose=True)
        print("[probe] 24h 统计窗口：", window24)
        print("[probe] 24h 各 App 下载：", data24)
        sys.exit(0)
    try:
        # 拉取窗口放宽到 10 天，取最近 7 个有数据的日期（昨日缺报时往前补齐）
        reports = get_recent_reports(10)
        days_sorted = sorted(reports)[-7:]
        # 逐日统计：监控 App 各自下载量 + 全账号当日销售总额
        aids = [str(app['app_id']) for app in APP_LIST]
        stats = {d: summarize_day(reports[d], aids) for d in days_sorted}
        per_day = {d: stats[d][0] for d in days_sorted}
        day_sales = {d: stats[d][1] for d in days_sorted}

        # 最近 24 小时下载（analytics 实时口径），失败不阻塞主报表
        h24 = None
        try:
            h24 = get_recent_24h_downloads()
            print("最近24小时下载：", h24[1])
        except Exception as e24:
            print("24小时数据获取失败（不阻塞主报表）：", e24)

        warning = None
        if yesterday not in reports:
            # Apple 销售日报延迟 1~3 天，10:30 时昨日报告常未生成
            warning = f"昨日({yesterday:%m-%d})报告尚未生成，以下为近7日已可得数据"
        png = render_report_image(days_sorted, per_day, day_sales, APP_LIST, warning, h24)
        # 本地留档一份（排查渲染问题用）
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'asc_daily_report.png'), 'wb') as f:
            f.write(png)
        send_wecom_image(png)
        print("任务执行成功，表格图已推企业微信")
    except Exception as e:
        err_msg = f"【App Store日报任务异常】\n日期:{yesterday}\n错误信息:{str(e)}"
        send_wecom_msg(err_msg)
        print(err_msg)
