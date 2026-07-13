# coding=utf-8
"""
SLP MySQL 数据库操作模块

提供 SLP 平台的数据库连接管理和常用业务操作方法。
使用单例模式管理数据库连接，支持自动重连。
"""
import ast
import logging
import time
from typing import Optional, Tuple, Dict, Any, List, Union

from common.mysql_base import MySQLConnection as MySQLConnectionBase

logger = logging.getLogger(__name__)


class MySQLConnection(MySQLConnectionBase):
    """SLP MySQL 连接管理器（ali 配置）"""
    _config_name = 'ali'


class conMysql:
    """MySQL 操作类"""

    # ========== 查询 SQL 映射 ==========
    SELECT_SIMPLE_MAP: Dict[str, str] = {
        'bean': "SELECT money_coupon FROM xs_user_money_extend WHERE uid=%s",
        'cash': "SELECT cash FROM xs_user_money_extend WHERE uid=%s",
        'sum_money': "SELECT money+money_b+money_cash_b+money_cash FROM xs_user_money WHERE uid=%s",
        'sum_commodity': "SELECT SUM(num) FROM xs_user_commodity WHERE uid=%s",
        'pay_room_money': "SELECT pay_room_money FROM xs_user_profile WHERE uid=%s",
        'popularity': "SELECT popularity FROM xs_user_popularity WHERE uid=%s",
        'user_index': "SELECT salt FROM xs_user_index WHERE uid=%s",
        'union': "SELECT rid FROM xs_chatroom WHERE property='union' LIMIT 1",
        'vip': "SELECT rid FROM xs_chatroom WHERE property='vip' LIMIT 1",
        'growth': "SELECT growth FROM xs_user_title_new WHERE uid=%s",
    }

    SELECT_WITH_PARAM_MAP: Dict[str, str] = {
        'single_money': "SELECT {money_type} FROM xs_user_money WHERE uid=%s",
        'num_commodity': "SELECT num FROM xs_user_commodity WHERE cid=%s AND uid=%s",
        'id_commodity': "SELECT id FROM xs_user_commodity WHERE cid=%s AND uid=%s",
        'level': "SELECT level FROM xs_user_title_new WHERE uid=%s",
    }

    SELECT_COMPLEX_SQL = (
        "SELECT id, name, money_value, break_money, upgrade_money "
        "FROM xs_relation_config WHERE id=%s"
    )

    SELECT_RELATION_ID_SQL = (
        "SELECT id FROM xs_relation_defend "
        "WHERE uid=%s AND defend_uid=%s AND relation_id=%s"
    )

    SELECT_PAY_CHANGE_SQL = (
        "SELECT reason FROM xs_pay_change WHERE uid=%s ORDER BY id DESC LIMIT 1"
    )

    # ============ 查询方法 ============
    
    @staticmethod
    def selectUserInfoSql(accountType: str, uid: str = "200000126", 
                         money_type: str = 'money_cash_b', 
                         cid: int = 263, 
                         payuid: str = "200000128") -> Optional[Union[int, float, Dict, List]]:
        """查询用户信息（映射字典模式）"""
        # 简单 SQL 直接查
        if accountType in conMysql.SELECT_SIMPLE_MAP:
            sql = conMysql.SELECT_SIMPLE_MAP[accountType]
            default = 0
            if accountType in ('union', 'vip'):
                res = MySQLConnection.execute_query_first(sql, default=None)
                if res is None:
                    raise EnvironmentError(f'库表无{"联盟房" if accountType == "union" else "个人房"}')
                return res
            return MySQLConnection.execute_query_first(sql, params=(uid,), default=default)

        # 需要额外参数的 SQL
        if accountType in conMysql.SELECT_WITH_PARAM_MAP:
            template = conMysql.SELECT_WITH_PARAM_MAP[accountType]
            if accountType == 'single_money':
                sql = template.format(money_type=money_type)
                params = (uid,)
            elif accountType in ('num_commodity', 'id_commodity'):
                sql = template
                params = (cid, uid)
            else:
                sql = template
                params = (uid,)
            return MySQLConnection.execute_query_first(sql, params=params, default=0 if accountType != 'level' else None)

        # relation_config 返回字典
        if accountType == 'relation_config':
            sql = conMysql.SELECT_COMPLEX_SQL
            cursor = MySQLConnection.get_cursor()
            try:
                cursor.execute(sql, (uid,))
                res = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                data_dict = [dict(zip(columns, row)) for row in res]
                return data_dict[0] if data_dict else None
            except Exception as error:
                logger.error('Select error: %s', error)
                return None

        # relation_id
        if accountType == 'relation_id':
            sql = conMysql.SELECT_RELATION_ID_SQL
            return MySQLConnection.execute_query_first(sql, params=(payuid, uid, cid), default=0)

        # pay_change 需要解析字典
        if accountType == 'pay_change':
            sql = conMysql.SELECT_PAY_CHANGE_SQL
            cursor = MySQLConnection.get_cursor()
            try:
                cursor.execute(sql, (uid,))
                res = cursor.fetchone()
                if res:
                    res_dict = ast.literal_eval(res[0])
                    return res_dict.get(str(money_type), 0)
                return 0
            except Exception as error:
                logger.error('Select error: %s', error)
                return 0

        logger.warning('Unknown accountType: %s', accountType)
        return None

    # ============ 删除方法 ============
    
    @staticmethod
    def deleteUserAccountSql(tableName: str, uid: str) -> None:
        """删除用户账户数据"""
        sql_map = {
            'user_commodity': ("DELETE FROM xs_user_commodity WHERE uid=%s", (uid,)),
            'user_title': ("DELETE FROM xs_user_title WHERE uid=%s LIMIT 5", (uid,)),
            'broker_user': ("DELETE FROM xs_broker_user WHERE uid=%s LIMIT 1", (uid,)),
            'chatroom': ("DELETE FROM xs_chatroom WHERE uid=%s LIMIT 1", (uid,)),
            'user_box': ("DELETE FROM xs_user_box WHERE uid=%s LIMIT 1", (uid,)),
            'pay_room_money': ("UPDATE xs_user_profile SET pay_room_money=0 WHERE uid=%s LIMIT 1", (uid,)),
            'user_title_new': ("UPDATE xs_user_title_new SET subscribe_time=0 WHERE uid=%s LIMIT 1", (uid,)),
        }
        item = sql_map.get(tableName)
        if item:
            sql, params = item
            MySQLConnection.execute_write(sql, params=params)
        else:
            logger.warning('Unknown tableName: %s', tableName)

    # ============ 更新方法 ============

    @staticmethod
    def updateUserRidInfoSql(property_rid: str, rid: int, area: str = 'en') -> None:
        """更新房间属性"""
        MySQLConnection.update_room_property(property_rid, rid, area)

    @staticmethod
    def updateUserBigArea(*uids: str, bigarea_id: int = 2) -> None:
        """更新用户大区"""
        MySQLConnection.update_user_bigarea(*uids, bigarea_id=bigarea_id)

    @staticmethod
    def updateUserLanguage(*uids: str, language: str = 'zh_CN', area_code: str = 'CN') -> None:
        """更新用户语言"""
        MySQLConnection.update_user_language(*uids, language=language, area_code=area_code)

    @staticmethod
    def updateUserMoneyClearSql(*uids: str) -> None:
        """清空用户账户余额"""
        MySQLConnection.clear_user_money(*uids)

    @staticmethod
    def updateMoneySql(uid: str, money: int = 0, money_cash: int = 0,
                       money_cash_b: int = 0, money_b: int = 0,
                       gold_coin: int = 0, money_debts: int = 0) -> None:
        """更新用户账户余额"""
        MySQLConnection.set_user_money(uid, money=money, money_cash=money_cash,
                                       money_cash_b=money_cash_b, money_b=money_b,
                                       gold_coin=gold_coin, money_debts=money_debts)

    @staticmethod
    def updateXsUserpopularity(uid: str) -> None:
        """更新用户人气数据"""
        MySQLConnection.reset_user_popularity(uid)

    @staticmethod
    def updateXsUserprofile_pay_room_money(uid: str) -> None:
        """更新用户 VIP 数据"""
        MySQLConnection.reset_user_pay_room_money(uid)

    # ============ 插入方法 ============

    @staticmethod
    def insertXsUserCommodity(uid: str, cid: int, num: int, state: int = 0) -> None:
        """用户背包增加数据"""
        MySQLConnection.insert_user_commodity(uid, cid, num, state)

    @staticmethod
    def insertXsUserBox(uid: str, gift_cid: int = 2505, box_type: str = 'copper') -> None:
        """更新箱子刷新物品"""
        MySQLConnection.insert_user_box(uid, gift_cid, box_type)

    # ============ 检查配置 ============

    @staticmethod
    def checkXsGiftConfig(gift_ids: Tuple[int, ...]) -> None:
        """检查礼物配置"""
        placeholders = ','.join(['%s'] * len(gift_ids))
        sql = f"UPDATE xs_gift SET deleted=0 WHERE id IN ({placeholders})"
        MySQLConnection.execute_write(sql, params=gift_ids)

    # ============ 专用查询方法 ============

    @staticmethod
    def select_greedy_prize(uid: str, round_id: int) -> Optional[Tuple]:
        """查询摩天轮开奖数据"""
        return MySQLConnection.query_greedy_prize(uid, round_id)

    @staticmethod
    def select_user_chatroom(property: str, bigarea_id: int = 1) -> int:
        """查询大区房间信息"""
        return MySQLConnection.query_user_chatroom(property, bigarea_id)

    @staticmethod
    def sqlXsUserpopularity(uid: str) -> int:
        """查询用户人气数据"""
        return MySQLConnection.query_user_popularity(uid)

    @staticmethod
    def sqlXsUserprofile_pay_room_money(uid: str) -> int:
        """查询用户 VIP 数据"""
        return MySQLConnection.query_user_pay_room_money(uid)

    # ============ SLP 测试依赖的兼容方法 ============

    @staticmethod
    def updateUserInfoSql(tableName: str, uid: str, level: int = 10) -> None:
        """更新用户信息（当前仅支持 user_title_new 爵位等级）"""
        if tableName != 'user_title_new':
            logger.warning('updateUserInfoSql 不支持 tableName: %s', tableName)
            return
        jw_config = {
            "0": 0, "10": 0, "20": 20000, "30": 80000,
            "40": 250000, "50": 1000000, "60": 2500000,
            "70": 6500000, "80": 15000000, "90": 50000000,
        }
        subscribe_time = int(time.time()) + 1 * 24 * 60 * 60
        growth = jw_config.get(str(level), 0)
        sql = ("UPDATE xs_user_title_new SET level=%s, growth=%s, "
               "effective_value=%s, subscribe_time=%s "
               "WHERE uid=%s")
        MySQLConnection.execute_write(sql, params=(level, growth, growth, subscribe_time, uid))

    @staticmethod
    def checkRidFactoryType(rid: int) -> Optional[str]:
        """查询房间的 room_factory_type"""
        sql = "SELECT room_factory_type FROM xs_chatroom WHERE rid=%s"
        return MySQLConnection.execute_query_first(sql, params=(rid,), default=None)

    @staticmethod
    def checkUserBroker(uid: str) -> bool:
        """校验是否是公会成员"""
        sql = "SELECT id FROM xs_broker_user WHERE uid=%s AND deleted=0 LIMIT 1"
        return MySQLConnection.execute_query_first(sql, params=(uid,), default=None) is not None

    @staticmethod
    def updateUserGodSql(uid: str, agreement_version: int) -> None:
        """更新用户 settings 的 agreement_version"""
        sql = "UPDATE xs_user_settings SET agreement_version=%s WHERE uid=%s"
        MySQLConnection.execute_write(sql, params=(agreement_version, uid))

    @staticmethod
    def selectZxPayData(uid: str) -> Optional[List[Dict[str, Any]]]:
        """查询 ZX 打赏流水聚合数据"""
        sql = (
            "SELECT JSON_EXTRACT(reason, '$.to') AS to_uid, "
            "JSON_EXTRACT(reason, '$.gid') AS gid, "
            "SUM(JSON_EXTRACT(reason, '$.num')) AS total_num "
            "FROM xs_pay_change WHERE uid = %s "
            "AND JSON_UNQUOTE(JSON_EXTRACT(reason, '$.obr')) IS NOT NULL "
            "GROUP BY gid, to_uid ORDER BY to_uid"
        )
        try:
            cursor = MySQLConnection.get_cursor(dict_cursor=True)
            cursor.execute(sql, (uid,))
            return cursor.fetchall()
        except Exception as error:
            logger.error('selectZxPayData error: %s', error)
            return None
