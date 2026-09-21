# coding=utf-8
import logging
import os
import gevent
from gevent import monkey

monkey.patch_all()

import time
import urllib.parse
import random
import pymysql
import requests
import urllib3
from common.Config import config

logger = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ============ 配置 ============
BASE_URL = "https://dev.iambanban.com/pay/create?package=com.imbb.banban.android"
HEADERS_TEMPLATE = {
    'Content-Type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache",
}

# 用户 Token（从环境变量读取，避免真实凭证入库；过期时在运行环境统一更新）
# 对应环境变量：EGG_TOKEN_CREATE / EGG_TOKEN_PAY600 / EGG_TOKEN_KTV / EGG_TOKEN_LIVE
USER_TOKENS = {
    key: os.environ.get(f'EGG_TOKEN_{key.upper()}', '')
    for key in ('create', 'pay600', 'ktv', 'live')
}

# 房间 / 用户 ID
RID_EGG    = 200057467
RID_PAY600  = 200000945
RID_KTV     = 193188260
RID_LIVE    = 200000934
UID_EGG     = 105000355
UID_PAY600  = 105002315
UID_KTV     = 100287189
UID_LIVE_MULTI = '100287189,100010150,100010151,100010152,100010153'
UID_BEAN_RESET = 105002093

GIFT_ID_EGG   = 2602
GIFT_ID_BEAN  = 488

# 礼物配置
GIFT_CONFIG = {
    35: 52000, 38: 131400, 63: 20, 100: 9900, 226: 600, 286: 5200, 310: 30, 
    315: 20, 446: 300, 450: 1000, 451: 2100, 452: 6600, 455: 13400, 
    488: 600, 495: 1200, 496: 4000, 497: 18800, 560: 100
}

VAP_CONFIG = {
    629: 21, 628: 6, 621: 188, 620: 6, 614: 520, 610: 10, 607: 21, 
    577: 21, 572: 1, 570: 1314, 316: 3344, 322: 188, 330: 30
}

EGG_LEVEL_MONEY = {1: 200, 2: 600, 3: 1200}

# 等待间隔（秒）：DB 写入后的短暂等待、批量送礼的间隔
DB_SETTLE_DELAY: float = 0.3
GIFT_INTERVAL: float = 2.0


# ============ 数据库操作 ============
def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**config.database.dev_config)


def update_bean(uid, money):
    """更新用户金豆"""
    con = get_db_connection()
    try:
        with con.cursor() as cur:
            cur.execute(
                "UPDATE xs_user_money SET money=%s, money_cash_b=0 WHERE uid=%s LIMIT 1",
                (money, uid)
            )
        con.commit()
    except Exception as e:
        con.rollback()
        logger.error('update fail: %s', e)
    finally:
        time.sleep(DB_SETTLE_DELAY)
        con.close()


# ============ HTTP请求 ============
def _build_headers(token_key):
    """构建请求头（统一管理 user-token）"""
    token = USER_TOKENS.get(token_key)
    if not token:
        raise EnvironmentError(
            f"缺少 '{token_key}' 的 token，请设置环境变量 EGG_TOKEN_{token_key.upper()}")
    return {**HEADERS_TEMPLATE, "user-token": token}


def send_request(url, data, headers, verify=False):
    """发送POST请求"""
    encoded = urllib.parse.urlencode(data).replace('+', '').replace('%27', '%22')
    res = requests.post(url, data=encoded, headers=headers, verify=verify)
    return res.json()


def check_response(res):
    """检查响应结果"""
    logger.info(res)
    if res.get('success') != 1:
        raise EnvironmentError(res)


# ============ 支付接口 ============
def post_pay_create():
    """个人房幸运蛋概率测试"""
    level = random.randint(1, 3)
    money = EGG_LEVEL_MONEY.get(level)
    
    headers = _build_headers('create')
    
    data = {
        "platform": "available",
        "type": "package",
        "money": money,
        "params": {
            "rid": RID_EGG,
            "uids": UID_EGG,
            "positions": "1",
            "position": -1,
            "giftId": GIFT_ID_EGG,
            "giftNum": 1,
            "price": money,
            "cid": 0,
            "ctype": "",
            "duction_money": 0,
            "version": 2,
            "num": 1,
            "gift_type": 'normal',
            "useCoin": -1,
            "star": 0,
            "show_pac_man_guide": 1,
            "refer": "",
            "all_mic": 0,
            "egg_level": str(level)
        }
    }
    
    res = send_request(config.pay_url + "com.imbb.banban.android", data, headers, verify=True)
    check_response(res)


def post_pay_600(gift_num):
    """600金豆支付"""
    headers = _build_headers('pay600')
    
    data = {
        "platform": "available",
        "type": "package",
        "money": 600 * gift_num,
        "params": {
            "rid": RID_PAY600,
            "uids": UID_PAY600,
            "positions": "1",
            "position": -1,
            "giftId": GIFT_ID_BEAN,
            "giftNum": gift_num,
            "price": 600,
            "cid": 0,
            "ctype": "",
            "duction_money": 0,
            "version": 2,
            "num": gift_num,
            "gift_type": 'bean',
            "useCoin": -1,
            "star": 0,
            "show_pac_man_guide": 1,
            "refer": "",
            "all_mic": 0
        }
    }
    
    res = send_request(BASE_URL, data, headers)
    check_response(res)


def post_pay_ktv():
    """KTV场景支付"""
    headers = _build_headers('ktv')
    
    for gift_id, price in GIFT_CONFIG.items():
        data = {
            "platform": "available",
            "type": "package",
            "money": price,
            "params": {
                "rid": RID_KTV,
                "uids": UID_KTV,
                "positions": "1",
                "position": -1,
                "giftId": gift_id,
                "giftNum": 1,
                "price": 200,
                "cid": 0,
                "ctype": "",
                "duction_money": 0,
                "version": 2,
                "num": 1,
                "gift_type": 'bean',
                "useCoin": -1,
                "star": 0,
                "show_pac_man_guide": 1,
                "refer": "",
                "all_mic": 0
            }
        }
        
        res = send_request(BASE_URL, data, headers)
        time.sleep(GIFT_INTERVAL)
        check_response(res)


def post_pay_live():
    """直播场景支付"""
    headers = _build_headers('live')
    
    for gift_id, price in VAP_CONFIG.items():
        data = {
            "platform": "available",
            "type": "package",
            "money": price * 5,
            "params": {
                "rid": RID_LIVE,
                "uids": UID_LIVE_MULTI,
                "positions": "0,1,2,3,4",
                "position": -1,
                "giftId": gift_id,
                "giftNum": 1,
                "price": price,
                "cid": 0,
                "ctype": "",
                "duction_money": 0,
                "version": 2,
                "num": 5,
                "gift_type": 'normal',
                "useCoin": -1,
                "star": 0,
                "show_pac_man_guide": 1,
                "refer": "",
                "all_mic": 0
            }
        }
        
        res = send_request(BASE_URL, data, headers)
        time.sleep(GIFT_INTERVAL)
        check_response(res)


# ============ 并发测试 ============
def run_concurrent(func, num):
    """执行并发测试"""
    gevent.joinall([gevent.spawn(func) for _ in range(num)])


def main_pay():
    """主入口"""
    update_bean(UID_BEAN_RESET, 1000000000)
    update_bean(UID_EGG, 0)
    
    for _ in range(100000):
        run_concurrent(post_pay_create, 20)


if __name__ == '__main__':
    main_pay()
