# coding=utf-8
"""
APP MySQL 数据库操作模块

提供统一的数据库连接管理和常用业务操作方法。
使用单例模式管理数据库连接，支持自动重连。
"""
import pymysql
from pymysql import cursors
from typing import Optional, Tuple, Dict, Any
from common.Config import config


# 数据库配置
DB_CONFIG: Dict[str, Any] = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'xianshi',
    'charset': 'utf8',
    'autocommit': True
}


class MySQLConnection:
    """MySQL 连接管理器（单例模式）"""

    _connection: Optional[pymysql.Connection] = None
    _cursor: Optional[pymysql.Cursor] = None

    @classmethod
    def get_connection(cls) -> pymysql.Connection:
        """获取数据库连接
        
        Returns:
            MySQL 连接对象
        """
        if cls._connection is None or not cls._connection.open:
            cls._connection = pymysql.connect(**DB_CONFIG)
            cls._connection.select_db(DB_CONFIG['database'])
        cls._connection.ping(reconnect=True)
        return cls._connection

    @classmethod
    def get_cursor(cls, dict_cursor: bool = False):
        """获取游标
        
        Args:
            dict_cursor: 是否返回字典游标
            
        Returns:
            MySQL 游标对象
        """
        con = cls.get_connection()
        if dict_cursor:
            return con.cursor(cursor=cursors.DictCursor)
        return cls._cursor if cls._cursor else con.cursor()

    @classmethod
    def execute_query(cls, sql: str) -> Optional[Tuple]:
        """执行查询 SQL
        
        Args:
            sql: SQL 语句
            
        Returns:
            查询结果（单条记录），失败返回 None
        """
        try:
            cursor = cls.get_cursor()
            cursor.execute(sql)
            return cursor.fetchone()
        except Exception as e:
            print(f"Query error: {e}")
            return None

    @classmethod
    def execute_write(cls, sql: str) -> bool:
        """执行写 SQL
        
        Args:
            sql: SQL 语句
            
        Returns:
            执行成功返回 True，失败返回 False
        """
        con = cls.get_connection()
        try:
            cursor = cls.get_cursor()
            cursor.execute(sql)
            return True
        except Exception as e:
            con.rollback()
            print(f"Write error: {e}")
            return False
        finally:
            con.commit()


class conMysql:
    """MySQL 操作类"""

    # SQL 映射字典
    QUERY_SQL_MAP: Dict[str, str] = {
        'sum_money': "SELECT money+money_b+money_cash_b+money_cash FROM xs_user_money WHERE uid={uid}",
        'sum_commodity': "SELECT SUM(num) FROM xs_user_commodity WHERE uid={uid}",
        'sum_commodity_32': "SELECT SUM(num) FROM xs_user_commodity WHERE uid={uid} AND cid=32",
        'money_cash_personal': "SELECT money_cash_personal FROM xs_user_money_extend WHERE uid={uid}",
        'chat-pay-card': "SELECT num FROM xs_user_commodity WHERE uid={uid} AND cid=42598",
        'pay_change': "SELECT money FROM xs_pay_change_new WHERE uid={uid} ORDER BY id DESC LIMIT 1",
    }

    DELETE_SQL_MAP: Dict[str, str] = {
        'user_commodity': "DELETE FROM xs_user_commodity WHERE uid={uid}",
        'user_box': "DELETE FROM xs_user_box WHERE uid={uid}",
        'user_journey_planet_draw_record': "DELETE FROM xs_user_journey_planet_draw_record WHERE uid={uid}",
        'user_journey_planet_record': "DELETE FROM xs_user_journey_planet_record WHERE uid={uid}",
        'chat_pay_card_record': "DELETE FROM xs_chat_pay_card_record WHERE uid={uid}",
    }

    # ============ 查询方法 ============
    
    @staticmethod
    def selectUserInfoSql(accountType: str, uid: int = None, money_type: str = 'money_cash_b') -> Optional[int]:
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
            
        if accountType in conMysql.QUERY_SQL_MAP:
            sql = conMysql.QUERY_SQL_MAP[accountType].format(uid=uid)
            res = MySQLConnection.execute_query(sql)
            return int(res[0]) if res and res[0] else 0

        if accountType == 'single_money':
            sql = f"SELECT {money_type} FROM xs_user_money WHERE uid={uid}"
            res = MySQLConnection.execute_query(sql)
            return res[0] if res else None

        print(f'{accountType} Error')
        return None

    # ============ 删除方法 ============
    
    @staticmethod
    def deleteUserAccountSql(tableName: str, uid: int) -> None:
        """删除用户数据
        
        Args:
            tableName: 表名
            uid: 用户 ID
        """
        if tableName in conMysql.DELETE_SQL_MAP:
            sql = conMysql.DELETE_SQL_MAP[tableName].format(uid=uid)
            MySQLConnection.execute_write(sql)
        else:
            print(f'{tableName} Error')

    # ============ 更新方法 ============
    
    @staticmethod
    def updateUserRidInfoSql(property_rid: str, rid: int, area: str = 'en') -> None:
        """更新房间属性
        
        Args:
            property_rid: 属性 RID
            rid: 房间 ID
            area: 区域，默认'en'
        """
        sql = f"UPDATE xs_chatroom SET property='{property_rid}', area='{area}' WHERE rid={rid}"
        MySQLConnection.execute_write(sql)

    @staticmethod
    def updateUserBigArea(*uids: int, bigarea_id: int = 2) -> None:
        """更新用户大区
        
        Args:
            *uids: 用户 ID 列表
            bigarea_id: 大区 ID，默认 2
        """
        for uid in uids:
            sql = f"UPDATE xs_user_bigarea SET bigarea_id={bigarea_id} WHERE uid IN ({uid})"
            MySQLConnection.execute_write(sql)

    @staticmethod
    def updateUserLanguage(*uids: int, language: str = 'zh_CN', area_code: str = 'CN') -> None:
        """更新用户语言
        
        Args:
            *uids: 用户 ID 列表
            language: 语言，默认'zh_CN'
            area_code: 区域代码，默认'CN'
        """
        for uid in uids:
            sql = f"UPDATE xs_user_settings SET language='{language}', area_code='{area_code}' WHERE uid IN ({uid})"
            MySQLConnection.execute_write(sql)

    @staticmethod
    def updateUserMoneyClearSql(*uids: int) -> None:
        """清空用户账户余额
        
        Args:
            *uids: 用户 ID 列表
        """
        for uid in uids:
            sql = ("UPDATE xs_user_money SET money=0, money_b=0, money_cash=0, "
                   "money_cash_b=0, gold_coin=0, money_debts=0, money_order=0, "
                   "money_order_b=0 WHERE uid={uid}".format(uid=uid))
            MySQLConnection.execute_write(sql)

    @staticmethod
    def updateUserextendMoneyClearSql(*uids: int) -> None:
        """清空用户扩展账户余额
        
        Args:
            *uids: 用户 ID 列表
        """
        for uid in uids:
            sql = f"UPDATE xs_user_money_extend SET money_cash_personal=0 WHERE uid={uid}"
            MySQLConnection.execute_write(sql)

    @staticmethod
    def updateMoneySql(uid: int, money: int = 0, money_cash: int = 0, 
                       money_cash_b: int = 0, money_b: int = 0, 
                       gold_coin: int = 0, money_debts: int = 0) -> None:
        """更新用户账户余额
        
        Args:
            uid: 用户 ID
            money: 金豆
            money_cash: 现金
            money_cash_b: 现金 B
            money_b: 金豆 B
            gold_coin: 金币
            money_debts: 债务
        """
        sql = (f"UPDATE xs_user_money SET money={money}, money_b={money_b}, "
               f"money_cash={money_cash}, money_cash_b={money_cash_b}, "
               f"gold_coin={gold_coin}, money_debts={money_debts} "
               f"WHERE uid={uid} LIMIT 1")
        MySQLConnection.execute_write(sql)

    @staticmethod
    def updateXsUserpopularity(uid: int) -> None:
        """更新用户人气数据
        
        Args:
            uid: 用户 ID
        """
        sql = f"UPDATE xs_user_popularity SET popularity=0 WHERE uid={uid}"
        MySQLConnection.execute_write(sql)

    @staticmethod
    def updateXsUserprofile_pay_room_money(uid: int) -> None:
        """更新用户 VIP 数据
        
        Args:
            uid: 用户 ID
        """
        sql = f"UPDATE xs_user_profile SET pay_room_money=0 WHERE uid={uid}"
        MySQLConnection.execute_write(sql)

    # ============ 插入方法 ============
    
    @staticmethod
    def insertXsUserCommodity(uid: int, cid: int, num: int, state: int = 0) -> None:
        """用户背包增加数据
        
        Args:
            uid: 用户 ID
            cid: 物品 ID
            num: 数量
            state: 状态
        """
        sql = f"INSERT INTO xs_user_commodity (uid, cid, num, state) VALUES({uid}, {cid}, {num}, {state})"
        MySQLConnection.execute_write(sql)

    @staticmethod
    def insertXsUserBox(uid: int, gift_cid: int = 2505, box_type: str = 'copper') -> None:
        """更新箱子刷新物品
        
        Args:
            uid: 用户 ID
            gift_cid: 礼物 ID，默认 2505
            box_type: 箱子类型，默认'copper'
        """
        sql = f"INSERT INTO xs_user_box (last_refresh_cid, last_refresh_sub_cid, uid, type) VALUES({gift_cid}, {gift_cid}, {uid}, '{box_type}')"
        MySQLConnection.execute_write(sql)

    # ============ 检查配置 ============
    
    @staticmethod
    def checkXsGiftConfig() -> None:
        """检查礼物配置"""
        gift_ids = tuple(i for i in config.app_giftId.values())
        sql = f"UPDATE xs_gift SET deleted=0 WHERE id IN {gift_ids}"
        MySQLConnection.execute_write(sql)

    # ============ 查询方法 ============
    
    @staticmethod
    def select_greedy_prize(uid: int, round_id: int) -> Tuple:
        """查询摩天轮开奖数据
        
        Args:
            uid: 用户 ID
            round_id: 回合 ID
            
        Returns:
            (counter, prize) 元组，失败返回 0
        """
        sql = f"SELECT counter, prize FROM xs_greedy_round_player_v2 WHERE uid={uid} AND round_id={round_id}"
        res = MySQLConnection.execute_query(sql)
        return res if res else 0

    @staticmethod
    def select_user_chatroom(property: str, bigarea_id: int = 1) -> int:
        """查询大区房间信息
        
        Args:
            property: 属性
            bigarea_id: 大区 ID，默认 1
            
        Returns:
            房间 RID，不存在返回 0
        """
        sql = f"SELECT rid FROM xs_chatroom a LEFT JOIN xs_user_bigarea b ON a.uid=b.uid WHERE a.property='{property}' AND b.bigarea_id={bigarea_id} LIMIT 1"
        res = MySQLConnection.execute_query(sql)
        return res[0] if res else 0

    @staticmethod
    def sqlXsUserpopularity(uid: int) -> int:
        """查询用户人气数据
        
        Args:
            uid: 用户 ID
            
        Returns:
            人气值
        """
        sql = f"SELECT popularity FROM xs_user_popularity WHERE uid={uid}"
        res = MySQLConnection.execute_query(sql)
        return res[0] if res else 0

    @staticmethod
    def sqlXsUserprofile_pay_room_money(uid: int) -> int:
        """查询用户 VIP 数据
        
        Args:
            uid: 用户 ID
            
        Returns:
            VIP 经验值
        """
        sql = f"SELECT pay_room_money FROM xs_user_profile WHERE uid={uid}"
        res = MySQLConnection.execute_query(sql)
        return res[0] if res else 0
