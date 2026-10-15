"""
APP MySQL 数据库操作模块

提供统一的数据库连接管理和常用业务操作方法。
使用单例模式管理数据库连接，支持自动重连。
"""
import logging

from common.Config import config
from common.mysql_base import MySQLConnection as MySQLConnectionBase

logger = logging.getLogger(__name__)


class MySQLConnection(MySQLConnectionBase):
    """APP MySQL 连接管理器（dev 配置）"""
    _config_name = 'dev'
    _connection = None
    _cursor = None


class ConMysql:
    """MySQL 操作类"""

    # SQL 映射字典
    QUERY_SQL_MAP: dict[str, str] = {
        'sum_money': "SELECT money+money_b+money_cash_b+money_cash FROM xs_user_money WHERE uid=%s",
        'sum_commodity': "SELECT SUM(num) FROM xs_user_commodity WHERE uid=%s",
        'sum_commodity_32': "SELECT SUM(num) FROM xs_user_commodity WHERE uid=%s AND cid=32",
        'money_cash_personal': "SELECT money_cash_personal FROM xs_user_money_extend WHERE uid=%s",
        'chat-pay-card': "SELECT num FROM xs_user_commodity WHERE uid=%s AND cid=42598",
        'pay_change': "SELECT money FROM xs_pay_change_new WHERE uid=%s ORDER BY id DESC LIMIT 1",
    }

    _MONEY_COLUMNS = MySQLConnection._MONEY_COLUMNS

    DELETE_SQL_MAP: dict[str, str] = {
        'user_commodity': "DELETE FROM xs_user_commodity WHERE uid=%s",
        'user_box': "DELETE FROM xs_user_box WHERE uid=%s",
        'user_journey_planet_draw_record': "DELETE FROM xs_user_journey_planet_draw_record WHERE uid=%s",
        'user_journey_planet_record': "DELETE FROM xs_user_journey_planet_record WHERE uid=%s",
        'chat_pay_card_record': "DELETE FROM xs_chat_pay_card_record WHERE uid=%s",
    }

    # ============ 查询方法 ============

    @staticmethod
    def select_user_info_sql(accountType: str, uid: int | None = None, money_type: str = 'money_cash_b') -> int | None:
        """查询用户信息

        Args:
            accountType: 账户类型
            uid: 用户 ID，默认为 config.oversea_payUid
            money_type: 货币类型

        Returns:
            查询结果，失败返回 0 或 None
        """
        if uid is None:
            uid = config.oversea_payUid

        if accountType in ConMysql.QUERY_SQL_MAP:
            sql = ConMysql.QUERY_SQL_MAP[accountType]
            res = MySQLConnection.execute_query(sql, params=(uid,))
            return int(res[0]) if res and res[0] else 0

        if accountType == 'single_money':
            if money_type not in ConMysql._MONEY_COLUMNS:
                raise ValueError(f'Invalid money_type column: {money_type}')
            sql = f"SELECT {money_type} FROM xs_user_money WHERE uid=%s"
            res = MySQLConnection.execute_query(sql, params=(uid,))
            return res[0] if res else None

        logger.warning('Unknown accountType: %s', accountType)
        return None

    # ============ 删除方法 ============

    @staticmethod
    def delete_user_account_sql(tableName: str, uid: int) -> None:
        """删除用户数据

        Args:
            tableName: 表名
            uid: 用户 ID
        """
        if tableName in ConMysql.DELETE_SQL_MAP:
            sql = ConMysql.DELETE_SQL_MAP[tableName]
            MySQLConnection.execute_write(sql, params=(uid,))
        else:
            logger.warning('Unknown tableName: %s', tableName)

    # ============ 更新方法 ============

    @staticmethod
    def update_user_rid_info_sql(property_rid: str, rid: int, area: str = 'en') -> None:
        """更新房间属性"""
        MySQLConnection.update_room_property(property_rid, rid, area)

    @staticmethod
    def update_user_big_area(*uids: int, bigarea_id: int = 2) -> None:
        """更新用户大区"""
        MySQLConnection.update_user_bigarea(*uids, bigarea_id=bigarea_id)

    @staticmethod
    def update_user_language(*uids: int, language: str = 'zh_CN', area_code: str = 'CN') -> None:
        """更新用户语言"""
        MySQLConnection.update_user_language(*uids, language=language, area_code=area_code)

    updateUserLanguage = staticmethod(update_user_language)  # 兼容别名

    @staticmethod
    def update_user_money_clear_sql(*uids: int) -> None:
        """清空用户账户余额"""
        MySQLConnection.clear_user_money(*uids)

    @staticmethod
    def update_user_extend_money_clear_sql(*uids: int) -> None:
        """清空用户扩展账户余额"""
        sql = "UPDATE xs_user_money_extend SET money_cash_personal=0 WHERE uid=%s"
        for uid in uids:
            MySQLConnection.execute_write(sql, params=(uid,))

    @staticmethod
    def update_money_sql(uid: int, money: int = 0, money_cash: int = 0,
                       money_cash_b: int = 0, money_b: int = 0,
                       gold_coin: int = 0, money_debts: int = 0) -> None:
        """更新用户账户余额"""
        MySQLConnection.set_user_money(uid, money=money, money_cash=money_cash,
                                       money_cash_b=money_cash_b, money_b=money_b,
                                       gold_coin=gold_coin, money_debts=money_debts)

    @staticmethod
    def update_xs_user_popularity(uid: int) -> None:
        """更新用户人气数据"""
        MySQLConnection.reset_user_popularity(uid)

    @staticmethod
    def update_xs_user_profile_pay_room_money(uid: int) -> None:
        """更新用户 VIP 数据"""
        MySQLConnection.reset_user_pay_room_money(uid)

    # ============ 插入方法 ============

    @staticmethod
    def insert_xs_user_commodity(uid: int, cid: int, num: int, state: int = 0) -> None:
        """用户背包增加数据"""
        MySQLConnection.insert_user_commodity(uid, cid, num, state)

    @staticmethod
    def insert_xs_user_box(uid: int, gift_cid: int = 2505, box_type: str = 'copper') -> None:
        """更新箱子刷新物品"""
        MySQLConnection.insert_user_box(uid, gift_cid, box_type)

    # ============ 检查配置 ============

    @staticmethod
    def check_xs_gift_config() -> None:
        """检查礼物配置"""
        gift_ids = tuple(config.oversea_giftId.values())
        MySQLConnection._update_xs_gift_status(gift_ids)

    # ============ 查询方法 ============

    @staticmethod
    def select_greedy_prize(uid: int, round_id: int) -> tuple:
        """查询摩天轮开奖数据"""
        return MySQLConnection.query_greedy_prize(uid, round_id) or (0, 0)

    @staticmethod
    def select_user_chatroom(property: str, bigarea_id: int = 1) -> int:
        """查询大区房间信息"""
        return MySQLConnection.query_user_chatroom(property, bigarea_id)

    @staticmethod
    def sql_xs_user_popularity(uid: int) -> int:
        """查询用户人气数据"""
        return MySQLConnection.query_user_popularity(uid)

    @staticmethod
    def sql_xs_user_profile_pay_room_money(uid: int) -> int:
        """查询用户 VIP 数据"""
        return MySQLConnection.query_user_pay_room_money(uid)


# 兼容别名（驼峰 → PascalCase，后续逐步迁移外部调用后可移除）
conMysql = ConMysql
