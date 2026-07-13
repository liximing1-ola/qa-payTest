# coding=utf-8
"""
MySQL 数据库脚本工具模块

提供统一的数据库连接管理、SQL 执行和常用业务操作。
支持多环境配置（DEV/ALI），使用上下文管理器确保资源正确释放。
"""
import logging
import pymysql
from typing import Optional, Any, Tuple, Dict
from contextlib import contextmanager
from common.Config import config

logger = logging.getLogger(__name__)


class MySQLClient:
    """MySQL 客户端"""
    _config_name: str = 'dev'

    @classmethod
    def set_config(cls, config_name: str = 'dev') -> None:
        """切换配置
        
        Args:
            config_name: 配置名称（dev/ali/rds）
        """
        cls._config_name = config_name

    @classmethod
    def _get_config(cls) -> Dict[str, Any]:
        """获取当前数据库配置"""
        configs = {
            'dev': config.database.dev_config,
            'ali': config.database.ali_config,
            'rds': config.database.rds_config,
        }
        return configs.get(cls._config_name, config.database.dev_config)

    @classmethod
    @contextmanager
    def get_connection(cls):
        """获取数据库连接（上下文管理器）"""
        con = pymysql.connect(**cls._get_config())
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
    def execute(cls, sql: str, params: Optional[tuple] = None,
                fetch_one: bool = False, fetch_all: bool = False):
        """执行 SQL 语句

        Args:
            sql: SQL 语句，支持 %s 占位符
            params: SQL 参数元组
            fetch_one: 是否返回单条结果
            fetch_all: 是否返回所有结果

        Returns:
            查询结果或 None

        Raises:
            Exception: 执行失败时抛出异常
        """
        with cls.get_cursor() as (con, cur):
            try:
                cur.execute(sql, params)
                if fetch_one:
                    return cur.fetchone()
                if fetch_all:
                    return cur.fetchall()
                con.commit()
            except Exception as e:
                con.rollback()
                raise e

    @classmethod
    def execute_write(cls, sql: str, params: Optional[tuple] = None,
                      error_msg: str = 'execute fail') -> None:
        """执行写操作

        Args:
            sql: SQL 语句，支持 %s 占位符
            params: SQL 参数元组
            error_msg: 错误提示信息
        """
        try:
            cls.execute(sql, params)
        except Exception as e:
            logger.error('%s: %s', error_msg, e)

    @classmethod
    def execute_read(cls, sql: str, params: Optional[tuple] = None,
                     default: Any = None) -> Any:
        """执行读操作

        Args:
            sql: SQL 语句，支持 %s 占位符
            params: SQL 参数元组
            default: 默认返回值

        Returns:
            查询结果的第一列值，或默认值
        """
        try:
            res = cls.execute(sql, params, fetch_one=True)
            return res[0] if res else default
        except Exception as e:
            logger.error('execute_read error: %s', e)
            return default


# 内部引用
mysql = MySQLClient


class UserMoneyOperations:
    """用户资金相关操作"""

    @staticmethod
    def update(uid: int, money: int = 0, money_cash: int = 0,
               money_cash_b: int = 0, money_b: int = 0, gold_coin: int = 0) -> None:
        """更新用户账户余额

        Args:
            uid: 用户 ID
            money: 金豆
            money_cash: 现金
            money_cash_b: 现金 B
            money_b: 金豆 B
            gold_coin: 金币
        """
        sql = ("UPDATE xs_user_money SET money=%s, money_b=%s, "
               "money_cash=%s, money_cash_b=%s, "
               "gold_coin=%s WHERE uid=%s LIMIT 1")
        mysql.execute_write(sql, params=(money, money_b, money_cash, money_cash_b, gold_coin, uid),
                            error_msg='update fail')

    @staticmethod
    def select_all(uid: int) -> Optional[int]:
        """查询用户所有账户余额之和

        Args:
            uid: 用户 ID

        Returns:
            余额总和
        """
        sql = "SELECT money+money_b+money_cash_b+money_cash FROM xs_user_money WHERE uid=%s"
        return mysql.execute_read(sql, params=(uid,))


class UserCommodityOperations:
    """用户背包相关操作"""

    @staticmethod
    def delete_all(uid: int) -> None:
        """清空用户背包

        Args:
            uid: 用户 ID
        """
        sql = "DELETE FROM xs_user_commodity WHERE uid=%s"
        mysql.execute_write(sql, params=(uid,), error_msg='delete fail')

    @staticmethod
    def check(uid: int, cid: int) -> int:
        """检查指定物品数量

        Args:
            uid: 用户 ID
            cid: 物品 ID

        Returns:
            物品数量
        """
        sql = "SELECT num FROM xs_user_commodity WHERE cid=%s AND uid=%s"
        return mysql.execute_read(sql, params=(cid, uid), default=0)

    @staticmethod
    def check_all(uid: int) -> int:
        """检查所有物品数量

        Args:
            uid: 用户 ID

        Returns:
            物品总数
        """
        sql = "SELECT SUM(num) FROM xs_user_commodity WHERE uid=%s"
        result = mysql.execute_read(sql, params=(uid,), default=0)
        return int(result) if result else 0

    @staticmethod
    def get_id(uid: int, cid: int) -> Optional[int]:
        """获取物品表 ID

        Args:
            uid: 用户 ID
            cid: 物品 ID

        Returns:
            记录 ID
        """
        sql = "SELECT id FROM xs_user_commodity WHERE cid=%s AND uid=%s"
        return mysql.execute_read(sql, params=(cid, uid))

    @staticmethod
    def insert(uid: int, cid: int, num: int, state: int = 0) -> None:
        """插入物品

        Args:
            uid: 用户 ID
            cid: 物品 ID
            num: 数量
            state: 状态
        """
        sql = "INSERT INTO xs_user_commodity (uid, cid, num, state) VALUES (%s, %s, %s, %s)"
        mysql.execute_write(sql, params=(uid, cid, num, state), error_msg='insert fail')


class UserProfileOperations:
    """用户资料相关操作"""

    @staticmethod
    def get_uids(limit_num: int, min_uid: int = 131542080, app_id: int = 1) -> Tuple[str, ...]:
        """生成一批 UID

        Args:
            limit_num: 限制数量
            min_uid: 最小 UID
            app_id: 应用 ID

        Returns:
            UID 元组
        """
        # LIMIT 值不能参数化，但 uid/app_id 来自内部调用
        sql = "SELECT uid FROM xs_user_profile WHERE uid>%s AND app_id=%s LIMIT %s"
        try:
            results = mysql.execute(sql, params=(min_uid, app_id, limit_num), fetch_all=True)
            uids = tuple(str(i[0]) for i in results) if results else ()
            logger.info('Generated UIDs: %s', uids)
            return uids
        except Exception as e:
            logger.error('get_uids fail: %s', e)
            return ()
