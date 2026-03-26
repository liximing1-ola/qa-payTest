# coding=utf-8
import gevent
from gevent import monkey

monkey.patch_all()

import time
import urllib.parse
import random
import pymysql
import requests
import urllib3

urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ============ 配置 ============
BASE_URL = "https://dev.iambanban.com/pay/create?package=com.imbb.banban.android"
HEADERS_TEMPLATE = {
    'Content-Type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache",
    'Postman-Token': "f7d705b2-cf29-4a4a-81ba-2c8c8d0f5ed5"
}

DB_CONFIG = {
    "host": '192.168.11.46',
    "port": 3306,
    "user": 'root',
    "password": '123456',
    "database": 'xianshi',
    "charset": 'utf8'
}

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


# ============ 数据库操作 ============
def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)


def update_bean(uid, money):
    """更新用户金豆"""
    con = get_db_connection()
    try:
        with con.cursor() as cur:
            sql = f"update xs_user_money set money={money}, money_cash_b=0 where uid={uid} limit 1"
            cur.execute(sql)
        con.commit()
    except Exception as e:
        con.rollback()
        print('update fail', e)
    finally:
        time.sleep(0.3)
        con.close()


# ============ HTTP请求 ============
def send_request(url, data, headers, verify=False):
    """发送POST请求"""
    encoded = urllib.parse.urlencode(data).replace('+', '').replace('%27', '%22')
    res = requests.post(url, data=encoded, headers=headers, verify=verify)
    return res.json()


def check_response(res):
    """检查响应结果"""
    print(res)
    if res.get('success') != 1:
        raise EnvironmentError(res)


# ============ 支付接口 ============
def post_pay_create():
    """个人房幸运蛋概率测试"""
    level = random.randint(1, 3)
    money = EGG_LEVEL_MONEY.get(level)
    
    headers = {**HEADERS_TEMPLATE, "user-token": '0976FcAmUaHnJvJAKi804Ijs2Cm3__2BuamYTrhAVV9baYv2cOWvvuwII2kdNeSKeB8MGHOnQJq878fOl3VKNltq4__2BP7pfIksSLlQs1Y4s50wqo__2Fm3qksqrXTqC'}
    
    data = {
        "platform": "available",
        "type": "package",
        "money": money,
        "params": {
            "rid": 200057467,
            "uids": "105000355",
            "positions": "1",
            "position": -1,
            "giftId": 2602,
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
    
    res = send_request("https://192.168.11.46/pay/create?package=com.imbb.banban.android", data, headers, verify=True)
    check_response(res)


def post_pay_600(gift_num):
    """600金豆支付"""
    headers = {**HEADERS_TEMPLATE, "user-token": '8a2ekYGSBGzQGaeDDD__2FtXwt7q1ZaWC2r7eZViTdlGPPzJ__2FOCEtkXnkzbWnjgkZD8LlEwDsk9ZeanifS5wli8XrqnxZE35cfMCaZw1T10sTWSQgK__2FoDrIAd5H'}
    
    data = {
        "platform": "available",
        "type": "package",
        "money": 600 * gift_num,
        "params": {
            "rid": 200000945,
            "uids": "105002315",
            "positions": "1",
            "position": -1,
            "giftId": 488,
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
    headers = {**HEADERS_TEMPLATE, "user-token": '8082HvzDK1S2DSLztpkriEyegONNJKs01X9PrgDahsEEc5KbEk__2BusZxFOtR__2BalUhDtVjvcC9LgTYtbSdCy9LFlcABHj__2B2nc2NxmSBxHu7__2B7odOfpVyoR4xGq'}
    
    for gift_id, price in GIFT_CONFIG.items():
        data = {
            "platform": "available",
            "type": "package",
            "money": price,
            "params": {
                "rid": 193188260,
                "uids": 100287189,
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
        time.sleep(2)
        check_response(res)


def post_pay_live():
    """直播场景支付"""
    headers = {**HEADERS_TEMPLATE, "user-token": 'd3ccnXDBWkTkXLbr8PuGJegJdEPc6x9Sc__2BW32yxxuOWuNEfsEaHU1o4oKXtPNH9tylxUBv4Tt855126jdSUuZQ0eLMp__2BVLyltuTqHGSas20dOBF6__2FxPn7hc6'}
    
    for gift_id, price in VAP_CONFIG.items():
        data = {
            "platform": "available",
            "type": "package",
            "money": price * 5,
            "params": {
                "rid": 200000934,
                "uids": "100287189,100010150,100010151,100010152,100010153",
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
        time.sleep(2)
        check_response(res)


# ============ 并发测试 ============
def run_concurrent(func, num):
    """执行并发测试"""
    gevent.joinall([gevent.spawn(func) for _ in range(num)])


def main_pay():
    """主入口"""
    update_bean(105002093, 1000000000)
    update_bean(105000355, 0)
    
    for _ in range(100000):
        run_concurrent(post_pay_create, 20)


if __name__ == '__main__':
    main_pay()
