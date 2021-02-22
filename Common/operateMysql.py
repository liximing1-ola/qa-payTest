import pymysql

class MysqlUtil:
    # 私有属性,类外部无法直接进行访问
    _dbUrl = 'rm-bp1nfl3dp096d5o39.mysql.rds.aliyuncs.com'
    _dbPort = 3306
    _user = 'super'
    _password = 'dev123456'
    _dbName ='xianshi'

    conn = ''
    cur = ''

    def __init__(self):
        print('------ 数据库连接--------')
        # 创建游标对象
        self.cur = self.conn.cursor()

    def xss_init(self):
        print('------ 数据库连接--------')
        self.conn = pymysql.connect(host=self._dbUrl, port=self._dbPort, user=self._user, passwd=self._password,
                                    db=self._dbName, charset='utf8')
        # 创建游标对象
        self.cur = self.conn.cursor()

    def update(self, sql_update):
        try:
            rows = self.cur.execute(sql_update)
            self.conn.commit()
            return rows
        except Exception as e:
            self.conn.rollback()
            print(e)

    def update_more(self, sql_list):
        try:
            for sql in sql_list:
                self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(e)

    def search_one(self, sql_search):
        try:
            row_count = self.cur.execute(sql_search)
            if row_count > 0:
                results = self.cur.fetchone()
                return results
            else:
                return None
        except Exception as e:
            print(e)

    def search_all(self, sql_search):
        try:
            row_count = self.cur.execute(sql_search)
            if row_count > 0:
                results = self.cur.fetchall()
                return results
            else:
                return None
        except Exception as e:
            print(e)

    def close_con(self):
        try:
            self.conn.close()
        except Exception as e:
            print(e)


