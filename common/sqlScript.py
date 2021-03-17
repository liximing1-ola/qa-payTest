# coding=utf-8
import pymysql
from common.Consts import fail_case_reason

class Mysql:

    _dbUrl = '192.168.11.46'
    _dbPort = 3306
    _user = 'root'
    _password = '123456'
    _dbName = 'xianshi'

    @staticmethod
    def conMysql():
        con = pymysql.connect(host=Mysql._dbUrl,
                              port=Mysql._dbPort,
                              user=Mysql._user,
                              passwd=Mysql._password,
                              charset='utf8')
        con.select_db(Mysql._dbName)
        cursor = con.cursor()
        return con, cursor

    # 更新用户的账户余额
    @staticmethod
    def updateMoneySql(uid, money=0, money_cash=0, money_cash_b=0, money_b=0, gold_coin=0):
        con, cur = Mysql.conMysql()
        sql = "update xs_user_money set money={}, money_b={}, money_cash={}, money_cash_b={},gold_coin={} where uid={} limit 1"\
            .format(money, money_b, money_cash, money_cash_b, gold_coin, uid)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('update fail', error)
        finally:
            con.commit()

    # 查询用户当前所有账户余额之和
    @staticmethod
    def selectAllMoneySql(uid):
        con, cur = Mysql.conMysql()
        sql = "select money+money_b+money_cash_b+money_cash from xs_user_money where uid={}".format(uid)
        try:
            cur.execute(sql)
            res = cur.fetchone()
            if len(res) > 0:
                return res[0]
            else:
                return None
        except Exception as error:
            print(error)

    # 查询用户当前金币账户余额
    @staticmethod
    def selectCoinSql(uid):
        con, cur = Mysql.conMysql()
        sql = "select gold_coin from xs_user_money where uid={}".format(uid)
        try:
            cur.execute(sql)
            res = cur.fetchone()
            if len(res) > 0:
                return res[0]
            else:
                return None
        except Exception as error:
            print(error)

    # 查询某个账户的余额值
    @staticmethod
    def selectMoneySql(uid, money_type='money_cash_b'):
        con, cur = Mysql.conMysql()
        sql = "select {} from xs_user_money where uid={}".format(money_type, uid)
        try:
            cur.execute(sql)
            res = cur.fetchone()
            if len(res) > 0:
                return res[0]
            else:
                return None
        except Exception as error:
            print(error)

    # 查询消费记录的money
    @staticmethod
    def selectPayChangeSql(uid):
        con, cur = Mysql.conMysql()
        sql = "select money from xs_pay_change_new where uid={} ORDER BY id DESC LIMIT 1".format(uid)
        try:
            cur.execute(sql)
            res = cur.fetchone()
            if len(res) > 0:
                return res[0]
        except Exception as error:
            print(error)

    # 查询消费记录的消费方式
    @staticmethod
    def selectPayChangeOpSql(uid):
        con, cur = Mysql.conMysql()
        sql = "select op from xs_pay_change_new where uid={} ORDER BY id DESC LIMIT 1".format(uid)
        try:
            cur.execute(sql)
            res = cur.fetchone()
            if len(res) > 0:
                return res[0]
        except Exception as error:
            print(error)

    # 查询用户的背包物品数
    @staticmethod
    def selectUserCommoditySql(uid):
        con, cur = Mysql.conMysql()
        sql = "select count(*) from xs_user_commodity where uid={}".format(uid)
        try:
            cur.execute(sql)
            res = cur.fetchone()
            if int(res[0]) >= 1:
                Mysql.deleteUserCommoditySql(uid)
            else:
                pass
        except Exception as error:
            print(error)

    # 清空用户背包
    @staticmethod
    def deleteUserCommoditySql(uid):
        con, cur = Mysql.conMysql()
        sql = "delete from xs_user_commodity where uid={}".format(uid)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('delete fail', error)
        finally:
            con.commit()

    # 删除用户爵位信息
    @staticmethod
    def deleteUserTitleSql(uid):
        con, cur = Mysql.conMysql()
        sql = "delete from xs_user_title where uid = {} limit 5".format(uid)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('delete fail', error)
        finally:
            con.commit()

    # 删除用户爵位信息 profile
    @staticmethod
    def updateUserTitleSql(uid):
        con, cur = Mysql.conMysql()
        sql = "update xs_user_profile set title=0 where uid={} limit 1".format(uid)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('update fail', error)
        finally:
            con.commit()

    # 检查用户背包指定物品数量
    @staticmethod
    def checkUserCommoditySql(cid, uid):
        con, cur = Mysql.conMysql()
        sql = "select num from xs_user_commodity where cid={} and uid={}".format(cid, uid)
        try:
            cur.execute(sql)
            res = cur.fetchone()
            if len(res) > 0:
                return res[0]
        except Exception as error:
            print(error)

    # 获得用户物品表的对应id
    @staticmethod
    def getUserCommodityIdSql(cid, uid):
        con, cur = Mysql.conMysql()
        sql = "select id from xs_user_commodity where cid={} and uid={}".format(cid, uid)
        try:
            cur.execute(sql)
            res = cur.fetchone()
            if len(res) > 0:
                return res[0]
        except Exception as error:
            print(error)

    # 修改用户为打包结算主播
    @staticmethod
    def updateBrokerUser(uid):
        con, cur = Mysql.conMysql()
        sql = "update xs_broker_user set uid={}, state=1, pack_cal=1  where id = 50 limit 1".format(uid)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('update fail', error)
        finally:
            con.commit()

    # 修改用户为房间房主
    @staticmethod
    def updateChatroomUid(uid):
        con, cur = Mysql.conMysql()
        sql = "update xs_chatroom set app_id=1, uid ={} where rid=193185577 limit 1".format(uid)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('update fail', error)
        finally:
            con.commit()

    # 删除用户工会记录
    @staticmethod
    def deleteXsBrokerUser(uid):
        con, cur = Mysql.conMysql()
        sql = "delete from xs_broker_user where uid ={} limit 1".format(uid)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('delete fail', error)
        finally:
            con.commit()

    # 更新箱子刷新物品
    @staticmethod
    def insertXsUserBox(gift_type, uid, box_type):
        con, cur = Mysql.conMysql()
        sql = "insert into xs_user_box (last_refresh_cid, last_refresh_sub_cid, uid, type) values ({},{},{},'{}')"\
            .format(gift_type, gift_type, uid, box_type)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            fail_case_reason.append(error)
            print('update fail', error)
        finally:
            con.commit()

    # 用户背包增加测试数据
    @staticmethod
    def insertXsUserCommodity(uid, cid, num, state=0):
        con, cur = Mysql.conMysql()
        sql = "insert into xs_user_commodity (uid, cid, num, state) values ({}, {}, {}, {})".format(uid, cid, num, state)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('insert fail', error)
        finally:
            con.commit()

    # 查询箱子开出物品
    @staticmethod
    def selectUserCommodity(uid):
        con, cur = Mysql.conMysql()
        sql = 'select sum(num) from xs_user_commodity where uid ={}'.format(uid)
        try:
            cur.execute(sql)
            res = cur.fetchone()
            return int(res[0])
        except Exception as error:
            print(error)

    # 清除xs_user_box用户数据
    @staticmethod
    def deleteUserBox(uid):
        con, cur = Mysql.conMysql()
        sql = "delete from xs_user_box where uid={} limit 1".format(uid)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            fail_case_reason.append(error)
            print('delete fail', error)
        finally:
            con.commit()







