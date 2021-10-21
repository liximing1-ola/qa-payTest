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
        "user-token": 'd5ebEDTZUx__2Fr39HLI7Pgt0jvVlvxlgGFnBWZsQOSzqLQkR0LKp897obh6O56WqMAtcdd0b__2FMVKAWRgQRm5knamMkjxulS0ZeuscVUu7jRfvrdcaFVgb3rO7R'}
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
    res = requests.post(url, data=data, headers=headers)
    res = res.json()
    print(res)
    if res['success'] != 1:
        pass
    else:
        raise EnvironmentError('error')

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


if __name__ == '__main__':
    main_pay()