# coding=utf-8
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

    @staticmethod
    def selectUserInfoSql(accountType, uid, cid=0, duration_time=86400):
        if accountType == 'star_coin':  # 查询账户余额
            sql = f"select star_coin from xs_user_money where uid={uid};"
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res is None:
                    return 0
                else:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'gift_num':  # 查询用户背包某个礼物总数
            sql = f'select sum(num) from xs_user_commodity where uid ={uid} and cid = {cid};'
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res[0] is None:
                    return 0
                else:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'commodity_num':  # 查询用户背包某个物品总数
            sql = f'select sum(num) from xs_user_commodity where uid ={uid} and cid = {cid} and duration_time={duration_time};'
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res[0] is None:
                    return 0
                else:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'wealth':  # 查询用户-财富值
            sql = f'select wealth from xs_user_wealth where uid ={uid};'
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res[0] is None:
                    return 0
                else:
                    return res[0]
            except Exception as error:
                print(error)
        elif accountType == 'charm':  # 查询用户-财富值
            sql = f'select charm from xs_user_charm where uid ={uid};'
            try:
                conMysql.cur.execute(sql)
                res = conMysql.cur.fetchone()
                if res[0] is None:
                    return 0
                else:
                    return res[0]
            except Exception as error:
                print(error)

    @staticmethod
    def updateMoneySql(uid, money):
        """更新用户账户余额"""
        sql = f"UPDATE xs_user_money SET star_coin={money} WHERE uid={uid};"
        try:
            conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('update fail', error)
        finally:
            conMysql.con.commit()

    @staticmethod
    def updateWealthSql(uid, wealth, pre_wealth=0):
        """更新用户-财富值"""
        sql = f"UPDATE xs_user_wealth SET wealth={wealth},pre_wealth={pre_wealth} WHERE uid={uid};"
        try:
            conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('update fail', error)
        finally:
            conMysql.con.commit()

    @staticmethod
    def updateCharmSql(uid, charm):
        """更新用户-魅力值"""
        sql = f"UPDATE xs_user_charm SET charm={charm} WHERE uid={uid};"
        try:
            conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('update fail', error)
        finally:
            conMysql.con.commit()

    @staticmethod
    def deleteUserAccountSql(tableName, uid, wid=0):
        if tableName == 'user_commodity':  # 清除用户背包数据
            sql = f"delete from xs_user_commodity where uid={uid}"
            try:
                conMysql.cur.execute(sql)
            except Exception as error:
                conMysql.con.rollback()
                print('delete fail', error)
            finally:
                conMysql.con.commit()
        if tableName == 'user_work_reward':  # 清除用户打赏作品的标记
            sql = f"delete from xs_user_work_reward where uid={uid} and wid={wid};"
            try:
                conMysql.cur.execute(sql)
            except Exception as error:
                conMysql.con.rollback()
                print('delete fail', error)
            finally:
                conMysql.con.commit()

    @staticmethod
    def insertXsUserCommodity(uid, cid, num, period_end=int(time.time() + 3600)):
        """向用户背包发礼物"""
        sql = f"INSERT INTO `xs_user_commodity` (`uid`, `cid`, `num`, `period_end`) VALUES({uid}, {cid}, {num}, {period_end});"
        try:
            conMysql.cur.execute(sql)
        except Exception as error:
            conMysql.con.rollback()
            print('insert fail', error)
        finally:
            conMysql.con.commit()

    @staticmethod
    def deleteProducerSinger(producer_uid, singer_uid):
        """
        清除的制作人/歌手的关系
        :param producer_uid: 制作人uid
        :param singer_uid: 歌手uid
        :return:
        """
        sql1 = f"update xs_audition_singer set producer_uid = 0 where uid= {producer_uid};"
        try:
            conMysql.cur.execute(sql1)
        except Exception as error:
            conMysql.con.rollback()
            print('insert fail', error)
        finally:
            conMysql.con.commit()
        sql2 = f"delete from xs_audition_relation where producer_uid={producer_uid} and singer_uid ={singer_uid};"
        try:
            conMysql.cur.execute(sql2)
        except Exception as error:
            conMysql.con.rollback()
            print('insert fail', error)
        finally:
            conMysql.con.commit()

    @staticmethod
    def selectProducerSinger(producer_uid):
        """
        已签约歌手人数
        :param producer_uid: 制作人uid
        :return:
        """
        sql1 = f"select count(1) from xs_audition_relation where producer_uid = {producer_uid};"
        try:
            conMysql.cur.execute(sql1)
        except Exception as error:
            conMysql.con.rollback()
            print('insert fail', error)
        finally:
            conMysql.con.commit()
        sql2 = f"select count(1) from xs_audition_purchasing where  status=0 and uid={producer_uid}"
        try:
            conMysql.cur.execute(sql2)
        except Exception as error:
            conMysql.con.rollback()
            print('insert fail', error)
        finally:
            conMysql.con.commit()

    @staticmethod
    def updateSingerWorth(singer_uid, worth):
        """
        修改歌手的身价
        :param singer_uid: 歌手uid
        :param worth: 身价
        :return:
        """
        sql = f"update xs_audition_singer set worth={worth} where uid={singer_uid}"
        try:
            conMysql.cur.execute(sql2)
        except Exception as error:
            conMysql.con.rollback()
            print('insert fail', error)
        finally:
            conMysql.con.commit()
if __name__ == '__main__':
    # conMysql.updateMoneySql(124458, 19999)
    print(conMysql.selectUserInfoSql('star_coin', 124458))
