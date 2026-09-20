# coding=utf-8
"""
common/conMysql.py 单元测试（SQL 映射分发 / 参数组装 / 事务包装）

全部 mock MySQLConnection 底层执行方法，可在无数据库环境下直接运行：
    python -m pytest tests/test_conMysql.py -v
"""
import unittest
from unittest.mock import Mock, call, patch

from common.Config import config
from common.conMysql import MySQLConnection, conMysql


class TestSelectUserInfoSql(unittest.TestCase):
    """selectUserInfoSql 分发与参数组装"""

    def test_simple_map(self):
        """简单映射应使用 uid 参数化并默认返回 0"""
        with patch.object(MySQLConnection, 'execute_query_first', return_value=7) as m:
            res = conMysql.selectUserInfoSql('bean', uid=111)
        self.assertEqual(res, 7)
        m.assert_called_once_with(conMysql.SELECT_SIMPLE_MAP['bean'],
                                  params=(111,), default=0)

    def test_with_cid_map(self):
        """带 cid 的映射参数顺序应为 (cid, uid)"""
        with patch.object(MySQLConnection, 'execute_query_first', return_value=8) as m:
            res = conMysql.selectUserInfoSql('id_commodity', uid=111, cid=55)
        self.assertEqual(res, 8)
        m.assert_called_once_with(conMysql.SELECT_WITH_CID_MAP['id_commodity'],
                                  params=(55, 111), default=0)

    def test_return_none_map(self):
        """返回 None 类映射的默认值应为 None"""
        with patch.object(MySQLConnection, 'execute_query_first', return_value=None) as m:
            conMysql.selectUserInfoSql('level', uid=111)
        m.assert_called_once_with(conMysql.SELECT_RETURN_NONE_MAP['level'],
                                  params=(111,), default=None)

    def test_single_money_parameterized_uid(self):
        """货币列白名单内的查询应拼入列名并对 uid 参数化"""
        with patch.object(MySQLConnection, 'execute_query_first', return_value=99) as m:
            res = conMysql.selectUserInfoSql('single_money', uid=111,
                                             money_type='money_cash_b')
        self.assertEqual(res, 99)
        m.assert_called_once_with('SELECT money_cash_b FROM xs_user_money WHERE uid=%s',
                                  params=(111,), default=None)

    def test_single_money_rejects_non_whitelist_column(self):
        """白名单外的 money_type 应抛 ValueError 且不执行查询（防注入）"""
        with patch.object(MySQLConnection, 'execute_query_first') as m:
            with self.assertRaises(ValueError):
                conMysql.selectUserInfoSql('single_money', uid=111,
                                           money_type='money_cash; DROP TABLE x')
        m.assert_not_called()

    def test_relation_id_handler(self):
        """relation_id 参数应为 (payUid, uid, cid)"""
        with patch.object(MySQLConnection, 'execute_query_first', return_value=0) as m:
            conMysql.selectUserInfoSql('relation_id', uid=111, cid=7)
        m.assert_called_once_with(
            'SELECT id FROM xs_relation_defend WHERE uid=%s AND defend_uid=%s AND relation_id=%s',
            params=(config.payUid, 111, 7), default=0)

    def test_unknown_account_type_returns_none(self):
        """未知 accountType 应返回 None 且不触发查询"""
        with patch.object(MySQLConnection, 'execute_query_first') as m:
            self.assertIsNone(conMysql.selectUserInfoSql('not_exists', uid=111))
        m.assert_not_called()


class TestDeleteUserAccountSql(unittest.TestCase):
    """deleteUserAccountSql 分发"""

    def test_delete_table_map(self):
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.deleteUserAccountSql('user_commodity', 111)
        m.assert_called_once_with(conMysql.DELETE_SQL_MAP['user_commodity'], params=(111,))

    def test_update_style_map(self):
        """历史命名兼容：user_profile 实际为 UPDATE title=0"""
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.deleteUserAccountSql('user_profile', 111)
        m.assert_called_once_with(conMysql.DELETE_UPDATE_MAP['user_profile'], params=(111,))

    def test_unknown_table_noop(self):
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.deleteUserAccountSql('not_exists', 111)
        m.assert_not_called()


class TestUpdateUserInfoSql(unittest.TestCase):
    """updateUserInfoSql 分发与参数构建"""

    def test_broker_user(self):
        """broker_user 参数顺序应为 (bid, uid)"""
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.updateUserInfoSql('broker_user', 111, bid=222)
        m.assert_called_once_with(conMysql.UPDATE_USER_INFO_MAP['broker_user'][0],
                                  params=(222, 111))

    def test_chatroom_uses_live_rid(self):
        """chatroom 参数应为 (uid, live_rid)"""
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.updateUserInfoSql('chatroom', 111)
        m.assert_called_once_with(conMysql.UPDATE_USER_INFO_MAP['chatroom'][0],
                                  params=(111, config.live_role['live_rid']))

    def test_unknown_table_noop(self):
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.updateUserInfoSql('not_exists', 111)
        m.assert_not_called()


class TestSimpleWrappers(unittest.TestCase):
    """简单包装方法透传校验"""

    def test_update_money_forwards_all_fields(self):
        """updateMoneySql 应透传全部字段（含 money_debts）"""
        with patch.object(MySQLConnection, 'set_user_money') as m:
            conMysql.updateMoneySql(1, money=5, money_debts=9)
        m.assert_called_once_with(1, money=5, money_cash=0, money_cash_b=0,
                                  money_b=0, gold_coin=0, money_debts=9)

    def test_delete_user_bean_sql_multiple_uids(self):
        """deleteUserBeanSql 应对每个 uid 各执行一次删除"""
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.deleteUserBeanSql(1, 2)
        self.assertEqual(m.call_args_list, [
            call('DELETE FROM xs_user_money_extend WHERE uid=%s LIMIT 1', params=(1,)),
            call('DELETE FROM xs_user_money_extend WHERE uid=%s LIMIT 1', params=(2,)),
        ])

    def test_insert_bean_sql(self):
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.insertBeanSql(1, 6000, cash=3, cash_lock=4)
        m.assert_called_once_with(
            'INSERT INTO xs_user_money_extend(uid, money_coupon, cash, cash_lock) '
            'VALUES(%s,%s,%s,%s)',
            params=(1, 6000, 3, 4))

    def test_insert_user_box(self):
        with patch.object(MySQLConnection, 'insert_user_box') as m:
            conMysql.insertXsUserBox(1, gift_cid=8)
        m.assert_called_once_with(1, 8, 'copper')

    def test_insert_user_commodity_checks_before_insert(self):
        """insertXsUserCommodity 应先校验物品存在再插入"""
        with patch.object(conMysql, 'checkXsCommodity') as m_check, \
                patch.object(MySQLConnection, 'insert_user_commodity') as m_insert:
            conMysql.insertXsUserCommodity(1, 5, 2, state=1)
        m_check.assert_called_once_with(5)
        m_insert.assert_called_once_with(1, 5, 2, 1)

    def test_check_xs_commodity_exists(self):
        with patch.object(MySQLConnection, 'execute_query_first', return_value='青铜体验券'):
            conMysql.checkXsCommodity(5)  # 存在时不抛异常

    def test_check_xs_commodity_missing_raises(self):
        with patch.object(MySQLConnection, 'execute_query_first', return_value=None):
            with self.assertRaises(Exception):
                conMysql.checkXsCommodity(5)

    def test_update_user_money_clear(self):
        with patch.object(MySQLConnection, 'clear_user_money') as m:
            conMysql.updateUserMoneyClearSql(1, 2, 3)
        m.assert_called_once_with(1, 2, 3)


class TestTransactionalChecks(unittest.TestCase):
    """check* 系列的事务包装逻辑"""

    def _patched_conn(self):
        m_con = Mock()
        m_cur = Mock()
        return m_con, m_cur, (
            patch.object(MySQLConnection, 'get_connection', return_value=m_con),
            patch.object(MySQLConnection, 'get_cursor', return_value=m_cur),
        )

    def test_check_user_broker_insert_when_missing(self):
        """工会关系不存在时应 INSERT 并提交"""
        m_con, m_cur, (p_con, p_cur) = self._patched_conn()
        m_cur.fetchone.return_value = None
        with p_con, p_cur:
            conMysql.checkUserBroker(111, bid=222)
        insert_calls = [c for c in m_cur.execute.call_args_list
                        if 'INSERT INTO xs_broker_user' in c[0][0]]
        self.assertEqual(len(insert_calls), 1)
        self.assertEqual(insert_calls[0][0][1], (222, 111))
        m_con.commit.assert_called_once_with()
        m_con.rollback.assert_not_called()

    def test_check_user_broker_update_when_exists(self):
        """工会关系已存在时应 UPDATE 并提交"""
        m_con, m_cur, (p_con, p_cur) = self._patched_conn()
        m_cur.fetchone.return_value = (7,)
        with p_con, p_cur:
            conMysql.checkUserBroker(111, bid=222)
        update_calls = [c for c in m_cur.execute.call_args_list
                        if 'UPDATE xs_broker_user' in c[0][0]]
        self.assertEqual(len(update_calls), 1)
        self.assertEqual(update_calls[0][0][1], (111, 222, 7))
        m_con.commit.assert_called_once_with()

    def test_check_broker_user_rate_insert_when_missing(self):
        """分成比例不存在时应 INSERT (uid, creater, rate)"""
        m_con, m_cur, (p_con, p_cur) = self._patched_conn()
        m_cur.fetchone.return_value = None
        with p_con, p_cur:
            conMysql.checkBrokerUserRate(1, 2)
        insert_calls = [c for c in m_cur.execute.call_args_list
                        if 'INSERT INTO config.bbc_broker_user_rate' in c[0][0]]
        self.assertEqual(len(insert_calls), 1)
        self.assertEqual(insert_calls[0][0][1], (1, 2, 100))

    def test_transaction_rollback_on_error(self):
        """写操作异常时应回滚且不向上抛出"""
        m_con, m_cur, (p_con, p_cur) = self._patched_conn()
        m_cur.execute.side_effect = RuntimeError('boom')
        with p_con, p_cur:
            conMysql.checkUserBroker(111, bid=222)
        m_con.rollback.assert_called_once_with()
        m_con.commit.assert_not_called()
