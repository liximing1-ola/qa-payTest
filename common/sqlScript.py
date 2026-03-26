# coding=utf-8
import pymysql
from contextlib import contextmanager


class MySQLConfig:
    """MySQL配置"""
    DEV = {
        'host': '192.168.11.46',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'database': 'xianshi',
        'charset': 'utf8'
    }
    ALI = {
        'host': 'rm-bp1nfl3dp096d5o39.mysql.rds.aliyuncs.com',
        'port': 3306,
        'user': 'super',
        'password': 'dev123456',
        'database': 'xianshi',
        'charset': 'utf8'
    }


class MySQLClient:
    """MySQL客户端"""
    _config = MySQLConfig.DEV

    @classmethod
    def set_config(cls, config_name='dev'):
        """切换配置"""
        cls._config = getattr(MySQLConfig, config_name.upper(), MySQLConfig.DEV)

    @classmethod
    @contextmanager
    def get_connection(cls):
        """获取数据库连接（上下文管理器）"""
        con = pymysql.connect(**cls._config)
        try:
            yield con
        finally:
            con.close()

    @classmethod
    @contextmanager
    def get_cursor(cls):
        """获取游标（上下文管理器）"""
        with cls.get_connection() as con:
            cursor = con.cursor()
            try:
                yield con, cursor
            finally:
                cursor.close()

    @classmethod
    def execute(cls, sql, fetch_one=False, fetch_all=False):
        """执行SQL语句"""
        with cls.get_cursor() as (con, cur):
            try:
                cur.execute(sql)
                if fetch_one:
                    return cur.fetchone()
                if fetch_all:
                    return cur.fetchall()
                con.commit()
            except Exception as e:
                con.rollback()
                raise e

    @classmethod
    def execute_write(cls, sql, error_msg='execute fail'):
        """执行写操作"""
        try:
            cls.execute(sql)
        except Exception as e:
            print(error_msg, e)

    @classmethod
    def execute_read(cls, sql, default=None):
        """执行读操作"""
        try:
            res = cls.execute(sql, fetch_one=True)
            return res[0] if res else default
        except Exception as e:
            print(e)
            return default


# 内部引用
mysql = MySQLClient


class UserMoneyOperations:
    """用户资金相关操作"""

    @staticmethod
    def update(uid, money=0, money_cash=0, money_cash_b=0, money_b=0, gold_coin=0):
        """更新用户账户余额"""
        sql = f"UPDATE xs_user_money SET money={money}, money_b={money_b}, money_cash={money_cash}, money_cash_b={money_cash_b}, gold_coin={gold_coin} WHERE uid={uid} LIMIT 1"
        mysql.execute_write(sql, 'update fail')

    @staticmethod
    def select_all(uid):
        """查询用户所有账户余额之和"""
        sql = f"SELECT money+money_b+money_cash_b+money_cash FROM xs_user_money WHERE uid={uid}"
        return mysql.execute_read(sql)


class UserCommodityOperations:
    """用户背包相关操作"""

    @staticmethod
    def delete_all(uid):
        """清空用户背包"""
        sql = f"DELETE FROM xs_user_commodity WHERE uid={uid}"
        mysql.execute_write(sql, 'delete fail')

    @staticmethod
    def check(uid, cid):
        """检查指定物品数量"""
        sql = f"SELECT num FROM xs_user_commodity WHERE cid={cid} AND uid={uid}"
        return mysql.execute_read(sql, 0)

    @staticmethod
    def check_all(uid):
        """检查所有物品数量"""
        sql = f"SELECT SUM(num) FROM xs_user_commodity WHERE uid={uid}"
        result = mysql.execute_read(sql, 0)
        return int(result) if result else 0

    @staticmethod
    def get_id(cid, uid):
        """获取物品表ID"""
        sql = f"SELECT id FROM xs_user_commodity WHERE cid={cid} AND uid={uid}"
        return mysql.execute_read(sql)

    @staticmethod
    def insert(uid, cid, num, state=0):
        """插入物品"""
        sql = f"INSERT INTO xs_user_commodity (uid, cid, num, state) VALUES ({uid}, {cid}, {num}, {state})"
        mysql.execute_write(sql, 'insert fail')


class UserProfileOperations:
    """用户资料相关操作"""

    @staticmethod
    def get_uids(limit_num, min_uid=131542080, app_id=1):
        """生成一批UID"""
        sql = f"SELECT uid FROM xs_user_profile WHERE uid>{min_uid} AND app_id={app_id} LIMIT {limit_num}"
        try:
            results = mysql.execute(sql, fetch_all=True)
            uids = tuple(str(i[0]) for i in results) if results else ()
            print(uids)
            return uids
        except Exception as e:
            print('fail', e)
            return ()
