# coding=utf-8
import pymysql

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

    @staticmethod
    def updateMoneySql(money, money_cash, money_cash_b, money_b, uid):
        con, cur = Mysql.conMysql()
        sql = "update xs_user_money set money={}, money_b={}, money_cash={}, money_cash_b={} where uid={} limit 1"\
            .format(money, money_b, money_cash, money_cash_b, uid)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('update fail', error)
        finally:
            con.commit()

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

    @staticmethod
    def selectUserCommoditySql(uid):
        con, cur = Mysql.conMysql()
        sql = "select count(*) from xs_user_commodity where uid={}".format(uid)
        try:
            cur.execute(sql)
            res = cur.fetchone()
            if int(res[0]) >= 1:
                Mysql.deleteUserCommoditySql(uid, int(res[0]))
            else:
                pass
        except Exception as error:
            print(error)

    @staticmethod
    def deleteUserCommoditySql(uid, countLimit):
        con, cur = Mysql.conMysql()
        sql = "delete from xs_user_commodity where uid={} limit {}".format(uid, countLimit)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('delete fail', error)
        finally:
            con.commit()

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
        sql = "update xs_chatroom set app_id=1, uid ={}  where rid=193185577 limit 1".format(uid)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('update fail', error)
        finally:
            con.commit()



