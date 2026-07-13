# coding=utf-8
"""
MySQL 连接管理基类

统一各数据库模块（conMysql/conPtMysql/conSlpMysql/conStarifyMysql）中重复的
连接管理逻辑，避免多份单例/重连/游标管理代码。
"""
import logging
from typing import Optional, Tuple, Any

import pymysql
from pymysql import cursors

from common.Config import config

logger = logging.getLogger(__name__)


class MySQLConnection:
    """MySQL 连接管理器（单例模式，支持自动重连）

    子类通过设置 ``_config_name`` 指定使用哪个数据库配置：
        - dev  -> config.database.dev_config
        - ali  -> config.database.ali_config
        - rds  -> config.database.rds_config
    """

    _config_name: str = 'dev'
    _connection: Optional[pymysql.Connection] = None
    _cursor: Optional[pymysql.cursors.Cursor] = None

    @classmethod
    def _get_db_config(cls) -> dict:
        """获取当前配置对应的数据库连接参数"""
        return getattr(config.database, f'{cls._config_name}_config')

    @classmethod
    def get_connection(cls) -> pymysql.Connection:
        """获取数据库连接（单例 + 自动重连）"""
        if cls._connection is None or not cls._connection.open:
            db = cls._get_db_config()
            cls._connection = pymysql.connect(**db, autocommit=False)
            cls._connection.select_db(db['database'])
        cls._connection.ping(reconnect=True)
        return cls._connection

    @classmethod
    def get_cursor(cls, dict_cursor: bool = False):
        """获取游标

        Args:
            dict_cursor: 是否返回字典游标
        """
        con = cls.get_connection()
        if dict_cursor:
            return con.cursor(cursor=cursors.DictCursor)
        if cls._cursor is None or not cls._connection.open:
            cls._cursor = con.cursor()
        return cls._cursor

    @classmethod
    def execute_query(cls, sql: str, params: Optional[Tuple] = None) -> Optional[Tuple]:
        """执行查询 SQL，返回单条记录

        Args:
            sql: SQL 语句，可使用 %s 占位符
            params: 查询参数元组

        Returns:
            查询结果（单条记录），失败返回 None
        """
        try:
            cursor = cls.get_cursor()
            cursor.execute(sql, params)
            return cursor.fetchone()
        except Exception as e:
            logger.error('Query error: %s', e)
            return None

    @classmethod
    def execute_write(cls, sql: str, params: Optional[Tuple] = None) -> bool:
        """执行写 SQL

        Args:
            sql: SQL 语句，可使用 %s 占位符
            params: SQL 参数元组

        Returns:
            执行成功返回 True，失败返回 False
        """
        con = cls.get_connection()
        try:
            cursor = cls.get_cursor()
            cursor.execute(sql, params)
            con.commit()
            return True
        except Exception as e:
            con.rollback()
            logger.error('Write error: %s', e)
            return False

    @classmethod
    def execute_query_first(cls, sql: str, params: Optional[Tuple] = None, default: Any = 0) -> Any:
        """执行查询并返回第一行第一列

        Args:
            sql: SQL 语句
            params: 查询参数元组
            default: 无结果时默认值
        """
        res = cls.execute_query(sql, params)
        return res[0] if res else default

    # ============ 公共业务操作 ============
    # 以下方法提取自 conPtMysql/conSlpMysql 中完全相同的实现，
    # 通过 classmethod + cls 自动路由到正确的子类连接。

    @classmethod
    def clear_user_money(cls, *uids) -> None:
        """清空用户账户余额（含 money_order 字段）"""
        sql = ("UPDATE xs_user_money SET money=0, money_b=0, money_cash=0, "
               "money_cash_b=0, gold_coin=0, money_debts=0, money_order=0, "
               "money_order_b=0 WHERE uid=%s")
        for uid in uids:
            cls.execute_write(sql, params=(uid,))

    @classmethod
    def set_user_money(cls, uid, money=0, money_cash=0, money_cash_b=0,
                       money_b=0, gold_coin=0, money_debts=0) -> None:
        """更新用户账户余额"""
        sql = ("UPDATE xs_user_money SET money=%s, money_b=%s, "
               "money_cash=%s, money_cash_b=%s, "
               "gold_coin=%s, money_debts=%s WHERE uid=%s LIMIT 1")
        cls.execute_write(sql, params=(money, money_b, money_cash, money_cash_b,
                                      gold_coin, money_debts, uid))

    @classmethod
    def reset_user_popularity(cls, uid) -> None:
        """重置用户人气值为 0"""
        cls.execute_write("UPDATE xs_user_popularity SET popularity=0 WHERE uid=%s",
                          params=(uid,))

    @classmethod
    def reset_user_pay_room_money(cls, uid) -> None:
        """重置用户 VIP 经验值为 0"""
        cls.execute_write("UPDATE xs_user_profile SET pay_room_money=0 WHERE uid=%s",
                          params=(uid,))

    @classmethod
    def insert_user_commodity(cls, uid, cid, num, state=0) -> None:
        """向用户背包插入物品"""
        sql = "INSERT INTO xs_user_commodity (uid, cid, num, state) VALUES(%s, %s, %s, %s)"
        cls.execute_write(sql, params=(uid, cid, num, state))

    @classmethod
    def insert_user_box(cls, uid, gift_cid=2505, box_type='copper') -> None:
        """向用户箱子插入刷新物品"""
        sql = ("INSERT INTO xs_user_box (last_refresh_cid, last_refresh_sub_cid, uid, type) "
               "VALUES(%s, %s, %s, %s)")
        cls.execute_write(sql, params=(gift_cid, gift_cid, uid, box_type))

    @classmethod
    def update_room_property(cls, property_rid, rid, area='en') -> None:
        """更新房间属性"""
        sql = "UPDATE xs_chatroom SET property=%s, area=%s WHERE rid=%s"
        cls.execute_write(sql, params=(property_rid, area, rid))

    @classmethod
    def update_user_bigarea(cls, *uids, bigarea_id=2) -> None:
        """更新用户大区"""
        placeholders = ','.join(['%s'] * len(uids))
        sql = f"UPDATE xs_user_bigarea SET bigarea_id=%s WHERE uid IN ({placeholders})"
        cls.execute_write(sql, params=(bigarea_id,) + uids)

    @classmethod
    def update_user_language(cls, *uids, language='zh_CN', area_code='CN') -> None:
        """更新用户语言"""
        placeholders = ','.join(['%s'] * len(uids))
        sql = f"UPDATE xs_user_settings SET language=%s, area_code=%s WHERE uid IN ({placeholders})"
        cls.execute_write(sql, params=(language, area_code) + uids)

    @classmethod
    def query_user_popularity(cls, uid) -> int:
        """查询用户人气值"""
        return cls.execute_query_first(
            "SELECT popularity FROM xs_user_popularity WHERE uid=%s",
            params=(uid,), default=0
        )

    @classmethod
    def query_user_pay_room_money(cls, uid) -> int:
        """查询用户 VIP 经验值"""
        return cls.execute_query_first(
            "SELECT pay_room_money FROM xs_user_profile WHERE uid=%s",
            params=(uid,), default=0
        )

    @classmethod
    def query_user_chatroom(cls, property_name, bigarea_id=1) -> int:
        """查询大区房间信息"""
        sql = ("SELECT rid FROM xs_chatroom a "
               "LEFT JOIN xs_user_bigarea b ON a.uid=b.uid "
               "WHERE a.property=%s AND b.bigarea_id=%s LIMIT 1")
        return cls.execute_query_first(sql, params=(property_name, bigarea_id), default=0)

    @classmethod
    def query_greedy_prize(cls, uid, round_id):
        """查询摩天轮开奖数据"""
        sql = "SELECT counter, prize FROM xs_greedy_round_player_v2 WHERE uid=%s AND round_id=%s"
        return cls.execute_query(sql, params=(uid, round_id))
