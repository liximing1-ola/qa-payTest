# coding=utf-8
import gevent
from gevent import monkey

monkey.patch_all()

import time
import urllib.parse

import pymysql
import requests
import urllib3

urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 个人房幸运蛋概率测试
def postPayCreate():
    url = "https://dev.iambanban.com/pay/create?package=com.imbb.banban.android"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'Postman-Token': "f7d705b2-cf29-4a4a-81ba-2c8c8d0f5ed5",
        "user-token": 'cc19BF90fWLBasZjkV5__2B3XOCrWjFDy7pmXlFLascuUUcpJvjvba7NTnN0eTphNyvZBOpvz9wVlBwAZS__2FiM__2BPvRvafKLT__2Fenj8q3GH9HdDMvWm9MQF2fFDAWK'}
    data = {
        "platform": "available",
        "type": "package",
        "money": 200,
        "params":
            {"rid": 200057467,
             "uids": "105000355",
             "positions": "1",
             "position": -1,
             "giftId": 2602,
             "giftNum": 1,
             "price": 200,
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
             }
    }
    d = urllib.parse.urlencode(data)
    data = d.replace('+', '').replace('%27', '%22')
    res = requests.post(url, data=data, headers=headers, verify=False)
    res = res.json()
    if res['success'] == 1:
        pass
    else:
        raise EnvironmentError(res)


def postPayCreate_600(giftNum):
    url = "https://dev.iambanban.com/pay/create?package=com.imbb.banban.android"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'Postman-Token': "f7d705b2-cf29-4a4a-81ba-2c8c8d0f5ed5",
        "user-token": '8a2ekYGSBGzQGaeDDD__2FtXwt7q1ZaWC2r7eZViTdlGPPzJ__2FOCEtkXnkzbWnjgkZD8LlEwDsk9ZeanifS5wli8XrqnxZE35cfMCaZw1T10sTWSQgK__2FoDrIAd5H'}
    data = {
        "platform": "available",
        "type": "package",
        "money": 600 * giftNum,
        "params":
            {"rid": 200000945,
             "uids": "105002315",
             "positions": "1",
             "position": -1,
             "giftId": 488,
             "giftNum": giftNum,
             "price": 600,
             "cid": 0,
             "ctype": "",
             "duction_money": 0,
             "version": 2,
             "num": giftNum,
             "gift_type": 'bean',
             "useCoin": -1,
             "star": 0,
             "show_pac_man_guide": 1,
             "refer": "",
             "all_mic": 0,
             }
    }
    d = urllib.parse.urlencode(data)
    data = d.replace('+', '').replace('%27', '%22')
    res = requests.post(url, data=data, headers=headers)
    res = res.json()
    if res['success'] == 1:
        pass
    else:
        raise EnvironmentError(res)


def postPayCreate_ktv():
    gift_dict = {35: 52000, 38: 131400, 63: 20, 100: 9900, 226: 600, 286: 5200, 310: 30, 315: 20, 446: 300,
                 450: 1000, 451: 2100, 452: 6600, 455: 13400, 488: 600, 495: 1200, 496: 4000, 497: 18800, 560: 100}
    vap_dict = {629: 21, 628: 6, 621: 188, 620: 6, 614: 520, 610: 10, 607: 21, 577: 21, 572: 1, 570: 1314, 316: 3344,
                322: 188, 330: 30}
    url = "https://dev.iambanban.com/pay/create?package=com.imbb.banban.android"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'Postman-Token': "f7d705b2-cf29-4a4a-81ba-2c8c8d0f5ed5",
        "user-token": '8082HvzDK1S2DSLztpkriEyegONNJKs01X9PrgDahsEEc5KbEk__2BusZxFOtR__2BalUhDtVjvcC9LgTYtbSdCy9LFlcABHj__2B2nc2NxmSBxHu7__2B7odOfpVyoR4xGq'}
    for k, v in gift_dict.items():
        data = {
            "platform": "available",
            "type": "package",
            "money": v,
            "params":
                {"rid": 193188260,
                 "uids": 100287189,
                 "positions": "1",
                 "position": -1,
                 "giftId": k,
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
                 "all_mic": 0,
                 }
        }
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        res = requests.post(url, data=data, headers=headers)
        time.sleep(2)
        res = res.json()
        if res['success'] == 1:
            pass
        else:
            raise EnvironmentError(res)


def postPayCreate_live():
    vap_dict = {629: 21, 628: 6, 621: 188, 620: 6, 614: 520, 610: 10, 607: 21, 577: 21, 572: 1, 570: 1314, 316: 3344,
                322: 188, 330: 30}
    url = "https://dev.iambanban.com/pay/create?package=com.imbb.banban.android"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'Postman-Token': "f7d705b2-cf29-4a4a-81ba-2c8c8d0f5ed5",
        "user-token": 'd3ccnXDBWkTkXLbr8PuGJegJdEPc6x9Sc__2BW32yxxuOWuNEfsEaHU1o4oKXtPNH9tylxUBv4Tt855126jdSUuZQ0eLMp__2BVLyltuTqHGSas20dOBF6__2FxPn7hc6'}
    for k, v in vap_dict.items():
        data = {
            "platform": "available",
            "type": "package",
            "money": v * 5,
            "params":
                {"rid": 200000934,
                 "uids": "100287189,100010150,100010151,100010152,100010153",
                 "positions": "0,1,2,3,4",
                 "position": -1,
                 "giftId": k,
                 "giftNum": 1,
                 "price": v,
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
                 "all_mic": 0,
                 }
        }
        d = urllib.parse.urlencode(data)
        data = d.replace('+', '').replace('%27', '%22')
        res = requests.post(url, data=data, headers=headers)
        time.sleep(2)
        res = res.json()
        if res['success'] == 1:
            pass
        else:
            raise EnvironmentError(res)


def conMysql():
    db_config = {"dev_46_db": '192.168.11.46',
                 "dev_46_user": 'root',
                 "dev_46_pas": '123456',
                 }
    con = pymysql.connect(host=db_config['dev_46_db'],
                          port=3306,
                          user=db_config['dev_46_user'],
                          passwd=db_config['dev_46_pas'],
                          charset='utf8')
    con.select_db('xianshi')
    cursor = con.cursor()
    return con, cursor


def updateBeanSql(uid, money):
    con, cur = conMysql()
    sql = "update xs_user_money set money={} where uid={} limit 1".format(money, uid)
    try:
        cur.execute(sql)
    except Exception as error:
        con.rollback()
        print('update fail', error)
    finally:
        time.sleep(0.1)
        con.commit()


def release_test2(num):
    threads = []
    for i in range(num):
        thread = gevent.spawn(postPayCreate)
        threads.append(thread)
    gevent.joinall(threads)


def main_pay():
    i = 1
    updateBeanSql(105002093, 1000000000)
    updateBeanSql(105000355, 0)
    while i < 200000:
        release_test2(20)
        i += 1


if __name__ == '__main__':
    main_pay()
