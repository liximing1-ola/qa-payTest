# coding=utf-8
"""
PT MySQL数据库操作模块
"""
import pymysql
from pymysql import cursors
from common.Config import config


# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'xianshi',
    'charset': 'utf8',
    'autocommit': True
}


class MySQLConnection:
    """MySQL连接管理器"""

    _connection = None
    _cursor = None

    @classmethod
    def get_connection(cls):
        """获取数据库连接"""
        if cls._connection is None or not cls._connection.open:
            cls._connection = pymysql.connect(**DB_CONFIG)
            cls._connection.select_db(DB_CONFIG['database'])
        cls._connection.ping(reconnect=True)
        return cls._connection

    @classmethod
    def get_cursor(cls, dict_cursor=False):
        """获取游标"""
        con = cls.get_connection()
        if dict_cursor:
            return con.cursor(cursor=cursors.DictCursor)
        return cls._cursor if cls._cursor else con.cursor()

    @classmethod
    def execute_query(cls, sql):
        """执行查询SQL"""
        try:
            cursor = cls.get_cursor()
            cursor.execute(sql)
            return cursor.fetchone()
        except Exception as e:
            print(f"Query error: {e}")
            return None

    @classmethod
    def execute_write(cls, sql):
        """执行写SQL"""
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
    """MySQL操作类"""

    # SQL映射
    QUERY_SQL_MAP = {
        'sum_money': "SELECT money+money_b+money_cash_b+money_cash FROM xs_user_money WHERE uid={uid}",
        'sum_commodity': "SELECT SUM(num) FROM xs_user_commodity WHERE uid={uid}",
        'sum_commodity_32': "SELECT SUM(num) FROM xs_user_commodity WHERE uid={uid} AND cid=32",
        'money_cash_personal': "SELECT money_cash_personal FROM xs_user_money_extend WHERE uid={uid}",
        'chat-pay-card': "SELECT num FROM xs_user_commodity WHERE uid={uid} AND cid=42598",
        'pay_change': "SELECT money FROM xs_pay_change_new WHERE uid={uid} ORDER BY id DESC LIMIT 1",
    }

    DELETE_SQL_MAP = {
        'user_commodity': "DELETE FROM xs_user_commodity WHERE uid={uid}",
        'user_box': "DELETE FROM xs_user_box WHERE uid={uid}",
        'user_journey_planet_draw_record': "DELETE FROM xs_user_journey_planet_draw_record WHERE uid={uid}",
        'user_journey_planet_record': "DELETE FROM xs_user_journey_planet_record WHERE uid={uid}",
        'chat_pay_card_record': "DELETE FROM xs_chat_pay_card_record WHERE uid={uid}",
    }

    # ============ 查询方法 ============
    @staticmethod
    def selectUserInfoSql(accountType, uid=config.pt_payUid, money_type='money_cash_b'):
        """查询用户信息"""
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
    def deleteUserAccountSql(tableName, uid):
        """删除用户数据"""
        if tableName in conMysql.DELETE_SQL_MAP:
            sql = conMysql.DELETE_SQL_MAP[tableName].format(uid=uid)
            MySQLConnection.execute_write(sql)
        else:
            print(f'{tableName} Error')

    # ============ 更新方法 ============
    @staticmethod
    def updateUserRidInfoSql(property_rid, rid, area='en'):
        """更新房间属性"""
        sql = f"UPDATE xs_chatroom SET property='{property_rid}', area='{area}' WHERE rid={rid}"
        MySQLConnection.execute_write(sql)

    @staticmethod
    def updateUserBigArea(*uids, bigarea_id=2):
        """更新用户大区"""
        for uid in uids:
            sql = f"UPDATE xs_user_bigarea SET bigarea_id={bigarea_id} WHERE uid IN ({uid})"
            MySQLConnection.execute_write(sql)

    @staticmethod
    def updateUserLanguage(*uids, language='zh_CN', area_code='CN'):
        """更新用户语言"""
        for uid in uids:
            sql = f"UPDATE xs_user_settings SET language='{language}', area_code='{area_code}' WHERE uid IN ({uid})"
            MySQLConnection.execute_write(sql)

    @staticmethod
    def updateUserMoneyClearSql(*uids):
        """清空用户账户余额"""
        for uid in uids:
            sql = f"UPDATE xs_user_money SET money=0, money_b=0, money_cash=0, money_cash_b=0, gold_coin=0, money_debts=0, money_order=0, money_order_b=0 WHERE uid={uid}"
            MySQLConnection.execute_write(sql)

    @staticmethod
    def updateUserextendMoneyClearSql(*uids):
        """清空用户扩展账户余额"""
        for uid in uids:
            sql = f"UPDATE xs_user_money_extend SET money_cash_personal=0 WHERE uid={uid}"
            MySQLConnection.execute_write(sql)

    @staticmethod
    def updateMoneySql(uid, money=0, money_cash=0, money_cash_b=0, money_b=0, gold_coin=0, money_debts=0):
        """更新用户账户余额"""
        sql = f"UPDATE xs_user_money SET money={money}, money_b={money_b}, money_cash={money_cash}, money_cash_b={money_cash_b}, gold_coin={gold_coin}, money_debts={money_debts} WHERE uid={uid} LIMIT 1"
        MySQLConnection.execute_write(sql)

    @staticmethod
    def updateXsUserpopularity(uid):
        """更新用户人气数据"""
        sql = f"UPDATE xs_user_popularity SET popularity=0 WHERE uid={uid}"
        MySQLConnection.execute_write(sql)

    @staticmethod
    def updateXsUserprofile_pay_room_money(uid):
        """更新用户VIP数据"""
        sql = f"UPDATE xs_user_profile SET pay_room_money=0 WHERE uid={uid}"
        MySQLConnection.execute_write(sql)

    # ============ 插入方法 ============
    @staticmethod
    def insertXsUserCommodity(uid, cid, num, state=0):
        """用户背包增加数据"""
        sql = f"INSERT INTO xs_user_commodity (uid, cid, num, state) VALUES({uid}, {cid}, {num}, {state})"
        MySQLConnection.execute_write(sql)

    @staticmethod
    def insertXsUserBox(uid, gift_cid=2505, box_type='copper'):
        """更新箱子刷新物品"""
        sql = f"INSERT INTO xs_user_box (last_refresh_cid, last_refresh_sub_cid, uid, type) VALUES({gift_cid}, {gift_cid}, {uid}, '{box_type}')"
        MySQLConnection.execute_write(sql)

    # ============ 检查配置 ============
    @staticmethod
    def checkXsGiftConfig():
        """检查礼物配置"""
        gift_ids = tuple(i for i in config.pt_giftId.values())
        sql = f"UPDATE xs_gift SET deleted=0 WHERE id IN {gift_ids}"
        MySQLConnection.execute_write(sql)

    # ============ 查询方法 ============
    @staticmethod
    def select_greedy_prize(uid, round_id):
        """查询摩天轮开奖数据"""
        sql = f"SELECT counter, prize FROM xs_greedy_round_player_v2 WHERE uid={uid} AND round_id={round_id}"
        res = MySQLConnection.execute_query(sql)
        return res if res else 0

    @staticmethod
    def select_user_chatroom(property, bigarea_id=1):
        """查询大区房间信息"""
        sql = f"SELECT rid FROM xs_chatroom a LEFT JOIN xs_user_bigarea b ON a.uid=b.uid WHERE a.property='{property}' AND b.bigarea_id={bigarea_id} LIMIT 1"
        res = MySQLConnection.execute_query(sql)
        return res[0] if res else 0

    @staticmethod
    def sqlXsUserpopularity(uid):
        """查询用户人气数据"""
        sql = f"SELECT popularity FROM xs_user_popularity WHERE uid={uid}"
        res = MySQLConnection.execute_query(sql)
        return res[0] if res else 0

    @staticmethod
    def sqlXsUserprofile_pay_room_money(uid):
        """查询用户VIP数据"""
        sql = f"SELECT pay_room_money FROM xs_user_profile WHERE uid={uid}"
        res = MySQLConnection.execute_query(sql)
        return res[0] if res else 0
