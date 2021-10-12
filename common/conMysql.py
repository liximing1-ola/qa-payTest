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

    def __init__(self):
        self.con = pymysql.connect(host=self._dbUrl, port=self._dbPort, user=self._user, passwd=self._password,
                                    db=self._dbName, charset='utf8')
        self.cur = self.con.cursor()

    # 更新用户账户余额
    def updateMoneySql(self, uid, money=0, money_cash=0, money_cash_b=0, money_b=0, gold_coin=0):
        sql = "update xs_user_money set money={}, money_b={}, money_cash={}, money_cash_b={},gold_coin={} where uid={} limit 1"\
            .format(money, money_b, money_cash, money_cash_b, gold_coin, uid)
        try:
            self.cur.execute(sql)
        except Exception as error:
            self.con.rollback()
            print('update fail', error)
        finally:
            self.con.commit()