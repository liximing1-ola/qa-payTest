# coding=utf-8
import requests
import urllib.parse
import pymysql
import random
import time
def postPayCreate_gift(num):
    url = "https://dev.iambanban.com/pay/create?package=com.imbb.banban.android"
    gift_dict = checkGiftSql()
    print(gift_dict)
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'Postman-Token': "f7d705b2-cf29-4a4a-81ba-2c8c8d0f5ed5",
        "user-token": '0ee5fmt4__2FI5C4hAjxM8QqGmrLVQpzsrNdu1fKNQyGDBj9pXxNpQrvgsBJdddWFiAVwRZ__2BTlFv7C4O6sq0y6Yf5WjdxRKNsJp63WGbfYpbajc3mkftXHpJznn'}
    for i in gift_dict:
        for j in i:
            data = {
                "platform": "available",
                "type": "package",
                "money": int(j[1]) * 100 * num,
                "params":
                    {"rid": 200000930,
                     "uids": "105002315",
                     "positions": "0",
                     "position": -1,
                     "giftId": j[0],
                     "giftNum": num,
                     "price": int(j[1]) * 100,
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

def updateMoneySql(uid, money):
    con, cur = conMysql()
    sql = "update xs_user_money set money{} where uid={} limit 1".format(money, uid)
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
    sql = "select id,price from xs_gift where gift_type='normal' and deleted=0 and price>=1"
    try:
        cur.execute(sql)
        res = cur.fetchall()
        if res is None:
            return ()
        else:
            return res
    except Exception as error:
        con.rollback()
        print('update fail', error)
    finally:
        time.sleep(0.1)
        con.commit()

def main_pay():
    i = 1
    updateMoneySql(128440017, money=1000000000)
    while i < 10000:
        postPayCreate_gift(1)
        time.sleep(1)
        i += 1


if __name__=='__main__':
    postPayCreate_gift(1)