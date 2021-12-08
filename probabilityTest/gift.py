# coding=utf-8
import requests
import urllib.parse
import pymysql
import random
import time
def postPayCreate_gift():
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
            "money": v*5,
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

def checkGiftSql():
    con, cur = conMysql()
    sql = "select id,price from xs_gift where gift_type='normal' and deleted =0"
    try:
        cur.execute(sql)
        res = cur.fetchall()
        print(res)
    except Exception as error:
        con.rollback()
        print('update fail', error)
    finally:
        time.sleep(0.1)
        con.commit()


def main_pay():
    i = 1
    # updateBeanSql(128440017, coupon_money=1000000000)
    # updateBeanSql(105002315, 0)
    while i < 10000:
        num = int(random.choice('136'))
        print('第{}次, 开蛋数为{}'.format(i, num))
        postPayCreate_gift(num)
        time.sleep(1)
        i += 1


if __name__=='__main__':
    checkGiftSql()