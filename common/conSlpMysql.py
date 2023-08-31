# coding=utf-8
import ast
import time

import pymysql


class conMysql:
    db_config = {
        "ali_db": '127.0.0.1',
        "ali_user": 'root',
        "ali_pas": 'root'
    }
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
    def selectUserInfoSql(accountType, uid="200000126", money_type='money_cash_b', cid=263, payuid="200000128"):
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
        elif accountType == 'pay_room_money':  # 用户vip等级经验
            sql = "select pay_room_money from xs_user_profile where uid={}".format(uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res is None:
                    return 0
                else:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'popularity':  # 用户人气等级经验
            sql = "select popularity from xs_user_popularity where uid={}".format(uid)
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
        elif accountType == 'level':  # 查询用户爵位等级
            sql = "select level from xs_user_title_new where uid={}".format(uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if len(res) > 0:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'growth':  # 查询用户成长值
            sql = "select growth from xs_user_title_new where uid={}".format(uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if len(res) > 0:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'user_index':  # 查询用户salt
            sql = "select salt from xs_user_index where uid = {}".format(uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if len(res) > 0:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'relation_id':  # 查询用户守护关系id
            sql = "select id from xs_relation_defend where uid={} and defend_uid={} and relation_id={}". \
                format(payuid, uid, cid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res is None:
                    return 0
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
        elif accountType == 'vip':
            sql = " select rid from xs_chatroom where property='{}' limit 1".format(accountType)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res is None:
                    raise EnvironmentError('库表无个人房')
                else:
                    return res[0]
            except Exception as error:
                print(error)
        # elif accountType == 'fleet':
        #     sql = " select rid from xs_chatroom where property='{}' limit 1".format(accountType)
        #     try:
        #         conMysql.cur.execute(sql)
        #         res = conMysql.cur.fetchone()
        #         if res is None:
        #             raise EnvironmentError('库表无家族房')
        #         else:
        #             if res[0] != config.bb_user['fleetRid']:
        #                 return res[0]
        #             return res[1]
        #     except Exception as error:
        #         print(error)
        elif accountType == 'pay_change':  # 查询用户消费记录数据
            sql = 'select reason from xs_pay_change where uid={} order by id desc LIMIT 1'.format(uid)
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                res_dict = ast.literal_eval(res[0])
                reason_value = '{}'.format(money_type)
                if reason_value in res_dict.keys():
                    return res_dict[reason_value]
                else:
                    return 0
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
        # elif tableName == 'user_profile':  # 修改用户profile爵位数据
        #     sql = "update xs_user_profile set title=0 where uid={} limit 1".format(uid)
        #     try:
        #         conMysql.cur.execute(sql)
        #     except Exception as error:
        #         conMysql.con.rollback()
        #         print('update fail', error)
        #     finally:
        #         conMysql.con.commit()
        elif tableName == 'pay_room_money':  # VIP 修改用户pay_room_money爵位数据
            sql = "update xs_user_profile set pay_room_money=0 where uid={} limit 1".format(uid)
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
        elif tableName == 'user_popularity':  # 人气值
            sql = "update xs_user_popularity set popularity=0 where uid ={};".format(uid)
            try:
                conMysql.cur.execute(sql)
            except Exception as error:
                conMysql.con.rollback()
                print('update fail', error)
            finally:
                conMysql.con.commit()
        elif tableName == 'pay_change':  # 送礼流水
            sql = f"delete from xs_pay_change WHERE uid = {uid};"
            try:
                conMysql.cur.execute(sql)
            except Exception as error:
                conMysql.con.rollback()
                print('update fail', error)
            finally:
                conMysql.con.commit()
        else:
            print('{} Error'.format(tableName))

    # 更新用户数据
    @staticmethod
    def updateUserInfoSql(tableName, uid, level=10):
        # if tableName == 'broker_user':  # 修改用户为打包结算主播
        #     sql = "update xs_broker_user set bid={}, uid={}, state=1, pack_cal=1 where id = 50 limit 1".format(bid, uid)
        #     try:
        #         conMysql.cur.execute(sql)
        #     except Exception as error:
        #         conMysql.con.rollback()
        #         print('update fail', error)
        #     finally:
        #         conMysql.con.commit()
        #
        # elif tableName == 'user_index':  # 修改用户xs_user_index:salt
        #     dateline = int(time.time())
        #     sql = "update xs_user_index set salt='{}', dateline={} where uid={} limit 1".format(bid, dateline, uid)
        #     try:
        #         conMysql.cur.execute(sql)
        #     except Exception as error:
        #         conMysql.con.rollback()
        #         print('update fail', error)
        #     finally:
        #         conMysql.con.commit()
        #
        # # elif tableName == 'chatroom':  # 修改用户为房间房主
        # #     sql = "update xs_chatroom set app_id=1, uid={}, settlement_channel='live', " \
        # #           "room_factory_type='business-soundchat' where rid={} limit 1".format(uid, bid)
        # #     try:
        # #         conMysql.cur.execute(sql)
        # #     except Exception as error:
        # #         conMysql.con.rollback()
        # #         print('update fail', error)
        # #     finally:
        # #         conMysql.con.commit()
        #
        # # elif tableName == 'super_chatroom':
        # #     sql = "update xs_chatroom set type='super-voice-fresh',property='business',version=737,room_factory_type='super-voice-fresh'," \
        # #           "room_module_id=73,settlement_channel='super-voice' where rid={}".format(uid)
        # #     try:
        # #         conMysql.cur.execute(sql)
        # #     except Exception as error:
        # #         conMysql.con.rollback()
        # #         print('update fail', error)
        # #     finally:
        # #         conMysql.con.commit()
        # # elif tableName == 'user_title_new':  #dev开通1个月贵族
        # #     sql = "update xs_user_title_new set subscribe_time={},growth=10,level=10 where uid={} limit 1".format(time.time()+30*60*60,uid)
        # #     try:
        # #         conMysql.cur.execute(sql)
        # #     except Exception as error:
        # #         conMysql.con.rollback()
        # #         print('update fail', error)
        # #     finally:
        # #         conMysql.con.commit()
        # # elif tableName == 'level':  # 查询用户爵位等级
        # #     sql = "update xs_user_title_new set level={} where uid={}".format(level,uid)
        # #     try:
        # #         conMysql.cur.execute(sql)
        # #     except Exception as error:
        # #         conMysql.con.rollback()
        # #         print('update fail', error)
        # #     finally:
        # #         conMysql.con.commit()
        if tableName == 'user_title_new':  # 修改用户爵位等级
            jw_config = {
                "0": 0,
                "10": 0,
                "20": 20000,
                "30": 80000,
                "40": 250000,
                "50": 1000000,
                "60": 2500000,
                "70": 6500000,
                "80": 15000000,
                "90": 50000000,
            }
            subscribe_time = int(time.time()) + 1 * 24 * 60 * 60
            sql = f"""update xs_user_title_new set level={level},growth={jw_config[str(level)]},effective_value={jw_config[str(level)]},subscribe_time={subscribe_time} where uid ={uid};"""
            try:
                conMysql.cur.execute(sql)
            except Exception as error:
                conMysql.con.rollback()
                print('update fail', error)
            finally:
                conMysql.con.commit()
        else:
            print('{} Error'.format(tableName))

    # # 检查xs_gift配置
    # @staticmethod
    # def checkXsGiftConfig():
    #     sql = "update xs_gift set deleted=0 where id in {}".format(tuple(i for i in config.giftId.values()))
    #     try:
    #         conMysql.cur.execute(sql)
    #     except Exception as error:
    #         conMysql.con.rollback()
    #         print('update fail', error)
    #     finally:
    #         conMysql.con.commit()

    # 清空用户账户
    @staticmethod
    def updateUserMoneyClearSql(*uids):
        try:
            for uid in uids:
                sql = "update xs_user_money set money=0, money_b=0, money_cash=0, money_cash_b=0, gold_coin=0, " \
                      "money_debts=0 where uid={}".format(uid)
                conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('update fail', error)
        finally:
            conMysql.con.commit()

    # 更新用户账户余额
    @staticmethod
    def updateMoneySql(uid, money=0, money_cash=0, money_cash_b=0, money_b=0, gold_coin=0, money_debts=0):
        sql = "update xs_user_money set money={}, money_b={}, money_cash={}, money_cash_b={},gold_coin={}, money_debts={} " \
              "where uid={} limit 1".format(money, money_b, money_cash, money_cash_b, gold_coin, money_debts, uid)
        try:
            conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('update fail', error)
        finally:
            conMysql.con.commit()

    # # 删除用户金豆账户数据
    # @staticmethod
    # def deleteUserBeanSql(*uids):
    #     try:
    #         for uid in uids:
    #             sql = "delete from xs_user_money_extend where uid = {} limit 1".format(uid)
    #             time.sleep(0.01)
    #             conMysql.cur.execute(sql)
    #             conMysql.con.commit()
    #     except Exception as error:
    #         conMysql.con.rollback()
    #         print('delete fail', error)

    # # 插入用户金豆余额
    # @staticmethod
    # def insertBeanSql(uid, money_coupon, cash=0, cash_lock=0):
    #     sql = "insert into xs_user_money_extend(uid, money_coupon, cash, cash_lock) values({},{},{},{})" \
    #         .format(uid, money_coupon, cash, cash_lock)
    #     try:
    #         conMysql.cur.execute(sql)
    #     except Exception as error:
    #         conMysql.con.rollback()
    #         print('insert fail', error)
    #     finally:
    #         time.sleep(0.01)
    #         conMysql.con.commit()
    #
    # # 更新箱子刷新物品
    # @staticmethod
    # def insertXsUserBox(uid, gift_cid=9, box_type='copper'):
    #     sql = "insert into xs_user_box (last_refresh_cid, last_refresh_sub_cid, uid, type) values ({},{},{},'{}')" \
    #         .format(gift_cid, gift_cid, uid, box_type)
    #     try:
    #         conMysql.cur.execute(sql)
    #     except Exception as error:
    #         conMysql.con.rollback()
    #         print('update fail', error)
    #     finally:
    #         conMysql.con.commit()

    # 用户背包增加测试数据
    @staticmethod
    def insertXsUserCommodity(uid, cid, num, state=0):
        conMysql.checkXsCommodity(cid)
        sql = "insert into xs_user_commodity (uid, cid, num, state) values ({}, {}, {}, {})".format(uid, cid, num,
                                                                                                    state)
        try:
            conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('insert fail', error)
        finally:
            conMysql.con.commit()

    @staticmethod
    def checkXsCommodity(cid, name='青铜体验券'):
        sql = "select name from xs_commodity where cid={}".format(cid)
        conMysql.cur.execute(sql)
        res = conMysql.cur.fetchone()
        if res is None:
            raise Exception('xs_commodity {}不存在'.format(name))

    # 查询工会是否存在
    @staticmethod
    def checkUserXsBroker(bid):
        sql = 'select * from xs_broker where bid={}'.format(bid)
        try:
            conMysql.cur.execute(sql)
            res = conMysql.cur.fetchone()
            if res is None:
                sql = "insert into xs_broker (bid,app_id,bname,creater,dateline,types) values({}, {}, '{}', {}, {}, '{}')" \
                    .format(bid, 1, '10086', bid, 1571481302, 'live')
                try:
                    conMysql.cur.execute(sql)
                except Exception as error:
                    conMysql.con.rollback()
                    print('insert fail', error)
            else:
                sql = 'update xs_broker set creater={} where bid={} limit 1'.format(bid, bid)
                try:
                    conMysql.cur.execute(sql)
                except Exception as error:
                    conMysql.con.rollback()
                    print('update fail', error)
        except Exception as error:
            print(error)
        finally:
            conMysql.con.commit()

    # 查询用户是否是师父.不是就把他变成一代宗师（level=4，一代宗师）
    @staticmethod
    def checkUserXsMentorLevel(uid, level=4):
        sql = 'select * from xs_mentor_exp where uid={}'.format(uid)
        try:
            conMysql.cur.execute(sql)
            res = conMysql.cur.fetchone()
            if res is None:
                sql = 'insert into xs_mentor_exp (uid, level) values({}, {})'.format(uid, level)
                try:
                    conMysql.cur.execute(sql)
                except Exception as error:
                    conMysql.con.rollback()
                    print('insert fail', error)
            else:
                sql = "update xs_mentor_exp set level={} where uid={} limit 1".format(level, uid)
                try:
                    conMysql.cur.execute(sql)
                except Exception as error:
                    conMysql.con.rollback()
                    print('update fail', error)
        except Exception as error:
            print(error)
        finally:
            conMysql.con.commit()

    # 查询工会用户
    @staticmethod
    def checkUserBroker(uid, bid=136594717):
        sql = 'select id from xs_broker_user where uid={}'.format(uid)
        try:
            conMysql.cur.execute(sql)
            res = conMysql.cur.fetchone()
            if res is None:
                sql = "insert into xs_broker_user(bid, uid, state) values ({}, {}, 1)".format(bid, uid)
                try:
                    conMysql.cur.execute(sql)
                except Exception as error:
                    conMysql.con.rollback()
                    print('insert fail', error)
            else:
                sql = 'update xs_broker_user set uid={}, bid={} where id={}'.format(uid, bid, res[0])
                try:
                    conMysql.cur.execute(sql)
                except Exception as error:
                    conMysql.con.rollback()
                    print('update fail', error)
        except Exception as error:
            print(error)
        finally:
            conMysql.con.commit()

    # # 查询用户分成比
    # @staticmethod
    # def checkBrokerUserRate(uid, creater, rate=100):
    #     sql = 'select * from config.bbc_broker_user_rate where uid={}'.format(uid)
    #     try:
    #         conMysql.cur.execute(sql)
    #         res = conMysql.cur.fetchone()
    #         if res is None:
    #             sql = 'insert into config.bbc_broker_user_rate (uid, broker_creater, rate) values({}, {}, {})' \
    #                 .format(uid, creater, rate)
    #             try:
    #                 conMysql.cur.execute(sql)
    #             except Exception as error:
    #                 conMysql.con.rollback()
    #                 print('insert fail', error)
    #         else:
    #             sql = "update config.bbc_broker_user_rate set rate={}, broker_creater={} where uid={} limit 1" \
    #                 .format(rate, creater, uid)
    #             try:
    #                 conMysql.cur.execute(sql)
    #             except Exception as error:
    #                 conMysql.con.rollback()
    #                 print('update fail', error)
    #     except Exception as error:
    #         print(error)
    #     finally:
    #         conMysql.con.commit()

    # 查询rid的房间类型
    @staticmethod
    def checkRidFactoryType(rid):
        sql = 'select room_factory_type from xs_chatroom where rid={}'.format(rid)
        try:
            conMysql.cur.execute(sql)
            res = conMysql.cur.fetchone()
            if len(res) > 0:
                return res[0]
            else:
                return None
        except Exception as error:
            print(error)

    # 修改大神认证 1=同意,0=不同意
    @staticmethod
    def updateUserGodSql(uid, agreement_version):
        try:
            sql = f"update xs_user_settings set agreement_version={agreement_version} where uid={uid}"
            conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('update fail', error)
        finally:
            conMysql.con.commit()

    # 查询甄选礼盒打赏数据
    @staticmethod
    def selectZxPayData(uid):
        sql = f"""
        SELECT JSON_EXTRACT(reason, '$.to') AS to_uid,JSON_EXTRACT(reason, '$.gid') AS gid,SUM(JSON_EXTRACT(reason, '$.num')) AS total_num FROM xs_pay_change WHERE uid = {uid} AND JSON_UNQUOTE(JSON_EXTRACT(reason, '$.obr')) IS NOT NULL GROUP BY gid, to_uid ORDER BY to_uid;
        """
        try:
            cur = conMysql.con.cursor(cursor=pymysql.cursors.DictCursor)
            cur.execute(sql)
            res = cur.fetchall()
            if res is None:
                return 0
            else:
                return res
        except Exception as error:
            print(error)


if __name__ == '__main__':
    data = conMysql().selectZxPayData("200000216")
    print(data)
