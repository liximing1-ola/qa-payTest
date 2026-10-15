"""
Starify MySQL数据库操作模块
"""
import logging
import time

from common.mysql_base import MySQLConnection as MySQLConnectionBase

logger = logging.getLogger(__name__)


class MySQLConnection(MySQLConnectionBase):
    """Starify MySQL 连接管理器（ali 配置）"""
    _config_name = 'ali'
    _connection = None
    _cursor = None


class ConMysql:
    """MySQL操作类"""

    # ============ 查询方法 ============
    @staticmethod
    def select_user_info_sql(accountType, uid, cid=0, duration_time=86400):
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
        if not item:
            return 0
        sql, params = item
        res = MySQLConnection.execute_query_first(sql, params=params, default=0)
        return res if res is not None else 0

    # ============ 更新方法 ============
    @staticmethod
    def update_money_sql(uid, money):
        """更新用户账户余额"""
        MySQLConnection.execute_write(
            "UPDATE xs_user_money SET star_coin=%s WHERE uid=%s", params=(money, uid))

    @staticmethod
    def update_wealth_sql(uid, wealth, pre_wealth=0):
        """更新用户财富值"""
        MySQLConnection.execute_write(
            "UPDATE xs_user_wealth SET wealth=%s, pre_wealth=%s WHERE uid=%s",
            params=(wealth, pre_wealth, uid))

    @staticmethod
    def update_charm_sql(uid, charm):
        """更新用户魅力值"""
        MySQLConnection.execute_write(
            "UPDATE xs_user_charm SET charm=%s WHERE uid=%s", params=(charm, uid))

    # ============ 删除方法 ============
    @staticmethod
    def delete_user_account_sql(tableName, uid, wid=0):
        """删除用户数据"""
        sql_map = {
            'user_commodity': ("DELETE FROM xs_user_commodity WHERE uid=%s", (uid,)),
            'user_work_reward': ("DELETE FROM xs_user_work_reward WHERE uid=%s AND wid=%s", (uid, wid)),
        }
        item = sql_map.get(tableName)
        if item:
            sql, params = item
            MySQLConnection.execute_write(sql, params=params)

    # ============ 插入方法 ============
    @staticmethod
    def insert_xs_user_commodity(uid, cid, num, period_end=None):
        """向用户背包发礼物"""
        if period_end is None:
            period_end = int(time.time() + 3600)
        MySQLConnection.execute_write(
            "INSERT INTO xs_user_commodity (uid, cid, num, period_end) VALUES(%s, %s, %s, %s)",
            params=(uid, cid, num, period_end)
        )

    # ============ 歌手相关 ============
    @staticmethod
    def delete_producer_singer(singer_uid):
        """清除制作人/歌手关系"""
        sql_list = [
            ("UPDATE xs_audition_singer SET producer_uid=0 WHERE uid=%s", (singer_uid,)),
            ("DELETE FROM xs_audition_relation WHERE singer_uid=%s", (singer_uid,)),
        ]
        for sql, params in sql_list:
            MySQLConnection.execute_write(sql, params=params)

    @staticmethod
    def select_producer_singer(producer_uid):
        """查询已签约歌手人数"""
        sql_list = [
            ("SELECT COUNT(1) FROM xs_audition_relation WHERE producer_uid=%s", (producer_uid,)),
            ("SELECT COUNT(1) FROM xs_audition_purchasing WHERE status=0 AND uid=%s", (producer_uid,)),
        ]
        return sum(
            MySQLConnection.execute_query_first(sql, params=params, default=0) or 0
            for sql, params in sql_list
        )

    @staticmethod
    def update_singer_worth(singer_uid, worth=100):
        """修改歌手身价"""
        MySQLConnection.execute_write(
            "UPDATE xs_audition_singer SET worth=%s WHERE uid=%s", params=(worth, singer_uid))


if __name__ == '__main__':
    logger.info(ConMysql.select_user_info_sql('gift_num', 124458))


# 兼容别名（驼峰 → PascalCase，后续逐步迁移外部调用后可移除）
conMysql = ConMysql
