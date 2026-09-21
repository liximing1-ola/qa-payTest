# coding=utf-8
"""
common/conStarifyMysql.py 单元测试（SQL 分发 / 参数组装 / 签约歌手查询）

全部 mock MySQLConnection 底层执行方法，可在无数据库环境下直接运行：
    python -m pytest tests/test_conStarifyMysql.py -v
"""
import time
import unittest
from unittest.mock import call, patch

from common.conStarifyMysql import MySQLConnection, conMysql


class TestSelectUserInfoSql(unittest.TestCase):
    """selectUserInfoSql 分发与参数组装"""

    def test_star_coin(self):
        with patch.object(MySQLConnection, 'execute_query_first', return_value=7) as m:
            res = conMysql.selectUserInfoSql('star_coin', 111)
        self.assertEqual(res, 7)
        m.assert_called_once_with(
            'SELECT star_coin FROM xs_user_money WHERE uid=%s',
            params=(111,), default=0)

    def test_gift_num_params(self):
        """gift_num 参数顺序应为 (uid, cid)"""
        with patch.object(MySQLConnection, 'execute_query_first', return_value=3) as m:
            res = conMysql.selectUserInfoSql('gift_num', 111, cid=88)
        self.assertEqual(res, 3)
        m.assert_called_once_with(
            'SELECT SUM(num) FROM xs_user_commodity WHERE uid=%s AND cid=%s',
            params=(111, 88), default=0)

    def test_commodity_num_with_duration(self):
        """commodity_num 参数应为 (uid, cid, duration_time)"""
        with patch.object(MySQLConnection, 'execute_query_first', return_value=1) as m:
            conMysql.selectUserInfoSql('commodity_num', 111, cid=88,
                                       duration_time=60)
        m.assert_called_once_with(
            'SELECT SUM(num) FROM xs_user_commodity WHERE uid=%s AND cid=%s AND duration_time=%s',
            params=(111, 88, 60), default=0)

    def test_none_result_coerced_to_zero(self):
        """查询返回 None 应最终归零"""
        with patch.object(MySQLConnection, 'execute_query_first', return_value=None):
            self.assertEqual(conMysql.selectUserInfoSql('wealth', 111), 0)

    def test_unknown_account_type_returns_zero(self):
        """未知 accountType 应返回 0 且不触发查询"""
        with patch.object(MySQLConnection, 'execute_query_first') as m:
            self.assertEqual(conMysql.selectUserInfoSql('not_exists', 111), 0)
        m.assert_not_called()


class TestUpdateAndDelete(unittest.TestCase):
    """更新 / 删除方法"""

    def test_update_money(self):
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.updateMoneySql(111, 500)
        m.assert_called_once_with(
            'UPDATE xs_user_money SET star_coin=%s WHERE uid=%s',
            params=(500, 111))

    def test_update_wealth(self):
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.updateWealthSql(111, 1000, pre_wealth=900)
        m.assert_called_once_with(
            'UPDATE xs_user_wealth SET wealth=%s, pre_wealth=%s WHERE uid=%s',
            params=(1000, 900, 111))

    def test_update_charm(self):
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.updateCharmSql(111, 66)
        m.assert_called_once_with(
            'UPDATE xs_user_charm SET charm=%s WHERE uid=%s',
            params=(66, 111))

    def test_delete_user_commodity(self):
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.deleteUserAccountSql('user_commodity', 111)
        m.assert_called_once_with(
            'DELETE FROM xs_user_commodity WHERE uid=%s', params=(111,))

    def test_delete_user_work_reward_with_wid(self):
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.deleteUserAccountSql('user_work_reward', 111, wid=9)
        m.assert_called_once_with(
            'DELETE FROM xs_user_work_reward WHERE uid=%s AND wid=%s',
            params=(111, 9))

    def test_delete_unknown_noop(self):
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.deleteUserAccountSql('not_exists', 111)
        m.assert_not_called()

    def test_update_singer_worth(self):
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.updateSingerWorth(111, worth=300)
        m.assert_called_once_with(
            'UPDATE xs_audition_singer SET worth=%s WHERE uid=%s',
            params=(300, 111))


class TestInsertCommodity(unittest.TestCase):
    """insertXsUserCommodity 默认有效期"""

    def test_default_period_end_about_one_hour(self):
        """period_end 缺省时应约为 now+3600"""
        before = time.time() + 3600
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.insertXsUserCommodity(111, 88, 5)
        after = time.time() + 3600
        params = m.call_args[1]['params']
        self.assertEqual(params[:3], (111, 88, 5))
        # period_end 为 int(time.time()+3600) 的截断值，允许 1 秒容差
        self.assertTrue(before - 1 <= params[3] <= after)

    def test_explicit_period_end(self):
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.insertXsUserCommodity(111, 88, 5, period_end=12345)
        m.assert_called_once_with(
            'INSERT INTO xs_user_commodity (uid, cid, num, period_end) VALUES(%s, %s, %s, %s)',
            params=(111, 88, 5, 12345))


class TestProducerSinger(unittest.TestCase):
    """制作人/歌手关系操作"""

    def test_delete_producer_singer_two_statements(self):
        """清除关系应按顺序执行 UPDATE 与 DELETE 两条语句"""
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.deleteProducerSinger(111)
        self.assertEqual(m.call_count, 2)
        self.assertEqual(m.call_args_list, [
            call('UPDATE xs_audition_singer SET producer_uid=0 WHERE uid=%s',
                 params=(111,)),
            call('DELETE FROM xs_audition_relation WHERE singer_uid=%s',
                 params=(111,)),
        ])

    def test_select_producer_singer_sums_counts(self):
        """签约歌手数应为两条 COUNT 之和（None 按 0 计）"""
        with patch.object(MySQLConnection, 'execute_query_first',
                          side_effect=[2, None]) as m:
            res = conMysql.selectProducerSinger(222)
        self.assertEqual(res, 2)
        self.assertEqual(m.call_count, 2)


if __name__ == '__main__':
    unittest.main()
