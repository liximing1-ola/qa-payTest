"""日报公共渲染与推送工具：iOS / 鸿蒙 / 周期三条日报共用。

- load_font / cell_x / draw_table：表格图片绘制（单元格支持富样式，行支持合计/超标标记）
- send_wecom_image / send_wecom_msg：企业微信 webhook 推送
- save_local / report_failure：本地留档与任务异常通知
"""
import base64
import contextlib
import hashlib
import logging
import os
import sys

import requests
from PIL import ImageFont

logger = logging.getLogger(__name__)


def _detect_font_dir() -> str:
    """跨平台检测系统字体目录，支持环境变量 FONT_DIR 覆盖。"""
    env_dir = os.environ.get('FONT_DIR')
    if env_dir:
        if os.path.isdir(env_dir):
            return env_dir
        logger.warning('环境变量 FONT_DIR=%s 不存在，回退到自动检测', env_dir)

    if sys.platform == 'win32':
        candidate = r'C:\Windows\Fonts'
    elif sys.platform == 'darwin':
        candidate = '/System/Library/Fonts'
    else:
        candidate = '/usr/share/fonts'

    if os.path.isdir(candidate):
        return candidate
    logger.warning('系统字体目录 %s 不存在，字体加载将使用默认字体', candidate)
    return ''


FONT_DIR = _detect_font_dir()
# 渲染配色（雅黑字体不含彩色 emoji，图标一律用安全字符 ■/▶ 等）
C_TITLE = (28, 62, 120)
C_WARN = (190, 110, 10)
C_TEXT = (45, 45, 45)
C_GRID = (165, 165, 165)
C_HEADER_BG = (226, 232, 240)
C_TOTAL_BG = (243, 246, 252)
# 当日下载超标行：红字 + 浅红底
ALERT_DOWNLOAD_THRESHOLD = 1500
C_ALERT_TEXT = (205, 25, 25)
C_ALERT_BG = (253, 230, 230)


def load_font(size, bold=False):
    for name in (('msyhbd.ttc' if bold else 'msyh.ttc'), 'simsun.ttc'):
        try:
            return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
        except OSError:
            continue
    return ImageFont.load_default()


def cell_x(draw, text, font, col_x, col_w, align):
    """按对齐方式计算单元格文本横坐标"""
    w = draw.textlength(text, font=font)
    if align == 'right':
        return col_x + col_w - 12 - w
    if align == 'center':
        return col_x + (col_w - w) / 2
    return col_x + 12


def draw_table(draw, x, y, headers, rows, font, bold_font, aligns):
    """绘制带表头/网格线的表格，返回底部 y。
    rows 元素为 (cells, is_total[, is_alert])；单元格可为 str 或
    (text, fill[, bold]) 富样式元组（富样式按自身字体测宽，加粗不溢列）。"""
    def cell_style(cell, row_font):
        """返回 (文本, 颜色, 显示字体, 测宽字体)"""
        if isinstance(cell, tuple):
            f = bold_font if (len(cell) > 2 and cell[2]) else font
            return cell[0], cell[1], f, f
        return cell, C_TEXT, row_font, font

    widths = []
    for i, h in enumerate(headers):
        w = draw.textlength(h, font=bold_font)
        for row in rows:
            txt, _, _, mf = cell_style(row[0][i], font)
            w = max(w, draw.textlength(txt, font=mf))
        widths.append(int(w) + 24)
    row_h = font.size + 18
    total_w = sum(widths)

    # 表头
    draw.rectangle([x, y, x + total_w, y + row_h], fill=C_HEADER_BG)
    cy = y + (row_h - font.size) / 2
    cx = x
    for i, h in enumerate(headers):
        draw.text((cell_x(draw, h, bold_font, cx, widths[i], 'left'), cy),
                  h, font=bold_font, fill=C_TEXT)
        cx += widths[i]
    y += row_h

    # 数据行（合计行加粗+浅蓝底；超标行红字+浅红底；单元格富样式优先于行样式）
    for row in rows:
        cells, is_total = row[0], row[1]
        is_alert = row[2] if len(row) > 2 else False
        row_font = bold_font if is_total else font
        if is_total:
            draw.rectangle([x, y, x + total_w, y + row_h], fill=C_TOTAL_BG)
        elif is_alert:
            draw.rectangle([x, y, x + total_w, y + row_h], fill=C_ALERT_BG)
        cy = y + (row_h - font.size) / 2
        cx = x
        for i, cell in enumerate(cells):
            txt, fill, cf, _ = cell_style(cell, row_font)
            if is_alert and not is_total and fill is C_TEXT:
                fill = C_ALERT_TEXT
            draw.text((cell_x(draw, txt, cf, cx, widths[i], aligns[i]), cy),
                      txt, font=cf, fill=fill)
            cx += widths[i]
        # 行分隔线
        draw.line([x, y, x + total_w, y], fill=C_GRID, width=1)
        y += row_h
    # 竖线与外框
    cx = x
    for w in widths:
        draw.line([cx, y - row_h * (len(rows) + 1), cx, y], fill=C_GRID, width=1)
        cx += w
    draw.line([x, y, x + total_w, y], fill=C_GRID, width=1)
    draw.rectangle([x, y - row_h * (len(rows) + 1), x + total_w, y],
                   outline=C_GRID, width=1)
    return y


def save_local(png_bytes: bytes, filename: str):
    """渲染图本地留档一份（排查渲染问题用），写在脚本同目录"""
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(out, 'wb') as f:
        f.write(png_bytes)


def send_wecom_image(webhook: str, png_bytes: bytes):
    """企业微信图片消息推送（表格截图）"""
    payload = {
        "msgtype": "image",
        "image": {
            "base64": base64.b64encode(png_bytes).decode(),
            "md5": hashlib.md5(png_bytes).hexdigest(),
        }
    }
    r = requests.post(webhook, json=payload, timeout=10)
    if r.status_code != 200:
        logger.warning('企微图片推送 HTTP 异常: status=%s, body=%s', r.status_code, r.text)
        return
    resp = r.json()
    errcode = resp.get('errcode', 0)
    if errcode != 0:
        logger.warning('企微图片推送失败: errcode=%s, errmsg=%s', errcode, resp.get('errmsg', ''))
    else:
        logger.info('企微图片推送成功')


def send_wecom_msg(webhook: str, content: str):
    """企业微信文本消息推送（异常通知用）"""
    payload = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    r = requests.post(webhook, json=payload, timeout=10)
    if r.status_code != 200:
        logger.warning('企微推送 HTTP 异常: status=%s, body=%s', r.status_code, r.text)
        return
    resp = r.json()
    errcode = resp.get('errcode', 0)
    if errcode != 0:
        logger.warning('企微推送失败: errcode=%s, errmsg=%s', errcode, resp.get('errmsg', ''))
    else:
        logger.info('企微推送成功')


def report_failure(webhook: str, title: str, detail: str):
    """任务异常通知（推送失败不影响本地打印与退出码）"""
    err_msg = f"【{title}】\n{detail}"
    if webhook:
        with contextlib.suppress(Exception):
            send_wecom_msg(webhook, err_msg)
    logger.info(err_msg)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    )
