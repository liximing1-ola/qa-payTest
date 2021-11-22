# coding=utf-8
import requests
import urllib.parse
import json
import pymysql
import random
import time
# 个人房幸运蛋概率测试
def postPayCreate(giftNum):
    url = "https://dev.iambanban.com/pay/create?package=com.imbb.banban.android"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'Postman-Token': "f7d705b2-cf29-4a4a-81ba-2c8c8d0f5ed5",
        "user-token": '743d1Tu__2FuC__2FXEXOsfDVGwlyBH__2F7Wutu__2B6h8jQxOJgo1MqOCzx1MIdzUOKgEDvy__2Fpwu__2BuTX7gsDKaa__2BnS0XzKpmNZ7wIc0cgEQyyOIWV4ZAvd2BjciV7fOIdk'}
    data = {
        "platform": "available",
        "type": "package",
        "money": 200 * giftNum,
        "params":
            {"rid": 193193484,
             "uids": 100287189,
             "positions": "1",
             "position": -1,
             "giftId": 558,
             "giftNum": giftNum,
             "price": 200,
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


def conMysql():
    db_config = {"dev_46_db": '192.168.11.46',
                 "dev_46_user": 'root',
                 "dev_46_pas": '123456',
                 "ali_db": 'rm-bp1nfl3dp096d5o39.mysql.rds.aliyuncs.com',
                 "ali_user": 'super',
                 "ali_pas": 'dev123456'}
    con = pymysql.connect(host=db_config['dev_46_db'],
                          port=3306,
                          user=db_config['dev_46_user'],
                          passwd=db_config['dev_46_pas'],
                          charset='utf8')
    con.select_db('xianshi')
    cursor = con.cursor()
    return con, cursor


def updateBeanSql(uid, coupon_money):
    con, cur = conMysql()
    sql = "update xs_user_money_extend set money_coupon={} where uid={} limit 1".format(coupon_money, uid)
    try:
        cur.execute(sql)
    except Exception as error:
        con.rollback()
        print('update fail', error)
    finally:
        time.sleep(0.1)
        con.commit()


def main_pay():
    i = 1
    # updateBeanSql(127565486, coupon_money=1000000000)
    # updateBeanSql(100287189, 0)
    while i < 10000:
        num = int(random.choice('136'))
        print('第{}次, 开蛋数为{}'.format(i, num))
        postPayCreate(num)
        time.sleep(0.2)
        i += 1


def main_ktv():
    i = 1
    while i < 10000:
        print('第{}次'.format(i))
        postPayCreate_ktv()
        time.sleep(1)
        i += 1


if __name__ == '__main__':
    main_ktv()