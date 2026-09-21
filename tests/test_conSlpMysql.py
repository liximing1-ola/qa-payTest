# coding=utf-8
"""
common/conSlpMysql.py 单元测试（SQL 映射分发 / 参数组装 / 专用查询）

全部 mock MySQLConnection 底层执行方法，可在无数据库环境下直接运行：
    python -m pytest tests/test_conSlpMysql.py -v
"""
import unittest
from unittest.mock import Mock, patch

from common.conSlpMysql import MySQLConnection, conMysql


class TestSelectUserInfoSql(unittest.TestCase):
    """selectUserInfoSql 分发与参数组装"""

    def test_simple_map(self):
        """简单映射应使用 uid 参数化并默认返回 0"""
        with patch.object(MySQLConnection, 'execute_query_first', return_value=7) as m:
            res = conMysql.selectUserInfoSql('bean', '111')
        self.assertEqual(res, 7)
        m.assert_called_once_with(conMysql.SELECT_SIMPLE_MAP['bean'],
                                  params=('111',), default=0)

    def test_union_missing_raises(self):
        """union/vip 查无房间时应抛 EnvironmentError"""
        with patch.object(MySQLConnection, 'execute_query_first', return_value=None):
            with self.assertRaises(EnvironmentError):
                conMysql.selectUserInfoSql('union')

    def test_union_found(self):
        """union 命中时按无参调用并透传 rid"""
        with patch.object(MySQLConnection, 'execute_query_first', return_value=200001) as m:
            res = conMysql.selectUserInfoSql('union')
        self.assertEqual(res, 200001)
        m.assert_called_once_with(conMysql.SELECT_SIMPLE_MAP['union'], default=None)

    def test_single_money_whitelist(self):
        """single_money 白名单列应 format 进 SQL 并对 uid 参数化"""
        with patch.object(MySQLConnection, 'execute_query_first', return_value=99) as m:
            res = conMysql.selectUserInfoSql('single_money', '111',
                                              money_type='money_cash')
        self.assertEqual(res, 99)
        m.assert_called_once_with('SELECT money_cash FROM xs_user_money WHERE uid=%s',
                                  params=('111',), default=0)

    def test_single_money_rejects_non_whitelist(self):
        """白名单外的 money_type 应抛 ValueError 且不执行查询（防注入）"""
        with patch.object(MySQLConnection, 'execute_query_first') as m:
            with self.assertRaises(ValueError):
                conMysql.selectUserInfoSql('single_money', '111',
                                           money_type='money_cash; DROP TABLE x')
        m.assert_not_called()

    def test_with_cid_map(self):
        """num_commodity 参数顺序应为 (cid, uid)"""
        with patch.object(MySQLConnection, 'execute_query_first', return_value=3) as m:
            res = conMysql.selectUserInfoSql('num_commodity', '111', cid=263)
        self.assertEqual(res, 3)
        m.assert_called_once_with(conMysql.SELECT_WITH_PARAM_MAP['num_commodity'],
                                  params=(263, '111'), default=0)

    def test_level_map_default_none(self):
        """level 映射的默认值应为 None"""
        with patch.object(MySQLConnection, 'execute_query_first', return_value=None) as m:
            conMysql.selectUserInfoSql('level', '111')
        m.assert_called_once_with(conMysql.SELECT_WITH_PARAM_MAP['level'],
                                  params=('111',), default=None)

    def test_relation_id_params(self):
        """relation_id 参数顺序应为 (payuid, uid, cid)"""
        with patch.object(MySQLConnection, 'execute_query_first', return_value=0) as m:
            conMysql.selectUserInfoSql('relation_id', '111', cid=7, payuid='222')
        m.assert_called_once_with(conMysql.SELECT_RELATION_ID_SQL,
                                  params=('222', '111', 7), default=0)

    def test_relation_config_dict_row(self):
        """relation_config 应按 description 组装字典行"""
        m_cur = Mock()
        m_cur.description = [('id',), ('name',), ('money_value',),
                             ('break_money',), ('upgrade_money',)]
        m_cur.fetchall.return_value = [(2, 'CP', 520000, 99900, 520000)]
        with patch.object(MySQLConnection, 'get_cursor', return_value=m_cur):
            res = conMysql.selectUserInfoSql('relation_config', 1)
        self.assertEqual(res, {'id': 2, 'name': 'CP', 'money_value': 520000,
                               'break_money': 99900, 'upgrade_money': 520000})
        m_cur.execute.assert_called_once_with(conMysql.SELECT_COMPLEX_SQL, (1,))

    def test_relation_config_empty_returns_none(self):
        """relation_config 查无数据应返回 None"""
        m_cur = Mock()
        m_cur.description = [('id',)]
        m_cur.fetchall.return_value = []
        with patch.object(MySQLConnection, 'get_cursor', return_value=m_cur):
            self.assertIsNone(conMysql.selectUserInfoSql('relation_config', 1))

    def test_pay_change_parses_reason_dict(self):
        """pay_change 应 literal_eval reason 字符串并按 money_type 取值"""
        m_cur = Mock()
        m_cur.fetchone.return_value = ("{'money_cash': 30}",)
        with patch.object(MySQLConnection, 'get_cursor', return_value=m_cur):
            res = conMysql.selectUserInfoSql('pay_change', '111',
                                             money_type='money_cash')
        self.assertEqual(res, 30)
        # 无匹配键时返回 0
        m_cur.fetchone.return_value = ("{'money_cash': 30}",)
        with patch.object(MySQLConnection, 'get_cursor', return_value=m_cur):
            self.assertEqual(conMysql.selectUserInfoSql('pay_change', '111'), 0)

    def test_pay_change_no_row_returns_zero(self):
        """pay_change 查无流水应返回 0"""
        m_cur = Mock()
        m_cur.fetchone.return_value = None
        with patch.object(MySQLConnection, 'get_cursor', return_value=m_cur):
            self.assertEqual(conMysql.selectUserInfoSql('pay_change', '111'), 0)

    def test_unknown_account_type_returns_none(self):
        """未知 accountType 应返回 None 且不触发查询"""
        with patch.object(MySQLConnection, 'execute_query_first') as m:
            self.assertIsNone(conMysql.selectUserInfoSql('not_exists', '111'))
        m.assert_not_called()


class TestDeleteAndUpdate(unittest.TestCase):
    """删除 / 更新方法分发"""

    def test_delete_table_map(self):
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.deleteUserAccountSql('user_commodity', '111')
        m.assert_called_once_with(conMysql.DELETE_SQL_MAP['user_commodity'],
                                  params=('111',))

    def test_delete_unknown_noop(self):
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.deleteUserAccountSql('not_exists', '111')
        m.assert_not_called()

    def test_update_money_forwards_all_fields(self):
        """updateMoneySql 应透传全部字段（含 money_debts）"""
        with patch.object(MySQLConnection, 'set_user_money') as m:
            conMysql.updateMoneySql('111', money=100, money_cash=200,
                                    money_cash_b=300, money_b=400,
                                    gold_coin=500, money_debts=600)
        m.assert_called_once_with('111', money=100, money_cash=200,
                                  money_cash_b=300, money_b=400,
                                  gold_coin=500, money_debts=600)

    def test_clear_money_splat(self):
        with patch.object(MySQLConnection, 'clear_user_money') as m:
            conMysql.updateUserMoneyClearSql('111', '222')
        m.assert_called_once_with('111', '222')

    def test_insert_commodity(self):
        with patch.object(MySQLConnection, 'insert_user_commodity') as m:
            conMysql.insertXsUserCommodity('111', 263, 5, state=1)
        m.assert_called_once_with('111', 263, 5, 1)

    def test_update_user_title_growth_mapping(self):
        """updateUserInfoSql：level=40 应映射 growth=250000 并写入五元参数"""
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.updateUserInfoSql('user_title_new', '111', level=40)
        sql, kwargs = m.call_args[0][0], m.call_args[1]
        self.assertIn('growth=%s', sql)
        params = kwargs['params']
        self.assertEqual(params[0], 40)
        self.assertEqual(params[1], 250000)
        self.assertEqual(params[2], 250000)
        self.assertEqual(params[4], '111')

    def test_update_user_info_unknown_noop(self):
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.updateUserInfoSql('not_exists', '111')
        m.assert_not_called()


class TestDedicatedQueries(unittest.TestCase):
    """专用查询与透传方法"""

    def test_check_user_broker(self):
        """checkUserBroker：有记录 True / 无记录 False"""
        with patch.object(MySQLConnection, 'execute_query_first',
                          return_value=5):
            self.assertTrue(conMysql.checkUserBroker('111'))
        with patch.object(MySQLConnection, 'execute_query_first',
                          return_value=None):
            self.assertFalse(conMysql.checkUserBroker('111'))

    def test_check_rid_factory_type(self):
        with patch.object(MySQLConnection, 'execute_query_first', return_value='party') as m:
            res = conMysql.checkRidFactoryType(999)
        self.assertEqual(res, 'party')
        m.assert_called_once_with(
            'SELECT room_factory_type FROM xs_chatroom WHERE rid=%s',
            params=(999,), default=None)

    def test_update_user_god_sql(self):
        with patch.object(MySQLConnection, 'execute_write') as m:
            conMysql.updateUserGodSql('111', 3)
        m.assert_called_once_with(
            'UPDATE xs_user_settings SET agreement_version=%s WHERE uid=%s',
            params=(3, '111'))

    def test_greedy_prize_forwarding(self):
        with patch.object(MySQLConnection, 'query_greedy_prize',
                          return_value=(100, 50)) as m:
            res = conMysql.select_greedy_prize('111', 5)
        self.assertEqual(res, (100, 50))
        m.assert_called_once_with('111', 5)

    def test_user_chatroom_forwarding(self):
        with patch.object(MySQLConnection, 'query_user_chatroom',
                          return_value=200001) as m:
            res = conMysql.select_user_chatroom('business', bigarea_id=7)
        self.assertEqual(res, 200001)
        m.assert_called_once_with('business', 7)

    def test_select_zx_pay_data(self):
        """selectZxPayData：dict_cursor 游标执行 JSON_EXTRACT 聚合并返回行"""
        m_cur = Mock()
        m_cur.fetchall.return_value = [{'to_uid': 222, 'gid': 88, 'total_num': 4}]
        with patch.object(MySQLConnection, 'get_cursor', return_value=m_cur) as m_gc:
            res = conMysql.selectZxPayData('111')
        self.assertEqual(res, [{'to_uid': 222, 'gid': 88, 'total_num': 4}])
        m_gc.assert_called_once_with(dict_cursor=True)
        m_cur.execute.assert_called_once()

    def test_select_zx_pay_data_error_returns_none(self):
        m_cur = Mock()
        m_cur.execute.side_effect = RuntimeError('boom')
        with patch.object(MySQLConnection, 'get_cursor', return_value=m_cur):
            self.assertIsNone(conMysql.selectZxPayData('111'))


if __name__ == '__main__':
    unittest.main()
