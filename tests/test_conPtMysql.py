"""
common/conPtMysql.py 单元测试（SQL 映射分发 / 参数组装）

全部 mock MySQLConnection 底层执行方法，可在无数据库环境下直接运行：
    python -m pytest tests/test_conPtMysql.py -v
"""
import unittest
from unittest.mock import patch

from common.con_pt_mysql import ConMysql, MySQLConnection
from common.Config import config


class TestPtSelectUserInfoSql(unittest.TestCase):
    """conPtMysql.selectUserInfoSql"""

    def test_query_sql_map(self):
        """QUERY_SQL_MAP 中的类型应使用 uid 参数化"""
        with patch.object(MySQLConnection, 'execute_query', return_value=(100,)) as m:
            res = ConMysql.select_user_info_sql('sum_money', uid=111)
        self.assertEqual(res, 100)
        m.assert_called_once_with(ConMysql.QUERY_SQL_MAP['sum_money'], params=(111,))

    def test_query_sql_map_empty_result(self):
        """查询结果为空应返回 0"""
        with patch.object(MySQLConnection, 'execute_query', return_value=None):
            res = ConMysql.select_user_info_sql('sum_money', uid=111)
        self.assertEqual(res, 0)

    def test_query_sql_map_zero_value(self):
        """查询结果为 0 应返回 0"""
        with patch.object(MySQLConnection, 'execute_query', return_value=(0,)):
            res = ConMysql.select_user_info_sql('sum_money', uid=111)
        self.assertEqual(res, 0)

    def test_single_money_valid_column(self):
        """合法 money_type 应拼接列名"""
        with patch.object(MySQLConnection, 'execute_query', return_value=(50,)) as m:
            res = ConMysql.select_user_info_sql('single_money', uid=111, money_type='money_cash')
        self.assertEqual(res, 50)
        m.assert_called_once()
        sql = m.call_args[0][0]
        self.assertIn('money_cash', sql)

    def test_single_money_invalid_column(self):
        """非法 money_type 应抛 ValueError"""
        with patch.object(MySQLConnection, 'execute_query') as m:
            with self.assertRaises(ValueError):
                ConMysql.select_user_info_sql('single_money', uid=111, money_type='bad_col')
        m.assert_not_called()

    def test_single_money_no_result(self):
        """single_money 无结果应返回 None"""
        with patch.object(MySQLConnection, 'execute_query', return_value=None):
            res = ConMysql.select_user_info_sql('single_money', uid=111, money_type='money')
        self.assertIsNone(res)

    def test_default_uid_from_config(self):
        """uid 为 None 时应使用 config.oversea_payUid"""
        with patch.object(MySQLConnection, 'execute_query', return_value=(1,)) as m:
            ConMysql.select_user_info_sql('sum_money')
        m.assert_called_once()
        params = m.call_args[1]['params']
        self.assertEqual(params, (config.oversea_payUid,))

    def test_unknown_account_type(self):
        """未知 accountType 应返回 None"""
        with patch.object(MySQLConnection, 'execute_query') as m:
            res = ConMysql.select_user_info_sql('not_exists', uid=111)
        self.assertIsNone(res)
        m.assert_not_called()


class TestPtDeleteUserAccountSql(unittest.TestCase):
    """conPtMysql.deleteUserAccountSql"""

    def test_known_table(self):
        with patch.object(MySQLConnection, 'execute_write') as m:
            ConMysql.delete_user_account_sql('user_commodity', 111)
        m.assert_called_once_with(ConMysql.DELETE_SQL_MAP['user_commodity'], params=(111,))

    def test_unknown_table_noop(self):
        with patch.object(MySQLConnection, 'execute_write') as m:
            ConMysql.delete_user_account_sql('not_exists', 111)
        m.assert_not_called()


class TestPtUpdateWrappers(unittest.TestCase):
    """conPtMysql 更新方法包装器"""

    def test_update_user_rid_info(self):
        with patch.object(MySQLConnection, 'update_room_property') as m:
            ConMysql.update_user_rid_info_sql('union', 123, area='ja')
        m.assert_called_once_with('union', 123, 'ja')

    def test_update_user_big_area(self):
        with patch.object(MySQLConnection, 'update_user_bigarea') as m:
            ConMysql.update_user_big_area(1, 2, 3, bigarea_id=5)
        m.assert_called_once_with(1, 2, 3, bigarea_id=5)

    def test_update_user_language(self):
        with patch.object(MySQLConnection, 'update_user_language') as m:
            ConMysql.update_user_language(1, language='en', area_code='US')
        m.assert_called_once_with(1, language='en', area_code='US')

    def test_update_user_money_clear(self):
        with patch.object(MySQLConnection, 'clear_user_money') as m:
            ConMysql.update_user_money_clear_sql(1, 2)
        m.assert_called_once_with(1, 2)

    def test_update_extend_money_clear(self):
        """updateUserextendMoneyClearSql 应对每个 uid 执行"""
        with patch.object(MySQLConnection, 'execute_write') as m:
            ConMysql.update_user_extend_money_clear_sql(1, 2)
        self.assertEqual(m.call_count, 2)

    def test_update_money(self):
        with patch.object(MySQLConnection, 'set_user_money') as m:
            ConMysql.update_money_sql(1, money=10, gold_coin=5)
        m.assert_called_once_with(1, money=10, money_cash=0, money_cash_b=0,
                                  money_b=0, gold_coin=5, money_debts=0)

    def test_update_popularity(self):
        with patch.object(MySQLConnection, 'reset_user_popularity') as m:
            ConMysql.update_xs_user_popularity(1)
        m.assert_called_once_with(1)

    def test_update_pay_room_money(self):
        with patch.object(MySQLConnection, 'reset_user_pay_room_money') as m:
            ConMysql.update_xs_user_profile_pay_room_money(1)
        m.assert_called_once_with(1)


class TestPtInsertAndQuery(unittest.TestCase):
    """conPtMysql 插入与查询方法"""

    def test_insert_commodity(self):
        with patch.object(MySQLConnection, 'insert_user_commodity') as m:
            ConMysql.insert_xs_user_commodity(1, 5, 10, state=1)
        m.assert_called_once_with(1, 5, 10, 1)

    def test_insert_box(self):
        with patch.object(MySQLConnection, 'insert_user_box') as m:
            ConMysql.insert_xs_user_box(1, gift_cid=100, box_type='silver')
        m.assert_called_once_with(1, 100, 'silver')

    def test_check_gift_config(self):
        with patch.object(MySQLConnection, '_update_xs_gift_status') as m:
            ConMysql.check_xs_gift_config()
        m.assert_called_once()

    def test_select_greedy_prize_with_result(self):
        with patch.object(MySQLConnection, 'query_greedy_prize', return_value=(1, 100)):
            res = ConMysql.select_greedy_prize(1, 5)
        self.assertEqual(res, (1, 100))

    def test_select_greedy_prize_no_result(self):
        with patch.object(MySQLConnection, 'query_greedy_prize', return_value=None):
            res = ConMysql.select_greedy_prize(1, 5)
        self.assertEqual(res, (0, 0))

    def test_select_user_chatroom(self):
        with patch.object(MySQLConnection, 'query_user_chatroom', return_value=42):
            res = ConMysql.select_user_chatroom('union', bigarea_id=2)
        self.assertEqual(res, 42)

    def test_sql_popularity(self):
        with patch.object(MySQLConnection, 'query_user_popularity', return_value=99):
            res = ConMysql.sql_xs_user_popularity(1)
        self.assertEqual(res, 99)

    def test_sql_pay_room_money(self):
        with patch.object(MySQLConnection, 'query_user_pay_room_money', return_value=50):
            res = ConMysql.sql_xs_user_profile_pay_room_money(1)
        self.assertEqual(res, 50)


if __name__ == '__main__':
    unittest.main()
