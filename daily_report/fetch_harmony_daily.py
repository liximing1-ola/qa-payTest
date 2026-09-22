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
import os
from datetime import date, datetime, timedelta, timezone

import jwt
import requests
from dotenv import load_dotenv

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
    """获取 AGC 下载安装报表 → 返回 CSV 文本（UTC 日期，区间 ≤180 天）"""
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
    """按日期汇总报表：{日期: {'new','update','total'}}（多维度行自动累加）"""
    by_day = {}
    for row in csv.DictReader(io.StringIO(csv_text)):
        d = (row.get("日期") or "").strip()
        if not d:
            continue

        def num(key):
            v = (row.get(key) or "0").replace(",", "").strip()
            return int(float(v)) if v else 0

        agg = by_day.setdefault(d, {"new": 0, "update": 0, "total": 0})
        agg["new"] += num("新下载成功次数")
        agg["update"] += num("更新下载成功次数")
        agg["total"] += num("总下载成功次数")
    return by_day


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


# ========= 主流程 =========
if __name__ == "__main__":
    try:
        if not PROBE:
            # 正式日报（企微推送）在探测验证通过后实现
            print("日报模式尚未实现，先设置 HARMONY_PROBE=true 运行探测")
            sys.exit(0)

        now = datetime.now(timezone.utc)
        token = get_agc_token()
        print("[probe] AGC token 获取成功")

        start_d, end_d = (now - timedelta(days=7)).date(), now.date()
        csv_text = get_download_report(start_d, end_d, token)
        print(f"[probe] 下载报表区间(UTC)：{start_d} ~ {end_d}，CSV 前 1200 字符：")
        print(csv_text[:1200])
        print("[probe] 下载汇总：", json.dumps(summarize_downloads(csv_text), ensure_ascii=False))

        start_ms = int((now - timedelta(hours=24)).timestamp() * 1000)
        end_ms = int(now.timestamp() * 1000)
        orders = query_iap_orders(start_ms, end_ms)
        print(f"[probe] IAP 近24小时(UTC)订单数：{len(orders)}")
        for o in orders[:3]:
            print("[probe] 订单样例：", json.dumps(o, ensure_ascii=False))
        print("[probe] IAP 汇总：", json.dumps(summarize_orders(orders), ensure_ascii=False))
    except Exception as e:
        print("[harmony] 执行失败：", e)
        sys.exit(1)
