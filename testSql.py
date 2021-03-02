# coding=utf-8
import pymysql

# 调试用
def conMysql():
    _dbUrl = '192.168.11.46'
    _dbPort = 3306
    _user = 'root'
    _password = '123456'
    _dbName = 'xianshi'
    con = pymysql.connect(host=_dbUrl,
                          port=_dbPort,
                          user=_user,
                          passwd=_password,
                          charset='utf8')
    con.select_db(_dbName)
    cursor = con.cursor()
    return con, cursor

def selectUserCommoditySql(uid):
    con, cur = conMysql()
    sql = "select count(*) from xs_user_commodity where uid={}".format(uid)
    try:
        cur.execute(sql)
        res = cur.fetchone()
        if int(res) >= 1:
            deleteUserCommoditySql(uid, int(res))
        else:
            pass
    except Exception as error:
        print(error)

def deleteUserCommoditySql(uid, count):
    con, cur = conMysql()
    sql = "delete from xs_user_commodity where uid={} limit {}".format(uid, count)
    try:
        cur.execute(sql)
    except Exception as error:
        con.rollback()
        print('delete fail', error)
    finally:
        con.commit()

def checkUserCommoditySql(cid, uid):
    con, cur = conMysql()
    sql = "select num from xs_user_commodity where cid={} and uid={} limit 1".format(cid, uid)
    try:
        cur.execute(sql)
        res = cur.fetchone()
        if res is None:
            print('fail')
        if len(res) > 0:
            print(res[0])
            return res[0]
    except Exception as error:
        print(error)

def selectPayChangeOpSql(uid):
    con, cur = conMysql()
    sql = "select op from xs_pay_change_new where uid={} ORDER BY id DESC LIMIT 1".format(uid)
    try:
        cur.execute(sql)
        res = cur.fetchone()
        if len(res) > 0:
            return res[0]
    except Exception as error:
        print(error)

case_dice={'验证余额不足时，私聊一对一打赏': 'pass', '验证余额足够时，私聊一对一打赏': 'pass', '验证开通个人守护的收益分成': 'pass', '验证余额不足时，房间一对一打赏': 'pass', '验证余额足够时，直播类型房间一对一打赏': 'pass', '验证余额足够时，非直播类型房间一对一打赏': 'pass', '验证商城购买单个道具时逻辑': 'pass', '验证商城购买多个道具时逻辑': 'pass', '验证商城购买的道具在房间内赠送给其他人逻辑': 'pass', '验证商城购买的道具在房间内赠送给他人不足的逻辑': 'pass', '验证爵位开通及返钱到余额': 'pass', '验证爵位续费及返钱到余额': 'pass'}
def ltest():
    list_case=[]
    for k, v in case_dice.items():
        list_case.append('Case:{}, 结果:{}'.format(k, v) + '\n')
    return list_case



if __name__ == '__main__':
    print(ltest())
    # selectPayChangeOpSql(103273407)
    # checkUserCommoditySql(329, 103273407)
    # selectUserCommoditySql(100287189)
