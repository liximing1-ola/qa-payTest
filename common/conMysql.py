# coding=utf-8
import pymysql
import time
class conMysql:
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
    con.ping(reconnect=True)  # 断开重连
    cur = con.cursor()

    # 更新用户账户余额
    @staticmethod
    def updateMoneySql(uid, money=0, money_cash=0, money_cash_b=0, money_b=0, gold_coin=0):
        sql = "update xs_user_money set money={}, money_b={}, money_cash={}, money_cash_b={},gold_coin={} where uid={} limit 1"\
            .format(money, money_b, money_cash, money_cash_b, gold_coin, uid)
        try:
            conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('update fail： {}'.format(error))

    # 查询用户所有账户余额总和
    @staticmethod
    def selectAllMoneySql(uid):
        sql = "select (money+money_b+money_cash_b+money_cash) from xs_user_money where uid={}".format(uid)
        try:
            conMysql.cur.execute(sql)
            res = conMysql.cur.fetchone()
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
            conMysql.cur.execute(sql)
            res = conMysql.cur.fetchone()
            if len(res) > 0:
                return res[0]
        except Exception as error:
            print(error)

    # 删除用户工会记录
    @staticmethod
    def deleteXsBrokerUser(uid):
        sql = "delete from xs_broker_user where uid ={} limit 1".format(uid)
        try:
            conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('delete fail', error)

    # 删除用户商业房
    @staticmethod
    def deleteXsChatroom(uid):
        sql = "delete from xs_chatroom where uid ={} limit 1".format(uid)
        try:
            conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('delete fail', error)

    # 查询用户某个账户余额
    @staticmethod
    def selectMoneySql(uid, money_type='money_cash_b'):
        sql = "select {} from xs_user_money where uid={}".format(money_type, uid)
        try:
            conMysql.cur.execute(sql)
            res = conMysql.cur.fetchone()
            if len(res) > 0:
                return res[0]
            else:
                return None
        except Exception as error:
            print(error)

    # 删除用户金豆账户数据
    @staticmethod
    def deleteUserBeanSql(*uids):
        try:
            for uid in uids:
                sql = "delete from xs_user_money_extend where uid = {} limit 1".format(uid)
                time.sleep(0.01)
                conMysql.cur.execute(sql)
                conMysql.con.commit()
        except Exception as error:
            conMysql.con.rollback()
            print('delete fail', error)