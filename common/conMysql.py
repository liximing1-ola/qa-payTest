# coding=utf-8
import pymysql
import time
class Mysql:
    db_config = {"dev_46_db": '192.168.11.46',
                 "dev_46_user": 'root',
                 "dev_46_pas": '123456',
                 "ali_db": 'rm-bp1nfl3dp096d5o39.mysql.rds.aliyuncs.com',
                 "ali_user": 'super',
                 "ali_pas": 'dev123456'}
    _dbUrl = db_config['dev_46_db']
    _user = db_config['dev_46_user']
    _password = db_config['dev_46_pas']
    _dbName = 'xianshi'
    _dbPort = 3306

    con = pymysql.connect(host=_dbUrl,
                          port=_dbPort,
                          user=_user,
                          passwd=_password,
                          charset='utf8',
                          autocommit=True)
    con.select_db(_dbName)
    # 断开重连
    con.ping(reconnect=True)
    cur = con.cursor()

    # 更新用户账户余额
    @staticmethod
    def updateMoneySql(uid, money=0, money_cash=0, money_cash_b=0, money_b=0, gold_coin=0):
        sql = "update xs_user_money set money={}, money_b={}, money_cash={}, money_cash_b={},gold_coin={} where uid={} limit 1"\
            .format(money, money_b, money_cash, money_cash_b, gold_coin, uid)
        try:
            Mysql.cur.execute(sql)
        except Exception as error:
            Mysql.con.rollback()
            print('update fail', error)

    # 查询用户所有账户余额总和
    @staticmethod
    def selectAllMoneySql(uid):
        sql = "select money+money_b+money_cash_b+money_cash from xs_user_money where uid={}".format(uid)
        try:
            Mysql.cur.execute(sql)
            res = Mysql.cur.fetchone()
            if len(res) > 0:
                return res[0]
            else:
                return None
        except Exception as error:
            print(error)

    # 查询消费记录的支付方式
    @staticmethod
    def selectPayChangeSql(uid):
        sql = "select money from xs_pay_change_new where uid={} ORDER BY id DESC LIMIT 1".format(uid)
        try:
            Mysql.cur.execute(sql)
            res = Mysql.cur.fetchone()
            if len(res) > 0:
                return res[0]
        except Exception as error:
            print(error)