# coding=utf-8
"""
MySQL 数据库操作模块（普通场景）

提供用户信息查询、账户数据管理、公会/守护关系操作等功能。
使用 SQL 映射字典替代 if-elif 分支，提升可维护性。
"""
import pymysql
import time
import ast
from typing import Optional, Any
from common.Config import config


class conMysql:
    db_config = {"dev_46_db": '192.168.11.46',
                 "dev_46_user": 'root',
                 "dev_46_pas": '123456'}
    _dbUrl = db_config['dev_46_db']
    _user = db_config['dev_46_user']
    _password = db_config['dev_46_pas']
    _dbName = 'xianshi'
    _dbPort = 3306
    con = pymysql.connect(host=_dbUrl,
                          port=_dbPort,
                          user=_user,
                          passwd=_password,
                          charset='utf8',
                          autocommit=True)
    con.select_db(_dbName)
    con.ping(reconnect=True)
    cur = con.cursor()

    # ============ SQL 映射字典 ============

    # selectUserInfoSql 简单查询映射（返回单值，默认返回 0）
    SELECT_SIMPLE_MAP = {
        'bean':          "SELECT money_coupon FROM xs_user_money_extend WHERE uid={uid}",
        'cash':          "SELECT cash FROM xs_user_money_extend WHERE uid={uid}",
        'sum_money':     "SELECT money+money_b+money_cash_b+money_cash FROM xs_user_money WHERE uid={uid}",
        'sum_commodity': "SELECT SUM(num) FROM xs_user_commodity WHERE uid={uid}",
        'pay_room_money': "SELECT pay_room_money FROM xs_user_profile WHERE uid={uid}",
        'popularity':    "SELECT popularity FROM xs_user_popularity WHERE uid={uid}",
    }

    # selectUserInfoSql 带 cid 参数的查询映射
    SELECT_WITH_CID_MAP = {
        'num_commodity': "SELECT num FROM xs_user_commodity WHERE cid={cid} AND uid={uid}",
        'id_commodity':  "SELECT id FROM xs_user_commodity WHERE cid={cid} AND uid={uid}",
    }

    # selectUserInfoSql 仅 uid 参数的查询映射（返回 None 而非 0）
    SELECT_RETURN_NONE_MAP = {
        'level':      "SELECT level FROM xs_user_title_new WHERE uid={uid}",
        'user_index': "SELECT salt FROM xs_user_index WHERE uid={uid}",
    }

    # deleteUserAccountSql SQL 映射
    DELETE_SQL_MAP = {
        'user_commodity': "DELETE FROM xs_user_commodity WHERE uid={uid}",
        'user_title':     "DELETE FROM xs_user_title WHERE uid={uid} LIMIT 5",
        'broker_user':    "DELETE FROM xs_broker_user WHERE uid={uid} LIMIT 1",
        'chatroom':       "DELETE FROM xs_chatroom WHERE uid={uid} LIMIT 1",
        'user_box':       "DELETE FROM xs_user_box WHERE uid={uid} LIMIT 1",
    }

    # deleteUserAccountSql 更新类映射（名为 delete 但实际是 update 的操作）
    DELETE_UPDATE_MAP = {
        'user_profile':    "UPDATE xs_user_profile SET title=0 WHERE uid={uid} LIMIT 1",
        'user_title_new':  "UPDATE xs_user_title_new SET subscribe_time=0 WHERE uid={uid} LIMIT 1",
    }

    # ============ 内部工具方法 ============

    @staticmethod
    def _query_one(sql: str, default=0):
        """执行查询并返回单条记录第一个字段
        
        Args:
            sql: SQL 语句
            default: 查询无结果时的默认值
            
        Returns:
            查询结果值，异常返回 default
        """
        try:
            conMysql.cur.execute(sql)
            res = conMysql.cur.fetchone()
            if res is None:
                return default
            return res[0]
        except Exception as error:
            print(error)
            return default

    @staticmethod
    def _execute_sql(sql: str, op_name: str = 'execute'):
        """执行 SQL 语句（写操作）
        
        Args:
            sql: SQL 语句
            op_name: 操作名称（用于错误日志）
        """
        try:
            conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print(f'{op_name} fail', error)
        finally:
            conMysql.con.commit()

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
            sql = conMysql.SELECT_SIMPLE_MAP[accountType].format(uid=uid)
            return conMysql._query_one(sql, default=0)

        # 带 cid 参数的查询
        if accountType in conMysql.SELECT_WITH_CID_MAP:
            sql = conMysql.SELECT_WITH_CID_MAP[accountType].format(cid=cid, uid=uid)
            return conMysql._query_one(sql, default=0)

        # 返回 None 的查询
        if accountType in conMysql.SELECT_RETURN_NONE_MAP:
            sql = conMysql.SELECT_RETURN_NONE_MAP[accountType].format(uid=uid)
            return conMysql._query_one(sql, default=None)

        # 单账户余额查询
        if accountType == 'single_money':
            sql = "SELECT {} FROM xs_user_money WHERE uid={}".format(money_type, uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                return res[0] if res and len(res) > 0 else None
            except Exception as error:
                print(error)

        # 守护关系 ID
        elif accountType == 'relation_id':
            sql = "SELECT id FROM xs_relation_defend WHERE uid={} AND defend_uid={} AND relation_id={}".format(
                config.payUid, uid, cid)
            return conMysql._query_one(sql, default=0)

        # 守护关系配置
        elif accountType == 'relation_config':
            sql = "SELECT id, name, money_value, break_money, upgrade_money FROM xs_relation_config WHERE id={}".format(uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchall()
                column = [index[0] for index in conMysql.cur.description]
                data_dict = [dict(zip(column, row)) for row in res]
                return data_dict[0]
            except Exception as error:
                print(error)

        # 联盟房
        elif accountType == 'union':
            sql = "SELECT rid FROM xs_chatroom WHERE property='union' LIMIT 1"
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res is None:
                    raise EnvironmentError('库表无联盟房')
                return res[0]
            except Exception as error:
                print(error)

        # 家族房
        elif accountType == 'fleet':
            sql = "SELECT rid FROM xs_chatroom WHERE property='fleet' LIMIT 1"
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res is None:
                    raise EnvironmentError('库表无家族房')
                if res[0] != config.bb_user['fleetRid']:
                    return res[0]
                return res[1]
            except Exception as error:
                print(error)

        # 消费记录
        elif accountType == 'pay_change':
            sql = 'SELECT reason FROM xs_pay_change WHERE uid={} ORDER BY id DESC LIMIT 1'.format(uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                res_dict = ast.literal_eval(res[0])
                reason_value = '{}'.format(money_type)
                return res_dict.get(reason_value, 0)
            except Exception as error:
                print(error)

        else:
            print('{} Error'.format(accountType))

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
            sql = conMysql.DELETE_SQL_MAP[tableName].format(uid=uid)
            conMysql._execute_sql(sql, 'delete')

        # UPDATE 类操作（历史命名兼容）
        elif tableName in conMysql.DELETE_UPDATE_MAP:
            sql = conMysql.DELETE_UPDATE_MAP[tableName].format(uid=uid)
            conMysql._execute_sql(sql, 'update')

        else:
            print('{} Error'.format(tableName))

    # ============ 更新方法 ============

    @staticmethod
    def updateUserInfoSql(tableName, uid, bid=config.live_role['pack_ceo']):
        """更新用户数据
        
        Args:
            tableName: 表名标识
            uid: 用户 ID
            bid: 主播 ID
        """
        sql_map = {
            'broker_user': "UPDATE xs_broker_user SET bid={}, uid={}, state=1, pack_cal=1 WHERE id=50 LIMIT 1".format(bid, uid),
            'user_index': "UPDATE xs_user_index SET salt='{}', dateline={} WHERE uid={} LIMIT 1".format(
                bid, int(time.time()), uid),
            'chatroom': ("UPDATE xs_chatroom SET app_id=1, uid={}, settlement_channel='live', "
                         "room_factory_type='business-soundchat' WHERE rid={} LIMIT 1").format(
                uid, config.live_role['live_rid']),
            'super_chatroom': ("UPDATE xs_chatroom SET type='super-voice-fresh',property='business',version=737,"
                               "room_factory_type='super-voice-fresh',room_module_id=73,"
                               "settlement_channel='super-voice' WHERE rid={}").format(uid),
        }

        if tableName in sql_map:
            conMysql._execute_sql(sql_map[tableName], 'update')
        else:
            print('{} Error'.format(tableName))

    # ============ 数据管理方法 ============

    @staticmethod
    def checkXsGiftConfig():
        """检查 xs_gift 配置"""
        sql = "UPDATE xs_gift SET deleted=0 WHERE id IN {}".format(
            tuple(i for i in config.giftId.values()))
        conMysql._execute_sql(sql, 'update')

    @staticmethod
    def updateUserMoneyClearSql(*uids):
        """清空用户账户余额"""
        for uid in uids:
            sql = ("UPDATE xs_user_money SET money=0, money_b=0, money_cash=0, "
                   "money_cash_b=0, gold_coin=0, money_debts=0 WHERE uid={}".format(uid))
            conMysql._execute_sql(sql, 'update')

    @staticmethod
    def updateMoneySql(uid, money=0, money_cash=0, money_cash_b=0, money_b=0, gold_coin=0, money_debts=0):
        """更新用户账户余额"""
        sql = ("UPDATE xs_user_money SET money={}, money_b={}, money_cash={}, money_cash_b={}, "
               "gold_coin={}, money_debts={} WHERE uid={} LIMIT 1".format(
                   money, money_b, money_cash, money_cash_b, gold_coin, money_debts, uid))
        conMysql._execute_sql(sql, 'update')

    @staticmethod
    def deleteUserBeanSql(*uids):
        """删除用户金豆账户数据"""
        for uid in uids:
            sql = "DELETE FROM xs_user_money_extend WHERE uid={} LIMIT 1".format(uid)
            time.sleep(0.01)
            conMysql._execute_sql(sql, 'delete')

    @staticmethod
    def insertBeanSql(uid, money_coupon, cash=0, cash_lock=0):
        """插入用户金豆余额"""
        sql = "INSERT INTO xs_user_money_extend(uid, money_coupon, cash, cash_lock) VALUES({},{},{},{})".format(
            uid, money_coupon, cash, cash_lock)
        try:
            conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('insert fail', error)
        finally:
            time.sleep(0.01)
            conMysql.con.commit()

    @staticmethod
    def insertXsUserBox(uid, gift_cid=9, box_type='copper'):
        """更新箱子刷新物品"""
        sql = ("INSERT INTO xs_user_box (last_refresh_cid, last_refresh_sub_cid, uid, type) "
               "VALUES ({},{},{},'{}')".format(gift_cid, gift_cid, uid, box_type))
        conMysql._execute_sql(sql, 'insert')

    @staticmethod
    def insertXsUserCommodity(uid, cid, num, state=0):
        """用户背包增加测试数据"""
        conMysql.checkXsCommodity(cid)
        sql = "INSERT INTO xs_user_commodity (uid, cid, num, state) VALUES ({}, {}, {}, {})".format(
            uid, cid, num, state)
        conMysql._execute_sql(sql, 'insert')

    @staticmethod
    def checkXsCommodity(cid, name='青铜体验券'):
        """检查物品是否存在"""
        sql = "SELECT name FROM xs_commodity WHERE cid={}".format(cid)
        conMysql.cur.execute(sql)
        res = conMysql.cur.fetchone()
        if res is None:
            raise Exception('xs_commodity {}不存在'.format(name))

    # ============ 公会/守护关系方法 ============

    @staticmethod
    def _upsert(sql_select: str, sql_insert: str, sql_update_fn, op_name: str = 'upsert'):
        """通用 upsert 操作：查询存在则更新，不存在则插入
        
        Args:
            sql_select: 查询 SQL
            sql_insert: 插入 SQL（不存在时执行）
            sql_update_fn: 更新 SQL 工厂函数，接收查询结果的第一个字段作为参数
            op_name: 操作名称
        """
        try:
            conMysql.cur.execute(sql_select)
            res = conMysql.cur.fetchone()
            if res is None:
                conMysql.cur.execute(sql_insert)
            else:
                conMysql.cur.execute(sql_update_fn(res[0]))
        except Exception as error:
            print(f'{op_name} error: {error}')
        finally:
            conMysql.con.commit()

    @staticmethod
    def checkUserXsBroker(bid):
        """查询工会是否存在，不存在则创建"""
        sql_select = 'SELECT * FROM xs_broker WHERE bid={}'.format(bid)
        sql_insert = ("INSERT INTO xs_broker (bid,app_id,bname,creater,dateline,types) "
                      "VALUES({}, {}, '10086', {}, {}, 'live')").format(bid, 1, bid, 1571481302)
        sql_update_fn = lambda _: 'UPDATE xs_broker SET creater={} WHERE bid={} LIMIT 1'.format(bid, bid)
        conMysql._upsert(sql_select, sql_insert, sql_update_fn, 'checkUserXsBroker')

    @staticmethod
    def checkUserXsMentorLevel(uid, level=4):
        """查询用户是否是师父，不是则设为一代宗师"""
        sql_select = 'SELECT * FROM xs_mentor_exp WHERE uid={}'.format(uid)
        sql_insert = 'INSERT INTO xs_mentor_exp (uid, level) VALUES({}, {})'.format(uid, level)
        sql_update_fn = lambda _: 'UPDATE xs_mentor_exp SET level={} WHERE uid={} LIMIT 1'.format(level, uid)
        conMysql._upsert(sql_select, sql_insert, sql_update_fn, 'checkUserXsMentorLevel')

    @staticmethod
    def checkUserBroker(uid, bid=136594717):
        """查询工会用户，不存在则创建"""
        sql_select = 'SELECT id FROM xs_broker_user WHERE uid={}'.format(uid)
        sql_insert = 'INSERT INTO xs_broker_user(bid, uid, state) VALUES ({}, {}, 1)'.format(bid, uid)
        sql_update_fn = lambda row_id: 'UPDATE xs_broker_user SET uid={}, bid={} WHERE id={}'.format(uid, bid, row_id)
        conMysql._upsert(sql_select, sql_insert, sql_update_fn, 'checkUserBroker')

    @staticmethod
    def checkBrokerUserRate(uid, creater, rate=100):
        """查询/设置用户分成比例"""
        sql_select = 'SELECT * FROM config.bbc_broker_user_rate WHERE uid={}'.format(uid)
        sql_insert = ('INSERT INTO config.bbc_broker_user_rate (uid, broker_creater, rate) '
                      'VALUES({}, {}, {})').format(uid, creater, rate)
        sql_update_fn = lambda _: ('UPDATE config.bbc_broker_user_rate SET rate={}, broker_creater={} '
                                   'WHERE uid={} LIMIT 1').format(rate, creater, uid)
        conMysql._upsert(sql_select, sql_insert, sql_update_fn, 'checkBrokerUserRate')
