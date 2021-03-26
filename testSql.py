# coding=utf-8
import pymysql
# 本地服务器数据库测试用
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


if __name__ == '__main__':
    pass
