# coding=utf-8
import pymysql
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
    def selectUserInfoSql(accountType, uid=config.pt_payUid, money_type='money_cash_b'):
        if accountType == 'sum_money':  # 查询用户所有账户数据之和
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
            sql = "select money from xs_pay_change_new where uid={} ORDER BY id DESC LIMIT 1".format(uid)
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
        elif accountType == 'sum_commodity_32':  # 查询用户背包某个物品总数 举例：cid=32 欢乐券
            sql = 'select sum(num) from xs_user_commodity where uid ={} and cid = 32'.format(uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                return int(res[0])
            except Exception as error:
                print(error)

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
        elif tableName == 'user_box':  # 清除xs_user_box用户数据
            sql = "delete from xs_user_box where uid={}".format(uid)
            try:
                conMysql.cur.execute(sql)
            except Exception as error:
                conMysql.con.rollback()
                print('delete fail', error)
            finally:
                conMysql.con.commit()
        else:
            print('{} Error'.format(tableName))

    # 更新用户数据
    @staticmethod
    def updateUserRidInfoSql(property_rid, rid, area='en'):
        sql = "update xs_chatroom set property='{}', area='{}' where rid={}".format(property_rid, area, rid)
        try:
            conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('update fail', error)
        finally:
            conMysql.con.commit()

    # 更新用户大区
    # 1=en 2=cn 3=ar 4=ko 5=id 6=th 7=vi 8=tr 9=ms 10=ja
    # 默认中文大区
    @staticmethod
    def updateUserBigArea(*uids, bigarea_id=2):
        try:
            for uid in uids:
                sql = "update xs_user_bigarea set bigarea_id={} where uid in {}".format(bigarea_id, uid)
                conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('update fail', error)
        finally:
            conMysql.con.commit()

    # 更新用户语言
    @staticmethod
    def updateUserLanguage(*uids, language='zh_CN', area_code='CN'):
        try:
            for uid in uids:
                sql = "update xs_user_settings set language='{}',area_code='{}' where uid in {}".format(language, area_code, uid)
                conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('update fail', error)
        finally:
            conMysql.con.commit()

    #  清空用户账户余额
    @staticmethod
    def updateUserMoneyClearSql(*uids):
        try:
            for uid in uids:
                sql = "update xs_user_money set money=0, money_b=0, money_cash=0, money_cash_b=0, gold_coin=0, " \
                      "money_debts=0, money_order=0, money_order_b=0 where uid={}".format(uid)
                conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('update fail', error)
        finally:
            conMysql.con.commit()

    # 更新用户账户余额
    @staticmethod
    def updateMoneySql(uid, money=0, money_cash=0, money_cash_b=0, money_b=0, gold_coin=0, money_debts=0):
        sql = "update xs_user_money set money={}, money_b={}, money_cash={}, money_cash_b={},gold_coin={}, " \
              "money_debts={} where uid={} limit 1".format(money, money_b, money_cash, money_cash_b, gold_coin, money_debts, uid)
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
        sql = "update xs_gift set deleted=0 where id in {}".format(tuple(i for i in config.pt_giftId.values()))
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
    def insertXsUserBox(uid, gift_cid=2505, box_type='copper'):
        sql = "insert into xs_user_box (last_refresh_cid, last_refresh_sub_cid, uid, type) values ({},{},{},'{}')"\
            .format(gift_cid, gift_cid, uid, box_type)
        try:
            conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('update fail', error)
        finally:
            conMysql.con.commit()

    # 查询摩天轮开奖数据
    @staticmethod
    def select_greedy_prize(uid, round_id):
        sql = "select counter, prize from xs_greedy_round_player_v2 where uid={} and round_id={}".format(uid, round_id)
        try:
            conMysql.cur.execute(sql)
            res = conMysql.cur.fetchone()
            if res is None:
                return 0
            else:
                return res
        except Exception as error:
            print(error)

    # 查询房间信息xs_chatrooom
    @staticmethod
    def select_xs_chatroom(area,property):
        sql = "select rid, area, property from xs_chatroom where area= {} and property ={} limit 1".format(area,
                                                                                                         property)
        try:
            conMysql.cur.execute(sql)
            res = conMysql.cur.fetchone()
            if res is None:
                return 0
            else:
                return res
        except Exception as error:
            print(error)
