# coding=utf-8
import requests
import urllib.parse
import json
import pymysql
import random
import time
def postPayCreate(giftNum):
    url = "https://dev.iambanban.com/pay/create?package=com.imbb.banban.android"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'Postman-Token': "f7d705b2-cf29-4a4a-81ba-2c8c8d0f5ed5",
        "user-token": '80f0VpMwTs__2Fb__2BWidJAx60q1CJUZ46MoetFHMfPhJq9P__2F16VRv3rTJidyKNuOsXMqJGZUgQZwKOeyTAjI0RwEM8koV7UeQYZs0L6S__2Bn7auhQgBEr8G36FCM9t'}
    data = {
        "platform": "available",
        "type": "package",
        "money": 200*giftNum,
        "params":
            {"rid": 200000563,
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
    re = requests.post(url, data=data, headers=headers)
    res = json.loads(re.text)
    if res.get('success') > 0:
        print('success')
    else:
        raise EnvironmentError('测试环境异常:', res.get('msg'))

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

def main():
    i = 0
    updateBeanSql(127565486, coupon_money=1000000000)
    updateBeanSql(100287189, 0)
    time.sleep(30)
    while i > 10000:
        num = int(random.choice('136'))
        postPayCreate(num)
        time.sleep(1)
        num += 1


if __name__ == '__main__':
    main()
