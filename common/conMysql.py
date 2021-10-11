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
        self.conn = pymysql.connect(host=self._dbUrl, port=self._dbPort, user=self._user, passwd=self._password,
                                    db=self._dbName, charset='utf8')
        self.cur = self.conn.cursor()
