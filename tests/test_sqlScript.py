# coding=utf-8
"""
common/sqlScript.py 单元测试（MySQLClient 执行链 / 事务回滚 / 操作类 SQL 组装）

全部 mock pymysql.connect，可在无数据库环境下直接运行：
    python -m pytest tests/test_sqlScript.py -v
"""
import unittest
from unittest.mock import Mock, patch

from common.Config import config
from common.sqlScript import (
    MySQLClient,
    UserCommodityOperations,
    UserMoneyOperations,
    UserProfileOperations,
)


class _FakeChain:
    """patch pymysql.connect 后的连接/游标链 fixture"""

    def __init__(self):
        self.con = Mock()
        self.cur = Mock()
        self.con.cursor.return_value = self.cur
        self.patcher = patch('common.sqlScript.pymysql.connect',
                             return_value=self.con)

    def __enter__(self):
        self.patcher.start()
        return self

    def __exit__(self, *exc):
        self.patcher.stop()
        return False


class TestExecuteChain(unittest.TestCase):
    """MySQLClient.execute 连接链与事务行为"""

    def test_fetch_one(self):
        with _FakeChain() as f:
            f.cur.fetchone.return_value = (7,)
            res = MySQLClient.execute('SELECT x FROM t WHERE uid=%s', (1,),
                                      fetch_one=True)
        self.assertEqual(res, (7,))
        f.cur.execute.assert_called_once_with('SELECT x FROM t WHERE uid=%s', (1,))

    def test_fetch_all(self):
        with _FakeChain() as f:
            f.cur.fetchall.return_value = [(1,), (2,)]
            res = MySQLClient.execute('SELECT uid FROM t', None, fetch_all=True)
        self.assertEqual(res, [(1,), (2,)])

    def test_write_commits(self):
        """无 fetch 标志的执行应提交事务"""
        with _FakeChain() as f:
            MySQLClient.execute('UPDATE t SET a=1')
        f.con.commit.assert_called_once()
        f.con.rollback.assert_not_called()

    def test_error_rolls_back_and_raises(self):
        """执行异常应回滚并向上抛出"""
        with _FakeChain() as f:
            f.cur.execute.side_effect = RuntimeError('syntax')
            with self.assertRaises(RuntimeError):
                MySQLClient.execute('BAD SQL')
        f.con.rollback.assert_called_once()
        f.con.commit.assert_not_called()

    def test_execute_write_swallows_error(self):
        """execute_write 失败应记日志而不抛出"""
        with patch.object(MySQLClient, 'execute', side_effect=RuntimeError('x')):
            MySQLClient.execute_write('BAD SQL', error_msg='op fail')

    def test_execute_read_first_column(self):
        with patch.object(MySQLClient, 'execute', return_value=(42,)):
            self.assertEqual(MySQLClient.execute_read('SELECT x'), 42)

    def test_execute_read_default_on_empty(self):
        with patch.object(MySQLClient, 'execute', return_value=None):
            self.assertEqual(MySQLClient.execute_read('SELECT x', default=0), 0)

    def test_execute_read_default_on_error(self):
        with patch.object(MySQLClient, 'execute',
                          side_effect=RuntimeError('conn')):
            self.assertIsNone(MySQLClient.execute_read('SELECT x'))


class TestGetConfig(unittest.TestCase):
    """_get_config 环境路由"""

    def test_routes(self):
        cases = {
            'dev': config.database.dev_config,
            'ali': config.database.ali_config,
            'rds': config.database.rds_config,
        }
        for name, expected in cases.items():
            with patch.object(MySQLClient, '_config_name', name):
                self.assertEqual(MySQLClient._get_config(), expected)

    def test_unknown_falls_back_to_dev(self):
        with patch.object(MySQLClient, '_config_name', 'not_exists'):
            self.assertEqual(MySQLClient._get_config(), config.database.dev_config)


class TestUserMoneyOperations(unittest.TestCase):
    """UserMoneyOperations SQL 与参数顺序"""

    def test_update_params_order(self):
        """update 参数顺序应为 (money, money_b, money_cash, money_cash_b, gold_coin, money_debts, uid)"""
        with patch.object(MySQLClient, 'execute_write') as m:
            UserMoneyOperations.update(111, money=10, money_cash=20,
                                       money_cash_b=30, money_b=40,
                                       gold_coin=50, money_debts=60)
        sql = m.call_args[0][0]
        self.assertIn('money=%s', sql)
        self.assertIn('money_debts=%s', sql)
        self.assertIn('LIMIT 1', sql)
        self.assertEqual(m.call_args[1]['params'],
                         (10, 40, 20, 30, 50, 60, 111))

    def test_select_all_sum(self):
        with patch.object(MySQLClient, 'execute_read', return_value=100) as m:
            res = UserMoneyOperations.select_all(111)
        self.assertEqual(res, 100)
        self.assertIn('money+money_b+money_cash_b+money_cash',
                      m.call_args[0][0])
        self.assertEqual(m.call_args[1]['params'], (111,))


class TestUserCommodityOperations(unittest.TestCase):
    """UserCommodityOperations SQL 与参数"""

    def test_check(self):
        with patch.object(MySQLClient, 'execute_read', return_value=3) as m:
            res = UserCommodityOperations.check(111, 55)
        self.assertEqual(res, 3)
        sql, kwargs = m.call_args[0][0], m.call_args[1]
        self.assertIn('WHERE cid=%s AND uid=%s', sql)
        self.assertEqual(kwargs['params'], (55, 111))
        self.assertEqual(kwargs['default'], 0)

    def test_check_all_int_coercion(self):
        """check_all：'7' 应回退为 int 7，None 回退为 0"""
        with patch.object(MySQLClient, 'execute_read', return_value='7'):
            self.assertEqual(UserCommodityOperations.check_all(111), 7)
        with patch.object(MySQLClient, 'execute_read', return_value=None):
            self.assertEqual(UserCommodityOperations.check_all(111), 0)

    def test_get_id(self):
        with patch.object(MySQLClient, 'execute_read', return_value=9) as m:
            res = UserCommodityOperations.get_id(111, 55)
        self.assertEqual(res, 9)
        self.assertEqual(m.call_args[1]['params'], (55, 111))

    def test_insert(self):
        with patch.object(MySQLClient, 'execute_write') as m:
            UserCommodityOperations.insert(111, 55, 5, state=1)
        self.assertIn('INSERT INTO xs_user_commodity', m.call_args[0][0])
        self.assertEqual(m.call_args[1]['params'], (111, 55, 5, 1))

    def test_delete_all(self):
        with patch.object(MySQLClient, 'execute_write') as m:
            UserCommodityOperations.delete_all(111)
        self.assertEqual(m.call_args[0][0],
                         'DELETE FROM xs_user_commodity WHERE uid=%s')
        self.assertEqual(m.call_args[1]['params'], (111,))


class TestGetUids(unittest.TestCase):
    """UserProfileOperations.get_uids 结果组装"""

    def test_rows_to_uid_tuple(self):
        with patch.object(MySQLClient, 'execute',
                          return_value=[(131542081,), (131542082,)]) as m:
            res = UserProfileOperations.get_uids(2)
        self.assertEqual(res, ('131542081', '131542082'))
        sql, kwargs = m.call_args[0][0], m.call_args[1]
        self.assertIn('LIMIT %s', sql)
        self.assertEqual(kwargs['params'], (131542080, 1, 2))
        self.assertTrue(kwargs['fetch_all'])

    def test_empty_result(self):
        with patch.object(MySQLClient, 'execute', return_value=None):
            self.assertEqual(UserProfileOperations.get_uids(2), ())

    def test_error_returns_empty(self):
        with patch.object(MySQLClient, 'execute', side_effect=RuntimeError('x')):
            self.assertEqual(UserProfileOperations.get_uids(2), ())


if __name__ == '__main__':
    unittest.main()
