# coding=utf-8
"""
Starify MySQL数据库操作模块
"""
import time
import logging

from common.mysql_base import MySQLConnection as MySQLConnectionBase

logger = logging.getLogger(__name__)


class MySQLConnection(MySQLConnectionBase):
    """Starify MySQL 连接管理器（ali 配置）"""
    _config_name = 'ali'


class conMysql:
    """MySQL操作类"""

    # ============ 通用方法 ============
    @staticmethod
    def sql_fetchone(sql, params=None):
        """执行查询并返回第一行第一列，无结果返回 0"""
        res = MySQLConnection.execute_query(sql, params)
        return res[0] if res and res[0] is not None else 0

    @staticmethod
    def sql_execute(sql, params=None):
        """执行SQL语句"""
        return MySQLConnection.execute_write(sql, params)

    # ============ 查询方法 ============
    @staticmethod
    def selectUserInfoSql(accountType, uid, cid=0, duration_time=86400):
        """查询用户信息"""
        sql_map = {
            'star_coin': ("SELECT star_coin FROM xs_user_money WHERE uid=%s", (uid,)),
            'gift_num': ("SELECT SUM(num) FROM xs_user_commodity WHERE uid=%s AND cid=%s", (uid, cid)),
            'commodity_num': ("SELECT SUM(num) FROM xs_user_commodity WHERE uid=%s AND cid=%s AND duration_time=%s",
                              (uid, cid, duration_time)),
            'wealth': ("SELECT wealth FROM xs_user_wealth WHERE uid=%s", (uid,)),
            'charm': ("SELECT charm FROM xs_user_charm WHERE uid=%s", (uid,)),
        }
        item = sql_map.get(accountType)
        return conMysql.sql_fetchone(*item) if item else 0

    # ============ 更新方法 ============
    @staticmethod
    def updateMoneySql(uid, money):
        """更新用户账户余额"""
        conMysql.sql_execute("UPDATE xs_user_money SET star_coin=%s WHERE uid=%s", (money, uid))

    @staticmethod
    def updateWealthSql(uid, wealth, pre_wealth=0):
        """更新用户财富值"""
        conMysql.sql_execute("UPDATE xs_user_wealth SET wealth=%s, pre_wealth=%s WHERE uid=%s",
                             (wealth, pre_wealth, uid))

    @staticmethod
    def updateCharmSql(uid, charm):
        """更新用户魅力值"""
        conMysql.sql_execute("UPDATE xs_user_charm SET charm=%s WHERE uid=%s", (charm, uid))

    # ============ 删除方法 ============
    @staticmethod
    def deleteUserAccountSql(tableName, uid, wid=0):
        """删除用户数据"""
        sql_map = {
            'user_commodity': ("DELETE FROM xs_user_commodity WHERE uid=%s", (uid,)),
            'user_work_reward': ("DELETE FROM xs_user_work_reward WHERE uid=%s AND wid=%s", (uid, wid)),
        }
        item = sql_map.get(tableName)
        if item:
            conMysql.sql_execute(*item)

    # ============ 插入方法 ============
    @staticmethod
    def insertXsUserCommodity(uid, cid, num, period_end=None):
        """向用户背包发礼物"""
        if period_end is None:
            period_end = int(time.time() + 3600)
        conMysql.sql_execute(
            "INSERT INTO xs_user_commodity (uid, cid, num, period_end) VALUES(%s, %s, %s, %s)",
            (uid, cid, num, period_end)
        )

    # ============ 歌手相关 ============
    @staticmethod
    def deleteProducerSinger(singer_uid):
        """清除制作人/歌手关系"""
        sql_list = [
            ("UPDATE xs_audition_singer SET producer_uid=0 WHERE uid=%s", (singer_uid,)),
            ("DELETE FROM xs_audition_relation WHERE singer_uid=%s", (singer_uid,)),
        ]
        for sql, params in sql_list:
            conMysql.sql_execute(sql, params)

    @staticmethod
    def selectProducerSinger(producer_uid):
        """查询已签约歌手人数"""
        sql_list = [
            ("SELECT COUNT(1) FROM xs_audition_relation WHERE producer_uid=%s", (producer_uid,)),
            ("SELECT COUNT(1) FROM xs_audition_purchasing WHERE status=0 AND uid=%s", (producer_uid,)),
        ]
        return sum(conMysql.sql_fetchone(sql, params) for sql, params in sql_list)

    @staticmethod
    def updateSingerWorth(singer_uid, worth=100):
        """修改歌手身价"""
        conMysql.sql_execute("UPDATE xs_audition_singer SET worth=%s WHERE uid=%s", (worth, singer_uid))


if __name__ == '__main__':
    logger.info(conMysql.selectUserInfoSql('gift_num', 124458))
