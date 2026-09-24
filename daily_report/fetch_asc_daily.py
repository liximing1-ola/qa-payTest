import time

import jwt
import requests
import gzip
import io
import json
import base64
import hashlib
from datetime import date, timedelta
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

# 常见结算币种对 CNY 的近似折算率（日报统一折算为 USD 展示，精确对账以 ASC 财务报告为准；
# 表外币种按 1.0 计，新币种出现时需及时补表）
CNY_RATES = {
    'CNY': 1.0, 'EUR': 7.80, 'USD': 7.20, 'JPY': 0.048, 'HKD': 0.92,
    'SGD': 5.40, 'TWD': 0.23, 'AUD': 4.80, 'MYR': 1.55, 'IDR': 0.00045,
    'GBP': 9.20, 'CAD': 5.30, 'NZD': 4.35, 'KRW': 0.0052, 'BRL': 1.30,
    'MXN': 0.40, 'PHP': 0.126, 'VND': 0.000285, 'TRY': 0.21, 'AED': 1.96,
    'SAR': 1.92, 'DKK': 1.05, 'HUF': 0.020, 'KZT': 0.0145, 'NGN': 0.0047,
    'ZAR': 0.40, 'EGP': 0.148,
}

def _total_usd(amount_by_currency: dict) -> float:
    """多币种商品销售额折算为美元总额（两位小数展示；未知币种按 1.0 计）"""
    cny = sum(CNY_RATES.get(code, 1.0) * amount
              for code, amount in amount_by_currency.items())
    return round(cny / CNY_RATES['USD'], 2)

def summarize_day(df, aids):
    """单日统计：监控清单内各 App 的新下载（type1）与历史安装（type3），
    与全账号当日商品销售额（顾客支付口径 = 单价×数量，不分 App，折算 USD）"""
    per_app = {}
    for aid in aids:
        app_df = df[df['Apple Identifier'] == aid]

        def units(t):
            return int(app_df[app_df['Product Type Identifier'] == t]
                       ['Units'].astype(int).sum())

        per_app[aid] = {'new': units('1'), 'redownload': units('3')}
    gross = (df.assign(_g=pd.to_numeric(df['Customer Price'], errors='coerce').fillna(0.0)
                       * pd.to_numeric(df['Units'], errors='coerce').fillna(0))
               .groupby('Customer Currency')['_g'].sum().to_dict())
    return per_app, _total_usd(gross)

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

def render_report_image(days_sorted, per_day, day_sales, app_list, m_start, warning=None) -> bytes:
    """渲染近 7 日日报表格图片：每个 App 逐日下载量（底部自然月累计）+ 全账号
    自然月商品销售额（顾客支付口径 = 单价×数量，USD，与后台"销售和趋势"一致）"""
    f_title = _load_font(26, bold=True)
    f_block = _load_font(21, bold=True)
    f_cell = _load_font(19)
    f_cell_b = _load_font(19, bold=True)
    f_sales = _load_font(30, bold=True)
    f_note = _load_font(15)

    W, X, TOP = 640, 30, 26
    canvas = Image.new('RGB', (W, 1600), 'white')
    draw = ImageDraw.Draw(canvas)
    start, end = days_sorted[0], days_sorted[-1]
    # 自然月累计覆盖的日历日（月初 1 号当天即上月整月）
    m_days = [m_start + timedelta(days=i) for i in range((end - m_start).days + 1)]

    y = TOP
    draw.text((X, y), f"App Store 近7日日报  {start:%m-%d} ~ {end:%m-%d}（{end:%Y}年）",
              font=f_title, fill=_C_TITLE)
    y += 44
    if warning:
        draw.text((X, y), f"注：{warning}", font=f_note, fill=_C_WARN)
        y += 26

    no_stat = {'new': 0, 'redownload': 0}
    for app in app_list:
        aid = str(app['app_id'])
        draw.text((X, y), f"■ {app['name']}", font=f_block, fill=_C_TITLE)
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
        y = _draw_table(draw, X, y, ("日期", "新下载", "历史安装"),
                        rows, f_cell, f_cell_b, ('left', 'right', 'right'))
        y += 22

    # 商品销售额（顾客支付口径，全账号自然月累计，与后台"销售和趋势"一致）
    m_sales = sum(day_sales.get(d, 0) for d in m_days)
    draw.text((X, y), f"■ {m_start.month}月商品销售额（自然月，全账号，USD）",
              font=f_block, fill=_C_TITLE)
    y += 40
    draw.text((X + 12, y), f"{m_sales:,.2f}", font=f_sales, fill=_C_TEXT)
    y += 50

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

        warning = None
        if yesterday not in reports:
            # Apple 销售日报延迟 1~3 天，10:30 时昨日报告常未生成
            warning = f"昨日({yesterday:%m-%d})报告尚未生成，以下为近7日已可得数据"
        png = render_report_image(days_sorted, per_day, day_sales, APP_LIST, m_start, warning)
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
