# coding=utf-8
"""
MySQL 数据库操作模块（普通场景）

提供用户信息查询、账户数据管理、公会/守护关系操作等功能。
使用 SQL 映射字典替代 if-elif 分支，提升可维护性。
"""
import logging
import time
import ast

from common.Config import config
from common.mysql_base import MySQLConnection as MySQLConnectionBase

logger = logging.getLogger(__name__)


class MySQLConnection(MySQLConnectionBase):
    """ MySQL 连接管理器（dev 配置）"""
    _config_name = 'dev'


class conMysql:
    """MySQL 操作类"""

    # ============ SQL 映射字典 ============

    # selectUserInfoSql 简单查询映射（返回单值，默认返回 0）
    SELECT_SIMPLE_MAP = {
        'bean':          "SELECT money_coupon FROM xs_user_money_extend WHERE uid=%s",
        'cash':          "SELECT cash FROM xs_user_money_extend WHERE uid=%s",
        'sum_money':     "SELECT money+money_b+money_cash_b+money_cash FROM xs_user_money WHERE uid=%s",
        'sum_commodity': "SELECT SUM(num) FROM xs_user_commodity WHERE uid=%s",
        'pay_room_money': "SELECT pay_room_money FROM xs_user_profile WHERE uid=%s",
        'popularity':    "SELECT popularity FROM xs_user_popularity WHERE uid=%s",
    }

    # selectUserInfoSql 带 cid 参数的查询映射
    SELECT_WITH_CID_MAP = {
        'num_commodity': "SELECT num FROM xs_user_commodity WHERE cid=%s AND uid=%s",
        'id_commodity':  "SELECT id FROM xs_user_commodity WHERE cid=%s AND uid=%s",
    }

    # selectUserInfoSql 仅 uid 参数的查询映射（返回 None 而非 0）
    SELECT_RETURN_NONE_MAP = {
        'level':      "SELECT level FROM xs_user_title_new WHERE uid=%s",
        'user_index': "SELECT salt FROM xs_user_index WHERE uid=%s",
    }

    # ============ 复杂查询 handler ============

    @staticmethod
    def _select_single_money(uid, money_type):
        """单账户余额查询（money_type 为列名，无法参数化；uid 参数化）"""
        sql = "SELECT {} FROM xs_user_money WHERE uid=%s".format(money_type)
        return MySQLConnection.execute_query_first(sql, params=(uid,), default=None)

    @staticmethod
    def _select_relation_id(uid, cid):
        """守护关系 ID"""
        sql = "SELECT id FROM xs_relation_defend WHERE uid=%s AND defend_uid=%s AND relation_id=%s"
        return MySQLConnection.execute_query_first(sql, params=(config.payUid, uid, cid), default=0)

    @staticmethod
    def _select_relation_config(uid):
        """守护关系配置，返回字典"""
        sql = "SELECT id, name, money_value, break_money, upgrade_money FROM xs_relation_config WHERE id=%s"
        cursor = MySQLConnection.get_cursor()
        try:
            cursor.execute(sql, (uid,))
            res = cursor.fetchall()
            column = [index[0] for index in cursor.description]
            data_dict = [dict(zip(column, row)) for row in res]
            return data_dict[0] if data_dict else None
        except Exception as error:
            logger.error('relation_config query error: %s', error)
            return None

    @staticmethod
    def _select_union():
        """联盟房"""
        sql = "SELECT rid FROM xs_chatroom WHERE property='union' LIMIT 1"
        try:
            res = MySQLConnection.execute_query(sql)
            if res is None:
                raise EnvironmentError('库表无联盟房')
            return res[0]
        except EnvironmentError:
            raise
        except Exception as error:
            logger.error('union query error: %s', error)
            return None

    @staticmethod
    def _select_fleet():
        """家族房"""
        sql = "SELECT rid FROM xs_chatroom WHERE property='fleet' LIMIT 2"
        cursor = MySQLConnection.get_cursor()
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            if not rows:
                raise EnvironmentError('库表无家族房')
            for row in rows:
                if row[0] != config.bb_user.fleetRid:
                    return row[0]
            return rows[0][0]
        except EnvironmentError:
            raise
        except Exception as error:
            logger.error('fleet query error: %s', error)
            return None

    @staticmethod
    def _select_pay_change(uid, money_type):
        """消费记录"""
        sql = 'SELECT reason FROM xs_pay_change WHERE uid=%s ORDER BY id DESC LIMIT 1'
        cursor = MySQLConnection.get_cursor()
        try:
            cursor.execute(sql, (uid,))
            res = cursor.fetchone()
            res_dict = ast.literal_eval(res[0])
            return res_dict.get(money_type, 0)
        except Exception as error:
            logger.error('pay_change query error: %s', error)
            return None

    SELECT_COMPLEX_HANDLERS = {
        'single_money':  lambda uid, money_type, cid: conMysql._select_single_money(uid, money_type),
        'relation_id':   lambda uid, money_type, cid: conMysql._select_relation_id(uid, cid),
        'relation_config': lambda uid, money_type, cid: conMysql._select_relation_config(uid),
        'union':         lambda uid, money_type, cid: conMysql._select_union(),
        'fleet':         lambda uid, money_type, cid: conMysql._select_fleet(),
        'pay_change':    lambda uid, money_type, cid: conMysql._select_pay_change(uid, money_type),
    }

    # deleteUserAccountSql SQL 映射
    DELETE_SQL_MAP = {
        'user_commodity': "DELETE FROM xs_user_commodity WHERE uid=%s",
        'user_title':     "DELETE FROM xs_user_title WHERE uid=%s LIMIT 5",
        'broker_user':    "DELETE FROM xs_broker_user WHERE uid=%s LIMIT 1",
        'chatroom':       "DELETE FROM xs_chatroom WHERE uid=%s LIMIT 1",
        'user_box':       "DELETE FROM xs_user_box WHERE uid=%s LIMIT 1",
    }

    # deleteUserAccountSql 更新类映射（名为 delete 但实际是 update 的操作）
    DELETE_UPDATE_MAP = {
        'user_profile':    "UPDATE xs_user_profile SET title=0 WHERE uid=%s LIMIT 1",
        'user_title_new':  "UPDATE xs_user_title_new SET subscribe_time=0 WHERE uid=%s LIMIT 1",
    }

    # updateUserInfoSql SQL 与参数映射（params_builder 接收 (uid, bid) 返回参数元组）
    UPDATE_USER_INFO_MAP = {
        'broker_user': (
            "UPDATE xs_broker_user SET bid=%s, uid=%s, state=1, pack_cal=1 WHERE id=50 LIMIT 1",
            lambda uid, bid: (bid, uid),
        ),
        'user_index': (
            "UPDATE xs_user_index SET salt=%s, dateline=%s WHERE uid=%s LIMIT 1",
            lambda uid, bid: (bid, int(time.time()), uid),
        ),
        'chatroom': (
            "UPDATE xs_chatroom SET app_id=1, uid=%s, settlement_channel='live', "
            "room_factory_type='business-soundchat' WHERE rid=%s LIMIT 1",
            lambda uid, bid: (uid, config.live_role['live_rid']),
        ),
        'super_chatroom': (
            "UPDATE xs_chatroom SET type='super-voice-fresh', property='business', version=737, "
            "room_factory_type='super-voice-fresh', room_module_id=73, "
            "settlement_channel='super-voice' WHERE rid=%s",
            lambda uid, bid: (uid,),
        ),
    }

    # ============ 内部工具方法 ============

    # ============ 查询方法 ============

    @staticmethod
    def selectUserInfoSql(accountType, uid=config.rewardUid, money_type='money_cash_b', cid=263):
        """查询用户信息

        Args:
            accountType: 查询类型
            uid: 用户 ID
            money_type: 货币类型（用于 single_money 和 pay_change）
            cid: 物品 ID（用于 num_commodity、id_commodity、relation_id）
        """
        # 简单查询（返回单值，默认 0）
        if accountType in conMysql.SELECT_SIMPLE_MAP:
            sql = conMysql.SELECT_SIMPLE_MAP[accountType]
            return MySQLConnection.execute_query_first(sql, params=(uid,), default=0)

        # 带 cid 参数的查询
        if accountType in conMysql.SELECT_WITH_CID_MAP:
            sql = conMysql.SELECT_WITH_CID_MAP[accountType]
            return MySQLConnection.execute_query_first(sql, params=(cid, uid), default=0)

        # 返回 None 的查询
        if accountType in conMysql.SELECT_RETURN_NONE_MAP:
            sql = conMysql.SELECT_RETURN_NONE_MAP[accountType]
            return MySQLConnection.execute_query_first(sql, params=(uid,), default=None)

        # 复杂查询分发
        handler = conMysql.SELECT_COMPLEX_HANDLERS.get(accountType)
        if handler:
            return handler(uid, money_type, cid)

        logger.warning('Unknown accountType: %s', accountType)
        return None

    # ============ 删除方法 ============

    @staticmethod
    def deleteUserAccountSql(tableName, uid):
        """删除/清理用户数据

        Args:
            tableName: 表名标识
            uid: 用户 ID
        """
        # DELETE 类操作
        if tableName in conMysql.DELETE_SQL_MAP:
            sql = conMysql.DELETE_SQL_MAP[tableName]
            MySQLConnection.execute_write(sql, params=(uid,))

        # UPDATE 类操作（历史命名兼容）
        elif tableName in conMysql.DELETE_UPDATE_MAP:
            sql = conMysql.DELETE_UPDATE_MAP[tableName]
            MySQLConnection.execute_write(sql, params=(uid,))

        else:
            logger.warning('deleteUserAccountSql: unknown tableName: %s', tableName)

    # ============ 更新方法 ============

    @staticmethod
    def updateUserInfoSql(tableName, uid, bid=config.live_role['pack_ceo']):
        """更新用户数据

        Args:
            tableName: 表名标识
            uid: 用户 ID
            bid: 主播 ID
        """
        entry = conMysql.UPDATE_USER_INFO_MAP.get(tableName)
        if entry is None:
            logger.warning('updateUserInfoSql: unknown tableName: %s', tableName)
            return
        sql, params_builder = entry
        MySQLConnection.execute_write(sql, params=params_builder(uid, bid))

    # ============ 数据管理方法 ============

    @staticmethod
    def checkXsGiftConfig():
        """检查 xs_gift 配置"""
        gift_ids = tuple(i for i in config.giftId.values())
        placeholders = ','.join(['%s'] * len(gift_ids))
        sql = f"UPDATE xs_gift SET deleted=0 WHERE id IN ({placeholders})"
        MySQLConnection.execute_write(sql, params=gift_ids)

    @staticmethod
    def updateUserMoneyClearSql(*uids):
        """清空用户账户余额"""
        MySQLConnection.clear_user_money(*uids)

    @staticmethod
    def updateMoneySql(uid, money=0, money_cash=0, money_cash_b=0, money_b=0, gold_coin=0, money_debts=0):
        """更新用户账户余额"""
        MySQLConnection.set_user_money(uid, money=money, money_cash=money_cash,
                                       money_cash_b=money_cash_b, money_b=money_b,
                                       gold_coin=gold_coin, money_debts=money_debts)

    @staticmethod
    def deleteUserBeanSql(*uids):
        """删除用户金豆账户数据"""
        sql = "DELETE FROM xs_user_money_extend WHERE uid=%s LIMIT 1"
        for uid in uids:
            time.sleep(0.01)
            MySQLConnection.execute_write(sql, params=(uid,))

    @staticmethod
    def insertBeanSql(uid, money_coupon, cash=0, cash_lock=0):
        """插入用户金豆余额"""
        sql = "INSERT INTO xs_user_money_extend(uid, money_coupon, cash, cash_lock) VALUES(%s,%s,%s,%s)"
        time.sleep(0.01)
        MySQLConnection.execute_write(sql, params=(uid, money_coupon, cash, cash_lock))

    @staticmethod
    def insertXsUserBox(uid, gift_cid=9, box_type='copper'):
        """更新箱子刷新物品"""
        MySQLConnection.insert_user_box(uid, gift_cid, box_type)

    @staticmethod
    def insertXsUserCommodity(uid, cid, num, state=0):
        """用户背包增加测试数据"""
        conMysql.checkXsCommodity(cid)
        MySQLConnection.insert_user_commodity(uid, cid, num, state)

    @staticmethod
    def checkXsCommodity(cid, name='青铜体验券'):
        """检查物品是否存在"""
        sql = "SELECT name FROM xs_commodity WHERE cid=%s"
        res = MySQLConnection.execute_query_first(sql, params=(cid,), default=None)
        if res is None:
            raise Exception('xs_commodity {}不存在'.format(name))

    # ============ 公会/守护关系方法 ============

    @staticmethod
    def _transactional_write(write_fn):
        """在统一的事务中执行写操作"""
        con = MySQLConnection.get_connection()
        cursor = MySQLConnection.get_cursor()
        try:
            write_fn(cursor)
            con.commit()
        except Exception as error:
            con.rollback()
            logger.error('Transactional write error: %s', error)

    @staticmethod
    def checkUserXsBroker(bid):
        """查询工会是否存在，不存在则创建"""
        def _write(cursor):
            cursor.execute('SELECT * FROM xs_broker WHERE bid=%s', (bid,))
            if cursor.fetchone() is None:
                cursor.execute(
                    "INSERT INTO xs_broker (bid, app_id, bname, creater, dateline, types) "
                    "VALUES (%s, %s, '10086', %s, %s, 'live')",
                    (bid, 1, bid, 1571481302)
                )
            else:
                cursor.execute(
                    'UPDATE xs_broker SET creater=%s WHERE bid=%s LIMIT 1',
                    (bid, bid)
                )
        conMysql._transactional_write(_write)

    @staticmethod
    def checkUserXsMentorLevel(uid, level=4):
        """查询用户是否是师父，不是则设为一代宗师"""
        def _write(cursor):
            cursor.execute('SELECT * FROM xs_mentor_exp WHERE uid=%s', (uid,))
            if cursor.fetchone() is None:
                cursor.execute(
                    'INSERT INTO xs_mentor_exp (uid, level) VALUES (%s, %s)',
                    (uid, level)
                )
            else:
                cursor.execute(
                    'UPDATE xs_mentor_exp SET level=%s WHERE uid=%s LIMIT 1',
                    (level, uid)
                )
        conMysql._transactional_write(_write)

    @staticmethod
    def checkUserBroker(uid, bid=136594717):
        """查询工会用户，不存在则创建"""
        def _write(cursor):
            cursor.execute('SELECT id FROM xs_broker_user WHERE uid=%s', (uid,))
            res = cursor.fetchone()
            if res is None:
                cursor.execute(
                    'INSERT INTO xs_broker_user(bid, uid, state) VALUES (%s, %s, 1)',
                    (bid, uid)
                )
            else:
                cursor.execute(
                    'UPDATE xs_broker_user SET uid=%s, bid=%s WHERE id=%s LIMIT 1',
                    (uid, bid, res[0])
                )
        conMysql._transactional_write(_write)

    @staticmethod
    def checkBrokerUserRate(uid, creater, rate=100):
        """查询/设置用户分成比例"""
        def _write(cursor):
            cursor.execute('SELECT * FROM config.bbc_broker_user_rate WHERE uid=%s', (uid,))
            if cursor.fetchone() is None:
                cursor.execute(
                    'INSERT INTO config.bbc_broker_user_rate (uid, broker_creater, rate) VALUES (%s, %s, %s)',
                    (uid, creater, rate)
                )
            else:
                cursor.execute(
                    'UPDATE config.bbc_broker_user_rate SET rate=%s, broker_creater=%s WHERE uid=%s LIMIT 1',
                    (rate, creater, uid)
                )
        conMysql._transactional_write(_write)
