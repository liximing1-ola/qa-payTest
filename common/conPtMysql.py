# coding=utf-8
import pymysql
import time
from common.Config import config
class conMysql:
    db_config = {"ali_db": 'localhost',
                 "ali_user": 'root',
                 "ali_pas": '123456'}
    _dbUrl = db_config['ali_db']
    _user = db_config['ali_user']
    _password = db_config['ali_pas']
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

    # 查询用户账户信息
    @staticmethod
    def selectUserInfoSql(accountType, uid=config.rewardUid, money_type='money_cash_b', op='money', cid=263):
        if accountType == 'bean':  # 查询用户账户扩展表金豆余额
            sql = "select money_coupon from xs_user_money_extend where uid={}".format(uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res is None:
                    return 0
                else:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'cash':  # 查询用户账户扩展表 现金余额
            sql = "select cash from xs_user_money_extend where uid={}".format(uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res is None:
                    return 0
                else:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'sum_money':  # 查询用户所有账户数据之和
            sql = "select money+money_b+money_cash_b+money_cash from xs_user_money where uid={}".format(uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res is None:
                    return 0
                else:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'single_money':  # 查询用户单个账户数据
            sql = "select {} from xs_user_money where uid={}".format(money_type, uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if len(res) > 0:
                    return res[0]
                else:
                    return None
            except Exception as error:
                print(error)
        elif accountType == 'pay_change':  # 查询用户消费记录数据
            sql = "select {} from xs_pay_change_new where uid={} ORDER BY id DESC LIMIT 1".format(op, uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if len(res) > 0:
                    return res[0]
                else:
                    return 0
            except Exception as error:
                print(error)
        elif accountType == 'sum_commodity':  # 查询用户背包物品总数
            sql = 'select sum(num) from xs_user_commodity where uid ={}'.format(uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                return int(res[0])
            except Exception as error:
                print(error)
        elif accountType == 'num_commodity':  # 查询用户背包物品数量
            sql = "select num from xs_user_commodity where cid={} and uid={}".format(cid, uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res is None:
                    return 0
                else:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'id_commodity':  # 查询用户背包物品ID
            sql = "select id from xs_user_commodity where cid={} and uid={}".format(cid, uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if len(res) > 0:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'relation_id':  # 查询用户守护关系id
            sql = "select id from xs_relation_defend where uid={} and defend_uid={}".format(config.payUid, uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if len(res) > 0:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'relation_config':  # 查询守护关系配置
            sql = "select id, name, money_value, break_money, upgrade_money from xs_relation_config where id={}".format(
                uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchall()
                column = [index[0] for index in conMysql.cur.description]
                data_dict = [dict(zip(column, row)) for row in res]
                return data_dict[0]
            except Exception as error:
                print(error)
        elif accountType == 'union':
            sql = " select rid from xs_chatroom where property='{}' limit 1".format(accountType)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res is None:
                    raise EnvironmentError('库表无联盟房')
                else:
                    return res[0]
            except Exception as error:
                print(error)
        else:
            print('{} Error'.format(accountType))

    # 查询用户账户信息
    @staticmethod
    def selectUserMoneySql(accountType, uid, money_type='money_cash_b', op='money', cid=263):
        if accountType == 'bean':  # 查询用户账户扩展表金豆余额
            sql = "select money_coupon from xs_user_money_extend where uid={}".format(uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res is None:
                    return 0
                else:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'cash':  # 查询用户账户扩展表 现金余额
            sql = "select cash from xs_user_money_extend where uid={}".format(uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res is None:
                    return 0
                else:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'sum_money':  # 查询用户所有账户数据之和
            sql = "select money+money_b+money_cash_b+money_cash from xs_user_money where uid={}".format(uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res is None:
                    return 0
                else:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'single_money':  # 查询用户单个账户数据
            sql = "select {} from xs_user_money where uid={}".format(money_type, uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if len(res) > 0:
                    return res[0]
                else:
                    return None
            except Exception as error:
                print(error)
        elif accountType == 'pay_change':  # 查询用户消费记录数据
            sql = "select {} from xs_pay_change_new where uid={} ORDER BY id DESC LIMIT 1".format(op, uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if len(res) > 0:
                    return res[0]
                else:
                    return 0
            except Exception as error:
                print(error)
        elif accountType == 'sum_commodity':  # 查询用户背包物品总数
            sql = 'select sum(num) from xs_user_commodity where uid ={}'.format(uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                return int(res[0])
            except Exception as error:
                print(error)
        elif accountType == 'num_commodity':  # 查询用户背包物品数量
            sql = "select num from xs_user_commodity where cid={} and uid={}".format(cid, uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res is None:
                    return 0
                else:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'id_commodity':  # 查询用户背包物品ID
            sql = "select id from xs_user_commodity where cid={} and uid={}".format(cid, uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if len(res) > 0:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'relation_id':  # 查询用户守护关系id
            sql = "select id from xs_relation_defend where uid={} and defend_uid={}".format(config.payUid, uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if len(res) > 0:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'relation_config':  # 查询守护关系配置
            sql = "select id, name, money_value, break_money, upgrade_money from xs_relation_config where id={}".format(uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchall()
                column = [index[0] for index in conMysql.cur.description]
                data_dict = [dict(zip(column, row)) for row in res]
                return data_dict[0]
            except Exception as error:
                print(error)
        else:
            print('{} Error'.format(accountType))

    # 删除用户账户数据
    @staticmethod
    def deleteUserAccountSql(tableName, uid):
        if tableName == 'user_commodity':  # 清除用户背包数据
            sql = "delete from xs_user_commodity where uid={}".format(uid)
            try:
                conMysql.cur.execute(sql)
            except Exception as error:
                conMysql.con.rollback()
                print('delete fail', error)
            finally:
                conMysql.con.commit()
        elif tableName == 'user_title':  # 清除用户爵位数据
            sql = "delete from xs_user_title where uid = {} limit 5".format(uid)
            try:
                conMysql.cur.execute(sql)
            except Exception as error:
                conMysql.con.rollback()
                print('delete fail', error)
            finally:
                conMysql.con.commit()
        elif tableName == 'user_profile':  # 修改用户profile爵位数据
            sql = "update xs_user_profile set title=0 where uid={} limit 1".format(uid)
            try:
                conMysql.cur.execute(sql)
            except Exception as error:
                conMysql.con.rollback()
                print('update fail', error)
            finally:
                conMysql.con.commit()
        elif tableName == 'broker_user':  # 删除用户工会记录
            sql = "delete from xs_broker_user where uid ={} limit 1".format(uid)
            try:
                conMysql.cur.execute(sql)
            except Exception as error:
                conMysql.con.rollback()
                print('delete fail', error)
            finally:
                conMysql.con.commit()
        elif tableName == 'chatroom':  # 删除用户商业房
            sql = "delete from xs_chatroom where uid ={} limit 1".format(uid)
            try:
                conMysql.cur.execute(sql)
            except Exception as error:
                conMysql.con.rollback()
                print('delete fail', error)
            finally:
                conMysql.con.commit()
        elif tableName == 'user_box':  # 清除xs_user_box用户数据
            sql = "delete from xs_user_box where uid={} limit 1".format(uid)
            try:
                conMysql.cur.execute(sql)
            except Exception as error:
                conMysql.con.rollback()
                print('delete fail', error)
            finally:
                conMysql.con.commit()
        elif tableName == 'user_title_new':  # xs_user_title_new每次跑都清一下subscribe_time，防止数据溢出
            sql = "update xs_user_title_new set subscribe_time=0 where uid={} limit 1".format(uid)
            try:
                conMysql.cur.execute(sql)
            except Exception as error:
                conMysql.con.rollback()
                print('update fail', error)
            finally:
                conMysql.con.commit()
        else:
            print('{} Error'.format(tableName))

    # 清空用户账户
    @staticmethod
    def updateUserMoneyClearSql(*uids):
        try:
            for uid in uids:
                sql = "update xs_user_money set money=0, money_b=0, money_cash=0, money_cash_b=0, gold_coin=0, money_debts=0, money_order=0, money_order_b=0 where uid={}" \
                    .format(uid)
                conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('update fail', error)
        finally:
            conMysql.con.commit()

    # 更新用户账户余额
    @staticmethod
    def updateMoneySql(uid, money=0, money_cash=0, money_cash_b=0, money_b=0, gold_coin=0, money_debts=0):
        sql = "update xs_user_money set money={}, money_b={}, money_cash={}, money_cash_b={},gold_coin={}, money_debts={} where uid={} limit 1" \
            .format(money, money_b, money_cash, money_cash_b, gold_coin, money_debts, uid)
        try:
            conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('update fail', error)
        finally:
            conMysql.con.commit()

    # 检查xs_gift配置
    @staticmethod
    def checkXsGiftConfig():
        gift_list = tuple(i for i in config.pt_giftId.values())
        sql = "update xs_gift set deleted=0 where id in {}".format(gift_list)
        try:
            conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('update fail', error)
        finally:
            conMysql.con.commit()

    # 用户背包增加测试数据
    @staticmethod
    def insertXsUserCommodity(uid, cid, num, state=0):
        sql = "insert into xs_user_commodity (uid, cid, num, state) values ({}, {}, {}, {})".format(uid, cid, num, state)
        try:
            conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('insert fail', error)
        finally:
            conMysql.con.commit()

    # 更新箱子刷新物品
    @staticmethod
    def insertXsUserBox(uid, gift_cid=9, box_type='copper'):
        sql = "insert into xs_user_box (last_refresh_cid, last_refresh_sub_cid, uid, type) values ({},{},{},'{}')"\
            .format(gift_cid, gift_cid, uid, box_type)
        try:
            conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('update fail', error)
        finally:
            conMysql.con.commit()