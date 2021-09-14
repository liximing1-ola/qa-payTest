# coding=utf-8
import pymysql
import time
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

def selectMoneySql(uid):
    con, cur = conMysql()
    sql = "select money_coupon from xs_user_money_extend where uid={}".format(uid)
    try:
        cur.execute(sql)
        res = cur.fetchone()
        if res is None:
            return 0
        else:
            return res[0]
    except Exception as error:
        print(error)

def insertUserXsBroker(bid):
    con, cur = conMysql()
    sql = "insert into xs_broker (bid,app_id,bname,creater,dateline,types) values({}, {}, '{}', {}, {}, '{}')"\
        .format(bid, 1, '10086', bid, 1571481302, 'live')
    try:
        cur.execute(sql)
    except Exception as error:
        con.rollback()
        print('insert fail', error)
    finally:
        con.commit()

def updateUserXsBroker(bid):
    con, cur = conMysql()
    sql = 'update xs_broker set creater={} where bid={}'.format(bid, bid)
    try:
        cur.execute(sql)
    except Exception as error:
        con.rollback()
        print('update fail', error)
    finally:
        con.commit()


def selectUserXsBroker(bid):
    con, cur = conMysql()
    sql = 'select * from xs_broker where bid={} and creater={}'.format(bid, bid)
    try:
        cur.execute(sql)
        res = cur.fetchone()
        print(res)
        if res is None:
            insertUserXsBroker(bid)
        else:
            updateUserXsBroker(bid)
    except Exception as error:
        print(error)


if __name__ == '__main__':
    selectUserXsBroker(105002314)
