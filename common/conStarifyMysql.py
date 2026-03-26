# coding=utf-8
"""
Starify MySQL数据库操作模块
"""
import time
import pymysql
from contextlib import contextmanager


# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'xianshi',
    'charset': 'utf8',
    'autocommit': True
}


class MySQLConnection:
    """MySQL连接管理器"""

    _instance = None
    _connection = None
    _cursor = None

    @classmethod
    def get_connection(cls):
        """获取数据库连接（单例模式）"""
        if cls._connection is None or not cls._connection.open:
            cls._connection = pymysql.connect(**DB_CONFIG)
            cls._connection.select_db(DB_CONFIG['database'])
        cls._connection.ping(reconnect=True)
        return cls._connection

    @classmethod
    def get_cursor(cls):
        """获取游标"""
        if cls._cursor is None or not cls._connection.open:
            cls._connection = cls.get_connection()
            cls._cursor = cls._connection.cursor()
        return cls._cursor

    @classmethod
    def execute_query(cls, sql):
        """执行查询SQL"""
        try:
            cursor = cls.get_cursor()
            cursor.execute(sql)
            result = cursor.fetchone()
            return result[0] if result and result[0] is not None else 0
        except Exception as e:
            print(f"Query error: {e}")
            return 0

    @classmethod
    def execute_write(cls, sql):
        """执行写SQL"""
        try:
            cursor = cls.get_cursor()
            cursor.execute(sql)
            return True
        except Exception as e:
            cls._connection.rollback()
            print(f"Write error: {e}")
            return False
        finally:
            cls._connection.commit()


class conMysql:
    """MySQL操作类"""

    # ============ 通用方法 ============
    @staticmethod
    def sql_fetchone(sql):
        """执行查询并返回第一行第一列"""
        return MySQLConnection.execute_query(sql)

    @staticmethod
    def sql_execute(sql):
        """执行SQL语句"""
        return MySQLConnection.execute_write(sql)

    # ============ 查询方法 ============
    @staticmethod
    def selectUserInfoSql(accountType, uid, cid=0, duration_time=86400):
        """查询用户信息"""
        sql_map = {
            'star_coin': f"SELECT star_coin FROM xs_user_money WHERE uid={uid}",
            'gift_num': f"SELECT SUM(num) FROM xs_user_commodity WHERE uid={uid} AND cid={cid}",
            'commodity_num': f"SELECT SUM(num) FROM xs_user_commodity WHERE uid={uid} AND cid={cid} AND duration_time={duration_time}",
            'wealth': f"SELECT wealth FROM xs_user_wealth WHERE uid={uid}",
            'charm': f"SELECT charm FROM xs_user_charm WHERE uid={uid}",
        }
        sql = sql_map.get(accountType)
        return conMysql.sql_fetchone(sql) if sql else 0

    # ============ 更新方法 ============
    @staticmethod
    def updateMoneySql(uid, money):
        """更新用户账户余额"""
        sql = f"UPDATE xs_user_money SET star_coin={money} WHERE uid={uid}"
        conMysql.sql_execute(sql)

    @staticmethod
    def updateWealthSql(uid, wealth, pre_wealth=0):
        """更新用户财富值"""
        sql = f"UPDATE xs_user_wealth SET wealth={wealth}, pre_wealth={pre_wealth} WHERE uid={uid}"
        conMysql.sql_execute(sql)

    @staticmethod
    def updateCharmSql(uid, charm):
        """更新用户魅力值"""
        sql = f"UPDATE xs_user_charm SET charm={charm} WHERE uid={uid}"
        conMysql.sql_execute(sql)

    # ============ 删除方法 ============
    @staticmethod
    def deleteUserAccountSql(tableName, uid, wid=0):
        """删除用户数据"""
        sql_map = {
            'user_commodity': f"DELETE FROM xs_user_commodity WHERE uid={uid}",
            'user_work_reward': f"DELETE FROM xs_user_work_reward WHERE uid={uid} AND wid={wid}",
        }
        sql = sql_map.get(tableName)
        if sql:
            conMysql.sql_execute(sql)

    # ============ 插入方法 ============
    @staticmethod
    def insertXsUserCommodity(uid, cid, num, period_end=None):
        """向用户背包发礼物"""
        if period_end is None:
            period_end = int(time.time() + 3600)
        sql = f"INSERT INTO xs_user_commodity (uid, cid, num, period_end) VALUES({uid}, {cid}, {num}, {period_end})"
        conMysql.sql_execute(sql)

    # ============ 歌手相关 ============
    @staticmethod
    def deleteProducerSinger(singer_uid):
        """清除制作人/歌手关系"""
        sql_list = [
            f"UPDATE xs_audition_singer SET producer_uid=0 WHERE uid={singer_uid}",
            f"DELETE FROM xs_audition_relation WHERE singer_uid={singer_uid}"
        ]
        for sql in sql_list:
            conMysql.sql_execute(sql)

    @staticmethod
    def selectProducerSinger(producer_uid):
        """查询已签约歌手人数"""
        sql_list = [
            f"SELECT COUNT(1) FROM xs_audition_relation WHERE producer_uid={producer_uid}",
            f"SELECT COUNT(1) FROM xs_audition_purchasing WHERE status=0 AND uid={producer_uid}"
        ]
        return sum(conMysql.sql_fetchone(sql) for sql in sql_list)

    @staticmethod
    def updateSingerWorth(singer_uid, worth=100):
        """修改歌手身价"""
        sql = f"UPDATE xs_audition_singer SET worth={worth} WHERE uid={singer_uid}"
        conMysql.sql_execute(sql)


if __name__ == '__main__':
    print(conMysql.selectUserInfoSql('gift_num', 124458))
