# coding=utf-8
import pymysql
import time
class Mysql:
    db_config = {"dev_46_db": '192.168.11.46',
                 "dev_46_user": 'root',
                 "dev_46_pas": '123456',
                 "ali_db": 'rm-bp1nfl3dp096d5o39.mysql.rds.aliyuncs.com',
                 "ali_user": 'super',
                 "ali_pas": 'dev123456'}
    _dbUrl = db_config['dev_46_db']
    _user = db_config['dev_46_user']
    _password = db_config['dev_46_pas']
    _dbName = 'xianshi'
    _dbPort = 3306

    @staticmethod
    def conMysql():
        con = pymysql.connect(host=Mysql._dbUrl,
                              port=Mysql._dbPort,
                              user=Mysql._user,
                              passwd=Mysql._password,
                              charset='utf8',
                              autocommit=True)
        con.select_db(Mysql._dbName)
        # 断开重连
        # con.ping(reconnect=True)
        cursor = con.cursor()
        return con, cursor

    # 更新用户账户余额
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

    # 删除用户金豆账户数据
    @staticmethod
    def deleteUserBeanSql(*uids):
        con, cur = Mysql.conMysql()
        try:
            for uid in uids:
                sql = "delete from xs_user_money_extend where uid = {} limit 1".format(uid)
                time.sleep(0.01)
                cur.execute(sql)
                con.commit()
        except Exception as error:
            con.rollback()
            print('delete fail', error)

    # 更新用户金豆余额
    @staticmethod
    def updateBeanSql(uid, money_coupon):
        con, cur = Mysql.conMysql()
        sql = "insert into xs_user_money_extend(uid, money_coupon) values({},{})".format(uid, money_coupon)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('insert fail', error)
        finally:
            time.sleep(0.01)
            con.commit()

    # 查询用户金豆余额
    @staticmethod
    def selectBeanSql(uid):
        con, cur = Mysql.conMysql()
        sql = "select money_coupon from xs_user_money_extend where uid={}".format(uid)
        try:
            cur.execute(sql)
            res = cur.fetchone()
            if res is None:
                return 0
            else:
                return res[0]
        except Exception as error:
            print(error)

    # 查询用户所有账户余额总和
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

    # 查询用户某个账户余额
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

    # 查询消费记录的支付方式
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

    # 更新用户爵位信息 profile
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
            if res is None:
                return 0
            else:
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
    def updateBrokerUser(bid, uid):
        con, cur = Mysql.conMysql()
        sql = "update xs_broker_user set bid={}, uid={}, state=1, pack_cal=1 where id = 50 limit 1".format(bid, uid)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('update fail', error)
        finally:
            con.commit()

    # 修改用户为指定工会用户
    @staticmethod
    def updateSuperVoiceUser(bid, uid, nid=101):
        con, cur = Mysql.conMysql()
        sql = "update xs_broker_user set bid={}, uid={}, state=1 where id = {} limit 1".format(bid, uid, nid)
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
        sql = "update xs_chatroom set app_id=1, uid ={}, settlement_channel='live' where rid=193185577 limit 1".format(uid)
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

    # 删除用户商业房
    @staticmethod
    def deleteXsChatroom(uid):
        con, cur = Mysql.conMysql()
        sql = "delete from xs_chatroom where uid ={} limit 1".format(uid)
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
            print('delete fail', error)
        finally:
            con.commit()

    #  xs_user_title_new每次跑都清一下subscribe_time，防止数据溢出
    @staticmethod
    def updateUserTitleSubscribeTime(uid):
        con, cur = Mysql.conMysql()
        sql = "update xs_user_title_new set subscribe_time=0 where uid={} limit 1".format(uid)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('update fail', error)
        finally:
            con.commit()

    # 新建一个直播公会
    @staticmethod
    def insertUserXsBroker(bid):
        con, cur = Mysql.conMysql()
        sql = "insert into xs_broker (bid,app_id,bname,creater,dateline,types) values({}, {}, '{}', {}, {}, '{}')" \
            .format(bid, 1, '10086', bid, 1571481302, 'live')
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('insert fail', error)
        finally:
            con.commit()

    # 更新工会数据
    @staticmethod
    def updateUserXsBroker(bid):
        con, cur = Mysql.conMysql()
        sql = 'update xs_broker set creater={} where bid={}'.format(bid, bid)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('update fail', error)
        finally:
            con.commit()

    # 查询工会是否存在
    @staticmethod
    def selectUserXsBroker(bid):
        con, cur = Mysql.conMysql()
        sql = 'select * from xs_broker where bid={}'.format(bid)
        try:
            cur.execute(sql)
            res = cur.fetchone()
            if res is None:
                Mysql.insertUserXsBroker(bid)
            else:
                Mysql.updateUserXsBroker(bid)
        except Exception as error:
            print(error)

    # 将用户变为一代宗师
    @staticmethod
    def insertXsMentorExpLevel(uid, level):
        con, cur = Mysql.conMysql()
        sql = 'insert into xs_mentor_exp (uid, level) values({}, {})'.format(uid, level)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('insert fail', error)
        finally:
            con.commit()

    # 查询用户是否是师父.不是就把他变成一代宗师（level=4，一代宗师）
    @staticmethod
    def selectUserXsMentorLevel(uid, level=4):
        con, cur = Mysql.conMysql()
        sql = 'select * from xs_mentor_exp where uid={}'.format(uid)
        try:
            cur.execute(sql)
            res = cur.fetchone()
            if res is None:
                Mysql.insertXsMentorExpLevel(uid, level)
            else:
                Mysql.updateUserMentorLevel(uid, level)
        except Exception as error:
            print(error)

    @staticmethod
    def updateUserMentorLevel(uid, level):
        con, cur = Mysql.conMysql()
        sql = "update xs_mentor_exp set level={} where uid={} limit 1".format(level, uid)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('update fail', error)
        finally:
            con.commit()

    # 新建一个经纪人(1-5级/6级)
    @staticmethod
    def insertOnlineEarnAgent(uid, point):
        con, cur = Mysql.conMysql()
        sql = 'insert into xs_online_earn_agent (uid, point,create_time,update_time) values' \
              '({}, {}, 1630577931, 1630577931)'.format(uid, point)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('insert fail', error)
        finally:
            con.commit()

    # 查询用户经纪人身份是否存在,没有就创建一个
    @staticmethod
    def selectOnlineEarnAgent(uid, point=100):
        con, cur = Mysql.conMysql()
        sql = 'select * from xs_online_earn_agent where uid={}'.format(uid)
        try:
            cur.execute(sql)
            res = cur.fetchone()
            if res is None:
                Mysql.insertOnlineEarnAgent(uid, point)
            else:
                Mysql.updateOnlineEarnAgent(uid, point)
        except Exception as error:
            print(error)

    @staticmethod
    def updateOnlineEarnAgent(uid, point):
        con, cur = Mysql.conMysql()
        sql = "update xs_online_earn_agent set point={} where uid={} limit 1".format(point, uid)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('update fail', error)
        finally:
            con.commit()

    # 新建一个艺人
    @staticmethod
    def insertOnlineEarnArtist(uid, point):
        con, cur = Mysql.conMysql()
        sql = 'insert into xs_online_earn_artist (uid, point,create_time,update_time) values' \
              '({}, {}, 1630577931, 1630577931)'.format(uid, point)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('insert fail', error)
        finally:
            con.commit()

    # 查询用户艺人身份是否存在,没有就造一个
    @staticmethod
    def selectOnlineEarnArtist(uid, point=100):
        con, cur = Mysql.conMysql()
        sql = 'select * from xs_online_earn_artist where uid={}'.format(uid)
        try:
            cur.execute(sql)
            res = cur.fetchone()
            if res is None:
                Mysql.insertOnlineEarnArtist(uid, point)
            else:
                return 1
        except Exception as error:
            print(error)

    # 更新艺人和经纪人关联的表
    @staticmethod
    def updateOnlineEarnRelation(agent_uid, artist_uid):
        con, cur = Mysql.conMysql()
        sign_time=int(time.time())
        end_time=sign_time + 604800
        sql = 'update xs_online_earn_relation set agent_uid={}, artist_uid={}, sign_time={}, end_time={} ' \
              'where id=1'.format(agent_uid, artist_uid, sign_time, end_time)
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('update fail', error)
        finally:
            con.commit()

    # 网赚房间
    @staticmethod
    def updateXsFreshRoom():
        con, cur = Mysql.conMysql()
        sql = "update xs_chatroom set type='super-voice-fresh',property='business',version=737," \
              "room_factory_type='super-voice-fresh',room_module_id=73,settlement_channel='super-voice' where rid=200000287"
        try:
            cur.execute(sql)
        except Exception as error:
            con.rollback()
            print('update fail', error)
        finally:
            con.commit()