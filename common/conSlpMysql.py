# coding=utf-8
"""
SLP MySQL 数据库操作模块

提供 SLP 平台的数据库连接管理和常用业务操作方法。
使用单例模式管理数据库连接，支持自动重连。
"""
import ast
import time
from typing import Optional, Tuple, Dict, Any, List, Union
import pymysql


class DatabaseConfig:
    """数据库配置"""
    ALI: Dict[str, str] = {
        'host': '127.0.0.1',
        'port': '3306',
        'user': 'root',
        'password': 'root',
        'database': 'xianshi',
        'charset': 'utf8'
    }


class MySQLConnection:
    """MySQL连接管理器（单例模式）"""
    
    _connection: Optional[pymysql.Connection] = None
    _cursor: Optional[pymysql.cursors.Cursor] = None
    
    @classmethod
    def get_connection(cls) -> pymysql.Connection:
        """获取数据库连接"""
        if cls._connection is None or not cls._connection.open:
            config = DatabaseConfig.ALI
            cls._connection = pymysql.connect(
                host=config['host'],
                port=int(config['port']),
                user=config['user'],
                password=config['password'],
                charset=config['charset'],
                autocommit=True
            )
            cls._connection.select_db(config['database'])
        cls._connection.ping(reconnect=True)
        return cls._connection
    
    @classmethod
    def get_cursor(cls):
        """获取游标"""
        con = cls.get_connection()
        return cls._cursor if cls._cursor else con.cursor()


class conMysql:
    """MySQL 操作类"""

    # ========== 查询 SQL 映射 ==========
    SELECT_SIMPLE_MAP: Dict[str, str] = {
        'bean': "SELECT money_coupon FROM xs_user_money_extend WHERE uid={uid}",
        'cash': "SELECT cash FROM xs_user_money_extend WHERE uid={uid}",
        'sum_money': "SELECT money+money_b+money_cash_b+money_cash FROM xs_user_money WHERE uid={uid}",
        'sum_commodity': "SELECT SUM(num) FROM xs_user_commodity WHERE uid={uid}",
        'pay_room_money': "SELECT pay_room_money FROM xs_user_profile WHERE uid={uid}",
        'popularity': "SELECT popularity FROM xs_user_popularity WHERE uid={uid}",
        'user_index': "SELECT salt FROM xs_user_index WHERE uid={uid}",
        'union': "SELECT rid FROM xs_chatroom WHERE property='union' LIMIT 1",
        'vip': "SELECT rid FROM xs_chatroom WHERE property='vip' LIMIT 1",
        'growth': "SELECT growth FROM xs_user_title_new WHERE uid={uid}",
    }

    SELECT_WITH_PARAM_MAP: Dict[str, str] = {
        'single_money': "SELECT {money_type} FROM xs_user_money WHERE uid={uid}",
        'num_commodity': "SELECT num FROM xs_user_commodity WHERE cid={cid} AND uid={uid}",
        'id_commodity': "SELECT id FROM xs_user_commodity WHERE cid={cid} AND uid={uid}",
        'level': "SELECT level FROM xs_user_title_new WHERE uid={uid}",
    }

    SELECT_COMPLEX_SQL = (
        "SELECT id, name, money_value, break_money, upgrade_money "
        "FROM xs_relation_config WHERE id={uid}"
    )

    SELECT_RELATION_ID_SQL = (
        "SELECT id FROM xs_relation_defend "
        "WHERE uid={payuid} AND defend_uid={uid} AND relation_id={cid}"
    )

    SELECT_PAY_CHANGE_SQL = (
        "SELECT reason FROM xs_pay_change WHERE uid={uid} ORDER BY id DESC LIMIT 1"
    )

    @staticmethod
    def _query_one(sql: str, default=0):
        """执行查询，返回单个值"""
        cursor = MySQLConnection.get_cursor()
        try:
            cursor.execute(sql)
            res = cursor.fetchone()
            return res[0] if res else default
        except Exception as error:
            print(f'Select error: {error}')
            return default

    @staticmethod
    def _execute_sql(sql: str, op_name: str = 'execute'):
        """执行 SQL 语句（写操作）"""
        cursor = MySQLConnection.get_cursor()
        con = MySQLConnection.get_connection()
        try:
            cursor.execute(sql)
        except Exception as error:
            con.rollback()
            print(f'{op_name} fail', error)
        finally:
            con.commit()

    # ============ 查询方法 ============
    
    @staticmethod
    def selectUserInfoSql(accountType: str, uid: str = "200000126", 
                         money_type: str = 'money_cash_b', 
                         cid: int = 263, 
                         payuid: str = "200000128") -> Optional[Union[int, float, Dict, List]]:
        """查询用户信息（映射字典模式）"""
        # 简单 SQL 直接查
        if accountType in conMysql.SELECT_SIMPLE_MAP:
            sql = conMysql.SELECT_SIMPLE_MAP[accountType].format(uid=uid)
            default = 0
            if accountType in ('union', 'vip'):
                res = conMysql._query_one(sql, default=None)
                if res is None:
                    raise EnvironmentError(f'库表无{"联盟房" if accountType == "union" else "个人房"}')
                return res
            return conMysql._query_one(sql, default)

        # 需要额外参数的 SQL
        if accountType in conMysql.SELECT_WITH_PARAM_MAP:
            sql = conMysql.SELECT_WITH_PARAM_MAP[accountType].format(uid=uid, cid=cid, money_type=money_type)
            return conMysql._query_one(sql, default=0 if accountType != 'level' else None)

        # relation_config 返回字典
        if accountType == 'relation_config':
            sql = conMysql.SELECT_COMPLEX_SQL.format(uid=uid)
            cursor = MySQLConnection.get_cursor()
            try:
                cursor.execute(sql)
                res = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                data_dict = [dict(zip(columns, row)) for row in res]
                return data_dict[0] if data_dict else None
            except Exception as error:
                print(f'Select error: {error}')
                return None

        # relation_id
        if accountType == 'relation_id':
            sql = conMysql.SELECT_RELATION_ID_SQL.format(uid=uid, cid=cid, payuid=payuid)
            return conMysql._query_one(sql, default=0)

        # pay_change 需要解析字典
        if accountType == 'pay_change':
            sql = conMysql.SELECT_PAY_CHANGE_SQL.format(uid=uid)
            cursor = MySQLConnection.get_cursor()
            try:
                cursor.execute(sql)
                res = cursor.fetchone()
                if res:
                    res_dict = ast.literal_eval(res[0])
                    return res_dict.get(str(money_type), 0)
                return 0
            except Exception as error:
                print(f'Select error: {error}')
                return 0

        print(f'{accountType} Error')
        return None

    # ============ 删除方法 ============
    
    @staticmethod
    def deleteUserAccountSql(tableName: str, uid: str) -> None:
        """删除用户账户数据"""
        sql_map = {
            'user_commodity': f"DELETE FROM xs_user_commodity WHERE uid={uid}",
            'user_title': f"DELETE FROM xs_user_title WHERE uid={uid} LIMIT 5",
            'broker_user': f"DELETE FROM xs_broker_user WHERE uid={uid} LIMIT 1",
            'chatroom': f"DELETE FROM xs_chatroom WHERE uid={uid} LIMIT 1",
            'user_box': f"DELETE FROM xs_user_box WHERE uid={uid} LIMIT 1",
            'pay_room_money': f"UPDATE xs_user_profile SET pay_room_money=0 WHERE uid={uid} LIMIT 1",
            'user_title_new': f"UPDATE xs_user_title_new SET subscribe_time=0 WHERE uid={uid} LIMIT 1",
        }
        sql = sql_map.get(tableName)
        if sql:
            conMysql._execute_sql(sql, f'Delete/Update {tableName}')
        else:
            print(f'{tableName} Error')

    # ============ 更新方法 ============
    
    @staticmethod
    def updateUserRidInfoSql(property_rid: str, rid: int, area: str = 'en') -> None:
        """更新房间属性"""
        sql = f"UPDATE xs_chatroom SET property='{property_rid}', area='{area}' WHERE rid={rid}"
        conMysql._execute_sql(sql, 'updateUserRidInfoSql')

    @staticmethod
    def _batch_update(sql_template: str, uids: Tuple[str, ...], op_name: str) -> None:
        """批量更新用户数据"""
        for uid in uids:
            sql = sql_template.format(uid=uid)
            conMysql._execute_sql(sql, op_name)

    @staticmethod
    def updateUserBigArea(*uids: str, bigarea_id: int = 2) -> None:
        """更新用户大区"""
        conMysql._batch_update(
            "UPDATE xs_user_bigarea SET bigarea_id={bigarea_id} WHERE uid IN ({uid})",
            uids, 'Update bigarea'
        )

    @staticmethod
    def updateUserLanguage(*uids: str, language: str = 'zh_CN', area_code: str = 'CN') -> None:
        """更新用户语言"""
        conMysql._batch_update(
            "UPDATE xs_user_settings SET language='{language}', area_code='{area_code}' WHERE uid IN ({uid})",
            uids, 'Update language'
        )

    @staticmethod
    def updateUserMoneyClearSql(*uids: str) -> None:
        """清空用户账户余额"""
        conMysql._batch_update(
            "UPDATE xs_user_money SET money=0, money_b=0, money_cash=0, "
            "money_cash_b=0, gold_coin=0, money_debts=0, money_order=0, "
            "money_order_b=0 WHERE uid={uid}",
            uids, 'Clear money'
        )

    @staticmethod
    def updateMoneySql(uid: str, money: int = 0, money_cash: int = 0, 
                       money_cash_b: int = 0, money_b: int = 0, 
                       gold_coin: int = 0, money_debts: int = 0) -> None:
        """更新用户账户余额"""
        sql = (f"UPDATE xs_user_money SET money={money}, money_b={money_b}, "
               f"money_cash={money_cash}, money_cash_b={money_cash_b}, "
               f"gold_coin={gold_coin}, money_debts={money_debts} "
               f"WHERE uid={uid} LIMIT 1")
        conMysql._execute_sql(sql, 'updateMoneySql')

    @staticmethod
    def updateXsUserpopularity(uid: str) -> None:
        """更新用户人气数据"""
        conMysql._execute_sql(
            f"UPDATE xs_user_popularity SET popularity=0 WHERE uid={uid}",
            'updateXsUserpopularity'
        )

    @staticmethod
    def updateXsUserprofile_pay_room_money(uid: str) -> None:
        """更新用户 VIP 数据"""
        conMysql._execute_sql(
            f"UPDATE xs_user_profile SET pay_room_money=0 WHERE uid={uid}",
            'updateXsUserprofile_pay_room_money'
        )

    # ============ 插入方法 ============
    
    @staticmethod
    def insertXsUserCommodity(uid: str, cid: int, num: int, state: int = 0) -> None:
        """用户背包增加数据"""
        conMysql._execute_sql(
            f"INSERT INTO xs_user_commodity (uid, cid, num, state) VALUES ({uid}, {cid}, {num}, {state})",
            'insertXsUserCommodity'
        )

    @staticmethod
    def insertXsUserBox(uid: str, gift_cid: int = 2505, box_type: str = 'copper') -> None:
        """更新箱子刷新物品"""
        conMysql._execute_sql(
            f"INSERT INTO xs_user_box (last_refresh_cid, last_refresh_sub_cid, uid, type) "
            f"VALUES ({gift_cid}, {gift_cid}, {uid}, '{box_type}')",
            'insertXsUserBox'
        )

    # ============ 检查配置 ============
    
    @staticmethod
    def checkXsGiftConfig(gift_ids: Tuple[int, ...]) -> None:
        """检查礼物配置"""
        conMysql._execute_sql(
            f"UPDATE xs_gift SET deleted=0 WHERE id IN {gift_ids}",
            'checkXsGiftConfig'
        )

    # ============ 专用查询方法 ============
    
    @staticmethod
    def select_greedy_prize(uid: str, round_id: int) -> Tuple:
        """查询摩天轮开奖数据"""
        sql = f"SELECT counter, prize FROM xs_greedy_round_player_v2 WHERE uid={uid} AND round_id={round_id}"
        return conMysql._query_one(sql, default=0)

    @staticmethod
    def select_user_chatroom(property: str, bigarea_id: int = 1) -> int:
        """查询大区房间信息"""
        sql = (f"SELECT rid FROM xs_chatroom a "
               f"LEFT JOIN xs_user_bigarea b ON a.uid=b.uid "
               f"WHERE a.property='{property}' AND b.bigarea_id={bigarea_id} LIMIT 1")
        res = conMysql._query_one(sql, default=None)
        return res[0] if isinstance(res, tuple) else (res if res else 0)

    @staticmethod
    def sqlXsUserpopularity(uid: str) -> int:
        """查询用户人气数据"""
        return conMysql._query_one(
            f"SELECT popularity FROM xs_user_popularity WHERE uid={uid}", default=0
        )

    @staticmethod
    def sqlXsUserprofile_pay_room_money(uid: str) -> int:
        """查询用户 VIP 数据"""
        return conMysql._query_one(
            f"SELECT pay_room_money FROM xs_user_profile WHERE uid={uid}", default=0
        )
