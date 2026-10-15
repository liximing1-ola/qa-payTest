# coding=utf-8
"""
common/mysql_base.py 单元测试（MySQL 连接管理基类）

全部 mock pymysql / config，可在无数据库环境下直接运行：
    python -m pytest tests/test_mysql_base.py -v
"""
import unittest
from unittest.mock import MagicMock, patch

from common.mysql_base import MySQLConnection


class TestGetConnection(unittest.TestCase):
    """get_connection 单例 + 自动重连"""

    def setUp(self):
        """每个测试前重置类级别状态"""
        MySQLConnection._connection = None
        MySQLConnection._cursor = None

    @patch('common.mysql_base.pymysql.connect')
    @patch.object(MySQLConnection, '_get_db_config',
                  return_value={'host': '127.0.0.1', 'port': 3306, 'user': 'root',
                                'password': '', 'database': 'test', 'charset': 'utf8'})
    def test_creates_connection_when_none(self, mock_cfg, mock_connect):
        """无连接时应创建新连接并 ping"""
        mock_conn = MagicMock()
        mock_conn.open = True
        mock_connect.return_value = mock_conn

        result = MySQLConnection.get_connection()

        mock_connect.assert_called_once_with(**mock_cfg(), autocommit=False)
        mock_conn.ping.assert_called_once_with(reconnect=True)
        self.assertIs(result, mock_conn)

    @patch('common.mysql_base.pymysql.connect')
    @patch.object(MySQLConnection, '_get_db_config',
                  return_value={'host': '127.0.0.1'})
    def test_reconnects_when_connection_closed(self, mock_cfg, mock_connect):
        """连接已关闭时应重新创建"""
        old_conn = MagicMock()
        old_conn.open = False
        MySQLConnection._connection = old_conn

        new_conn = MagicMock()
        new_conn.open = True
        mock_connect.return_value = new_conn

        result = MySQLConnection.get_connection()
        self.assertIs(result, new_conn)
        mock_connect.assert_called_once()

    @patch('common.mysql_base.pymysql.connect')
    @patch.object(MySQLConnection, '_get_db_config',
                  return_value={'host': '127.0.0.1'})
    def test_singleton_reuses_connection(self, mock_cfg, mock_connect):
        """已有有效连接时应复用，不重新创建"""
        existing = MagicMock()
        existing.open = True
        MySQLConnection._connection = existing

        result = MySQLConnection.get_connection()
        self.assertIs(result, existing)
        mock_connect.assert_not_called()


class TestGetCursor(unittest.TestCase):
    """get_cursor 单例游标复用 vs 字典游标新建"""

    def setUp(self):
        MySQLConnection._connection = None
        MySQLConnection._cursor = None

    @patch.object(MySQLConnection, 'get_connection')
    def test_singleton_cursor_reuse(self, mock_get_conn):
        """非字典游标应单例复用"""
        mock_conn = MagicMock()
        mock_conn.open = True
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        MySQLConnection._connection = mock_conn  # 设置 _connection 供 get_cursor 检查

        cur1 = MySQLConnection.get_cursor(dict_cursor=False)
        cur2 = MySQLConnection.get_cursor(dict_cursor=False)

        # 第一次创建，第二次复用
        self.assertIs(cur1, mock_cursor)
        self.assertIs(cur2, mock_cursor)

    @patch.object(MySQLConnection, 'get_connection')
    def test_dict_cursor_creates_new(self, mock_get_conn):
        """字典游标应每次新建"""
        mock_conn = MagicMock()
        mock_dict_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_dict_cursor
        mock_get_conn.return_value = mock_conn

        cur1 = MySQLConnection.get_cursor(dict_cursor=True)
        cur2 = MySQLConnection.get_cursor(dict_cursor=True)

        self.assertIs(cur1, mock_dict_cursor)
        self.assertIs(cur2, mock_dict_cursor)
        # 字典游标调用两次 cursor()
        self.assertEqual(mock_conn.cursor.call_count, 2)


class TestCursorContextManager(unittest.TestCase):
    """cursor 上下文管理器正确关闭游标"""

    def setUp(self):
        MySQLConnection._connection = None
        MySQLConnection._cursor = None

    @patch.object(MySQLConnection, 'get_connection')
    def test_cursor_context_closes_on_exit(self, mock_get_conn):
        """退出上下文后游标应被关闭"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        with MySQLConnection.cursor(dict_cursor=False) as cur:
            cur.execute('SELECT 1')

        mock_cursor.close.assert_called_once()

    @patch.object(MySQLConnection, 'get_connection')
    def test_cursor_context_closes_on_exception(self, mock_get_conn):
        """上下文内抛异常时游标也应被关闭"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        with self.assertRaises(RuntimeError):
            with MySQLConnection.cursor():
                raise RuntimeError('boom')

        mock_cursor.close.assert_called_once()

    @patch.object(MySQLConnection, 'get_connection')
    def test_cursor_dict_mode(self, mock_get_conn):
        """dict_cursor=True 时应使用 DictCursor"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn

        with MySQLConnection.cursor(dict_cursor=True):
            pass

        from pymysql import cursors
        mock_conn.cursor.assert_called_with(cursor=cursors.DictCursor)


class TestExecuteQuery(unittest.TestCase):
    """execute_query 正常/异常分支"""

    def setUp(self):
        MySQLConnection._connection = None
        MySQLConnection._cursor = None

    @patch.object(MySQLConnection, 'get_cursor')
    def test_normal_query(self, mock_get_cursor):
        """正常查询应返回 fetchone 结果"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (42,)
        mock_get_cursor.return_value = mock_cursor

        result = MySQLConnection.execute_query('SELECT 1')
        self.assertEqual(result, (42,))
        mock_cursor.execute.assert_called_once_with('SELECT 1', None)

    @patch.object(MySQLConnection, 'get_cursor')
    def test_query_with_params(self, mock_get_cursor):
        """带参数的查询应透传参数"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_get_cursor.return_value = mock_cursor

        MySQLConnection.execute_query('SELECT * FROM t WHERE uid=%s', (100,))
        mock_cursor.execute.assert_called_once_with('SELECT * FROM t WHERE uid=%s', (100,))

    @patch.object(MySQLConnection, 'get_cursor')
    def test_query_exception_returns_none(self, mock_get_cursor):
        """查询异常时应返回 None"""
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception('db error')
        mock_get_cursor.return_value = mock_cursor

        result = MySQLConnection.execute_query('BAD SQL')
        self.assertIsNone(result)


class TestExecuteWrite(unittest.TestCase):
    """execute_write 正常/异常分支"""

    def setUp(self):
        MySQLConnection._connection = None
        MySQLConnection._cursor = None

    @patch.object(MySQLConnection, 'get_cursor')
    @patch.object(MySQLConnection, 'get_connection')
    def test_normal_write(self, mock_get_conn, mock_get_cursor):
        """正常写入应 commit 并返回 True"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_get_cursor.return_value = mock_cursor

        result = MySQLConnection.execute_write('UPDATE t SET a=1')
        self.assertTrue(result)
        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()

    @patch.object(MySQLConnection, 'get_cursor')
    @patch.object(MySQLConnection, 'get_connection')
    def test_write_exception_rollback(self, mock_get_conn, mock_get_cursor):
        """写入异常时应 rollback 并返回 False"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception('write error')
        mock_get_conn.return_value = mock_conn
        mock_get_cursor.return_value = mock_cursor

        result = MySQLConnection.execute_write('BAD SQL')
        self.assertFalse(result)
        mock_conn.rollback.assert_called_once()


class TestExecuteQueryFirst(unittest.TestCase):
    """execute_query_first 返回第一行第一列"""

    def setUp(self):
        MySQLConnection._connection = None
        MySQLConnection._cursor = None

    @patch.object(MySQLConnection, 'execute_query', return_value=(99,))
    def test_returns_first_column(self, mock_query):
        """有结果时应返回第一列"""
        result = MySQLConnection.execute_query_first('SELECT count(*)')
        self.assertEqual(result, 99)

    @patch.object(MySQLConnection, 'execute_query', return_value=None)
    def test_returns_default_on_none(self, mock_query):
        """无结果时应返回默认值"""
        result = MySQLConnection.execute_query_first('SELECT count(*)', default=0)
        self.assertEqual(result, 0)

    @patch.object(MySQLConnection, 'execute_query', return_value=None)
    def test_custom_default(self, mock_query):
        """自定义默认值应生效"""
        result = MySQLConnection.execute_query_first('SELECT x', default='N/A')
        self.assertEqual(result, 'N/A')


class TestBusinessMethods(unittest.TestCase):
    """公共业务方法的 SQL 拼接验证"""

    def setUp(self):
        MySQLConnection._connection = None
        MySQLConnection._cursor = None

    @patch.object(MySQLConnection, 'execute_write')
    def test_clear_user_money(self, mock_write):
        """clear_user_money 应对每个 uid 执行一次清空"""
        MySQLConnection.clear_user_money(1, 2, 3)
        self.assertEqual(mock_write.call_count, 3)
        # 验证第一次调用参数
        first_call = mock_write.call_args_list[0]
        self.assertIn('UPDATE xs_user_money', first_call[0][0])
        self.assertEqual(first_call[1]['params'], (1,))

    @patch.object(MySQLConnection, 'execute_write')
    def test_set_user_money(self, mock_write):
        """set_user_money 应拼接所有金额字段"""
        MySQLConnection.set_user_money(uid=100, money=50, money_cash=30)
        mock_write.assert_called_once()
        sql = mock_write.call_args[0][0]
        self.assertIn('UPDATE xs_user_money', sql)
        self.assertIn('money=%s', sql)
        params = mock_write.call_args[1]['params']
        self.assertEqual(params[-1], 100)  # uid 在最后

    @patch.object(MySQLConnection, 'execute_write')
    def test_reset_user_popularity(self, mock_write):
        """reset_user_popularity 应设置 popularity=0"""
        MySQLConnection.reset_user_popularity(uid=42)
        mock_write.assert_called_once()
        self.assertIn('popularity=0', mock_write.call_args[0][0])
        self.assertEqual(mock_write.call_args[1]['params'], (42,))

    @patch.object(MySQLConnection, 'execute_write')
    def test_insert_user_commodity(self, mock_write):
        """insert_user_commodity 应拼接 uid/cid/num/state"""
        MySQLConnection.insert_user_commodity(uid=1, cid=5, num=3, state=1)
        mock_write.assert_called_once()
        self.assertIn('INSERT INTO xs_user_commodity', mock_write.call_args[0][0])
        self.assertEqual(mock_write.call_args[1]['params'], (1, 5, 3, 1))

    @patch.object(MySQLConnection, 'execute_write')
    def test_update_user_bigarea(self, mock_write):
        """update_user_bigarea 应支持多 uid IN 查询"""
        MySQLConnection.update_user_bigarea(1, 2, 3, bigarea_id=5)
        mock_write.assert_called_once()
        sql = mock_write.call_args[0][0]
        self.assertIn('IN (%s,%s,%s)', sql)
        params = mock_write.call_args[1]['params']
        self.assertEqual(params, (5, 1, 2, 3))

    @patch.object(MySQLConnection, 'execute_write')
    def test_update_user_language(self, mock_write):
        """update_user_language 应拼接 language 和 area_code"""
        MySQLConnection.update_user_language(10, 20, language='en', area_code='US')
        mock_write.assert_called_once()
        sql = mock_write.call_args[0][0]
        self.assertIn('language=%s', sql)
        self.assertIn('IN (%s,%s)', sql)
        params = mock_write.call_args[1]['params']
        self.assertEqual(params, ('en', 'US', 10, 20))

    @patch.object(MySQLConnection, 'execute_query_first', return_value=88)
    def test_query_user_popularity(self, mock_qf):
        """query_user_popularity 应返回人气值"""
        result = MySQLConnection.query_user_popularity(uid=42)
        self.assertEqual(result, 88)
        mock_qf.assert_called_once()

    @patch.object(MySQLConnection, 'execute_query')
    def test_query_greedy_prize(self, mock_query):
        """query_greedy_prize 应返回开奖数据"""
        mock_query.return_value = (5, 100)
        result = MySQLConnection.query_greedy_prize(uid=1, round_id=2)
        self.assertEqual(result, (5, 100))

    @patch.object(MySQLConnection, 'execute_write')
    def test_update_xs_gift_status(self, mock_write):
        """_update_xs_gift_status 应拼接 IN 占位符"""
        MySQLConnection._update_xs_gift_status((10, 20, 30))
        mock_write.assert_called_once()
        sql = mock_write.call_args[0][0]
        self.assertIn('IN (%s,%s,%s)', sql)
        self.assertEqual(mock_write.call_args[1]['params'], (10, 20, 30))


if __name__ == '__main__':
    unittest.main()
