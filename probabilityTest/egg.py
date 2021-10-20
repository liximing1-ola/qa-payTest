# coding=utf-8
import requests
import urllib.parse
import json
import logging
import pymysql
import random
import time
def postPayCreate():
    url = "https://dev.iambanban.com/pay/create?package=com.imbb.banban.android"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'Postman-Token': "f7d705b2-cf29-4a4a-81ba-2c8c8d0f5ed5",
        "user-token": '80f0VpMwTs__2Fb__2BWidJAx60q1CJUZ46MoetFHMfPhJq9P__2F16VRv3rTJidyKNuOsXMqJGZUgQZwKOeyTAjI0RwEM8koV7UeQYZs0L6S__2Bn7auhQgBEr8G36FCM9t'}
    data = {
        "platform": "available",
        "type": "package",
        "money": 200,
        "params":
            {"rid": 200000563,
             "uids": 100287189,
             "positions": "1",
             "position": -1,
             "giftId": 558,
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
    re = requests.post(url, data=data, headers=headers)
    res = json.loads(re.text)
    if res.get('success') > 0:
        logging.info('post success')
    else:
        raise EnvironmentError('测试环境异常:', res.get('msg'))


# 房间赠送箱子
def postPayCreateRoom(giftNum):
    url = 'https://dev.iambanban.com/pay/create?package=com.imbb.banban.android'
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'Postman-Token': "f7d705b2-cf29-4a4a-81ba-2c8c8d0f5ed5",
        "user-token": '8257__2BTAUzHPAI0sZrX6TQ8iLqv__2F__2FT3cRNpUsIQvOiA7noig5GnLyxCWq8Un6P6iIiajb2VxljHscHwAAM2xMU__2FoNzPLla4ai__2FmdmSOxnHXTrx__2FueX2__2BbsLvl'}
    data = {
        "platform": "available",
        "type": "package",
        "money": 600,
        "params":
            {"rid": 193185405,
             "uids": "100287189",
             "positions": "0",
             "giftId": 488,
             "giftNum": giftNum,
             "position": -1,
             "price": giftNum*600,
             "cid": 0,
             "ctype": "",
             "duction_money": 0,
             "version": 2,
             "num": giftNum,
             "gift_type": "bean",
             "exchange":1
             }
    }
    d = urllib.parse.urlencode(data)
    data = d.replace('+', '').replace('%27', '%22')
    re = requests.post(url, data=data, headers=headers)
    res = json.loads(re.text)
    if res.get('success') > 0:
        pass
        # logging.info('post success')
    else:
        raise EnvironmentError('测试环境异常:', res.get('msg'))

# 本地服务器数据库测试用
def conMysql():
    db_config = {"dev_46_db": '192.168.11.46',
                 "dev_46_user": 'root',
                 "dev_46_pas": '123456',
                 "ali_db": 'rm-bp1nfl3dp096d5o39.mysql.rds.aliyuncs.com',
                 "ali_user": 'super',
                 "ali_pas": 'dev123456'}
    con = pymysql.connect(host=db_config['ali_db'],
                          port=3306,
                          user=db_config['ali_user'],
                          passwd=db_config['ali_pas'],
                          charset='utf8')
    con.select_db('xianshi')
    cursor = con.cursor()
    return con, cursor

def giveBox():
    # updateMoneySql(118433132, 100000000)
    # updateBeanSql(100287189)
    num = 1
    while 5000:
        box_num=random.randint(1, 99)
        print('第{}次，随机开箱数{}'.format(num, box_num))
        num=num+1
        postPayCreateRoom(box_num)
        time.sleep(2)

def updateMoneySql(uid, money=0, money_cash=0, money_cash_b=0, money_b=0, gold_coin=0):
    # xs_user_money_extend:money_coupon*2
    # xs_user_money:money
    # money_coupon*2/money=返奖率
    con, cur = conMysql()
    sql = "update xs_user_money set money={}, money_b={}, money_cash={}, money_cash_b={},gold_coin={} where uid={} limit 1"\
            .format(money, money_b, money_cash, money_cash_b, gold_coin, uid)
    try:
        cur.execute(sql)
    except Exception as error:
        con.rollback()
        print('update fail', error)
    finally:
        con.commit()

def updateBeanSql(uid):
    con, cur = conMysql()
    sql = "update xs_user_money_extend set money_coupon=0 where uid={} limit 1".format(uid)
    try:
        cur.execute(sql)
    except Exception as error:
        con.rollback()
        print('update fail', error)
    finally:
        time.sleep(0.1)
        con.commit()


if __name__ == '__main__':
    postPayCreate()
