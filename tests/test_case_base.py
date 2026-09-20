# coding=utf-8
"""
case/base.py 单元测试（PayCase 数据载体 / run_case 执行模板 / 步骤分发器）

全程 mock 数据库与请求，可在无后端环境下直接运行：
    python -m pytest tests/test_case_base.py -v
"""
import unittest
from dataclasses import FrozenInstanceError
from unittest.mock import Mock, call, patch

from case import base as case_base
from case.base import PayCase, PayTestBase, _resolve
from common.Config import config


class _DummyPayTest(PayTestBase):
    """仅用于承载被测方法的空测试类（不定义任何 test_ 方法）"""


def _make_testcase():
    """绕过 unittest.TestCase.__init__ 构造实例，仅用于调用被测方法"""
    return _DummyPayTest.__new__(_DummyPayTest)


class TestPayCase(unittest.TestCase):
    """PayCase 数据载体的默认值与不可变性"""

    def test_field_defaults(self):
        """未显式赋值的字段应取默认值"""
        case = PayCase(des='场景')
        self.assertEqual(case.des, '场景')
        self.assertEqual(case.setup, [])
        self.assertEqual(case.data, {})
        self.assertEqual(case.checks, [])
        self.assertEqual(case.success, 1)
        self.assertIsNone(case.msg)
        self.assertEqual(case.post_wait, 0)
        self.assertEqual(case.queries, [])
        self.assertIsNone(case.prepare)
        self.assertEqual(case.report, 'case_list')

    def test_frozen_instance(self):
        """PayCase 为 frozen dataclass，禁止运行期修改"""
        case = PayCase(des='场景')
        with self.assertRaises(FrozenInstanceError):
            case.des = '修改'

    def test_mutable_defaults_are_independent(self):
        """可变默认值由 factory 提供，实例间互不共享"""
        first = PayCase(des='a')
        second = PayCase(des='b')
        first.setup.append('x')
        first.data['k'] = 1
        self.assertEqual(second.setup, [])
        self.assertEqual(second.data, {})


class TestResolveHelpers(unittest.TestCase):
    """_resolve / _resolve_check 延迟求值"""

    def test_resolve_callable_with_ctx(self):
        """callable 值应以 ctx 求值"""
        self.assertEqual(_resolve(lambda ctx: ctx['q'] + 1, {'q': 7}), 8)

    def test_resolve_plain_value(self):
        """非 callable 值原样返回"""
        self.assertEqual(_resolve(7, {}), 7)
        self.assertEqual(_resolve('abc', {}), 'abc')

    def test_resolve_check_resolves_callable_expected(self):
        """expected 为 callable 时应返回解析后的新字典，且不修改原字典"""
        check = {'field': 'bean', 'expected': lambda ctx: ctx['q'] * 2}
        resolved = PayTestBase._resolve_check(check, {'q': 5})
        self.assertEqual(resolved, {'field': 'bean', 'expected': 10})
        self.assertEqual(check['field'], 'bean')
        self.assertTrue(callable(check['expected']))

    def test_resolve_check_returns_original_when_plain(self):
        """expected 非 callable 时原样返回同一对象"""
        check = {'field': 'bean', 'expected': 5}
        self.assertIs(PayTestBase._resolve_check(check, {}), check)


class TestRunCaseFlow(unittest.TestCase):
    """run_case 七步模板：执行顺序、ctx 传递与结果记录"""

    def setUp(self):
        self.tc = _make_testcase()

    def test_full_flow_order_and_deferred_values(self):
        """完整场景应按 准备->查询->请求->断言->等待->校验->记录 顺序执行"""
        events = []
        fake_table = {}
        body = {'success': 1, 'msg': 'ok'}

        def _query():
            events.append('query')
            return 7

        case = PayCase(
            des='完整场景',
            prepare=lambda _t: events.append('prepare'),
            setup=[{'action': 'update_money', 'params': {'uid': 1}}],
            queries=[('q', _query)],
            data={'money': lambda ctx: ctx['q'] + 1,
                  'cls_ok': lambda ctx: ctx['cls'] is _DummyPayTest},
            checks=[{'field': 'bean', 'expected': lambda ctx: ctx['q'] * 2}],
            success=1, msg='ok', post_wait=0.01,
        )
        with patch('case.base.UserMoneyOperations') as m_money, \
                patch('case.base.encodeData',
                      side_effect=lambda **kw: events.append(('data', kw)) or kw), \
                patch('case.base.post_request_session',
                      side_effect=lambda url, d: events.append(('req', url, d))
                      or {'code': 200, 'body': body}), \
                patch('case.base.assert_code') as m_code, \
                patch('case.base.assert_body') as m_body, \
                patch('case.base.time.sleep', side_effect=lambda s: events.append(('sleep', s))), \
                patch.object(_DummyPayTest, '_validate_db_state',
                             side_effect=lambda checks: events.append(('check', checks))), \
                patch.dict('case.base.REPORT_TABLES', {'case_list': fake_table}):
            m_money.update.side_effect = lambda **kw: events.append('setup')
            self.tc.run_case(case)

        self.assertEqual(len(events), 7)
        self.assertEqual(events[0], 'prepare')
        self.assertEqual(events[1], 'setup')
        self.assertEqual(events[2], 'query')
        self.assertEqual(events[3], ('data', {'money': 8, 'cls_ok': True}))
        self.assertEqual(events[4], ('req', config.pay_url, {'money': 8, 'cls_ok': True}))
        self.assertEqual(events[5], ('sleep', 0.01))
        self.assertEqual(events[6], ('check', [{'field': 'bean', 'expected': 14}]))
        m_code.assert_called_once_with(200)
        self.assertEqual(m_body.call_args_list,
                         [call(body, 'success', 1), call(body, 'msg', 'ok')])
        self.assertEqual(fake_table, {'完整场景': case_base.result})

    def test_msg_none_skips_msg_assertion(self):
        """msg 为 None 时只断言 success 不检查文案"""
        body = {'success': 1}
        case = PayCase(des='无msg场景', data={'a': 1}, msg=None)
        with patch.object(_DummyPayTest, '_prepare_test_data') as m_prep, \
                patch('case.base.encodeData', return_value={'a': 1}), \
                patch('case.base.post_request_session',
                      return_value={'code': 200, 'body': body}), \
                patch('case.base.assert_code'), \
                patch('case.base.assert_body') as m_body, \
                patch.dict('case.base.REPORT_TABLES', {'case_list': {}}):
            self.tc.run_case(case)
        m_prep.assert_not_called()
        m_body.assert_called_once_with(body, 'success', 1)

    def test_optional_steps_skipped_when_absent(self):
        """setup/queries/checks 为空且 post_wait 为 0 时不应产生额外调用"""
        case = PayCase(des='最小场景')
        with patch.object(_DummyPayTest, '_prepare_test_data') as m_prep, \
                patch('case.base.encodeData', return_value={}) as m_enc, \
                patch('case.base.post_request_session',
                      return_value={'code': 200, 'body': {}}) as m_req, \
                patch('case.base.assert_code'), \
                patch('case.base.assert_body'), \
                patch('case.base.time.sleep') as m_sleep, \
                patch.object(_DummyPayTest, '_validate_db_state') as m_check, \
                patch.dict('case.base.REPORT_TABLES', {'case_list': {}}):
            self.tc.run_case(case)
        m_prep.assert_not_called()
        m_enc.assert_called_once_with()
        m_req.assert_called_once_with(config.pay_url, {})
        m_sleep.assert_not_called()
        m_check.assert_not_called()


class TestPrepareTestDataDispatcher(unittest.TestCase):
    """_prepare_test_data 步骤分发器"""

    def setUp(self):
        self.tc = _make_testcase()

    def test_update_money(self):
        with patch('case.base.UserMoneyOperations') as m:
            self.tc._prepare_test_data(
                [{'action': 'update_money', 'params': {'uid': 1, 'money': 5}}])
        m.update.assert_called_once_with(uid=1, money=5)

    def test_clear_user_money_with_uid_params(self):
        with patch('case.base.mysql') as m:
            self.tc._prepare_test_data(
                [{'action': 'clear_user_money', 'params': {'uid1': 1, 'uid2': 2}}])
        m.updateUserMoneyClearSql.assert_called_once_with(1, 2)

    def test_clear_user_money_with_uids_list(self):
        with patch('case.base.mysql') as m:
            self.tc._prepare_test_data([{'action': 'clear_user_money', 'uids': [1, 2, 3]}])
        m.updateUserMoneyClearSql.assert_called_once_with(1, 2, 3)

    def test_clear_user_data_defaults(self):
        with patch('case.base.mysql') as m:
            self.tc._prepare_test_data([{'action': 'clear_user_data'}])
        m.updateUserMoneyClearSql.assert_called_once_with(config.payUid, config.rewardUid)

    def test_delete_account_uses_params(self):
        with patch('case.base.mysql') as m:
            self.tc._prepare_test_data([{
                'action': 'delete_user_account',
                'params': {'table': 'user_commodity', 'uid': 9},
            }])
        m.deleteUserAccountSql.assert_called_once_with('user_commodity', 9)

    def test_delete_commodity(self):
        with patch('case.base.mysql') as m:
            self.tc._prepare_test_data([{'action': 'delete_commodity', 'uid': 9}])
        m.deleteUserAccountSql.assert_called_once_with('user_commodity', 9)

    def test_insert_commodity_default_uid(self):
        with patch('case.base.UserCommodityOperations') as m:
            self.tc._prepare_test_data(
                [{'action': 'insert_commodity', 'params': {'cid': 5, 'num': 2}}])
        m.insert.assert_called_once_with(config.payUid, cid=5, num=2)

    def test_insert_commodity_explicit_uid(self):
        with patch('case.base.UserCommodityOperations') as m:
            self.tc._prepare_test_data(
                [{'action': 'insert_commodity', 'params': {'uid': 9, 'cid': 5, 'num': 2}}])
        m.insert.assert_called_once_with(9, cid=5, num=2)

    def test_insert_user_box_default_uid(self):
        with patch('case.base.mysql') as m:
            self.tc._prepare_test_data(
                [{'action': 'insert_user_box', 'params': {'gift_cid': 8}}])
        m.insertXsUserBox.assert_called_once_with(config.payUid, gift_cid=8)

    def test_check_user_broker_params_form(self):
        with patch('case.base.mysql') as m:
            self.tc._prepare_test_data(
                [{'action': 'check_user_broker', 'params': {'uid': 9, 'bid': 5}}])
        m.checkUserBroker.assert_called_once_with(uid=9, bid=5)

    def test_check_user_broker_uid_bid_form(self):
        with patch('case.base.mysql') as m:
            self.tc._prepare_test_data([{'action': 'check_user_broker', 'uid': 9, 'bid': 5}])
        m.checkUserBroker.assert_called_once_with(9, bid=5)

    def test_check_broker_rate(self):
        with patch('case.base.mysql') as m:
            self.tc._prepare_test_data([{
                'action': 'check_broker_rate',
                'params': {'uid': 9, 'creater': 5, 'rate': 50},
            }])
        m.checkBrokerUserRate.assert_called_once_with(uid=9, creater=5, rate=50)

    def test_unknown_action_noop(self):
        """未知 action 不应触发任何数据库操作"""
        with patch('case.base.mysql') as m_mysql, \
                patch('case.base.UserMoneyOperations') as m_money, \
                patch('case.base.UserCommodityOperations') as m_commodity:
            self.tc._prepare_test_data([{'action': 'not_exists'}])
        self.assertEqual(m_mysql.mock_calls, [])
        self.assertEqual(m_money.mock_calls, [])
        self.assertEqual(m_commodity.mock_calls, [])


class TestValidateDbStateDispatcher(unittest.TestCase):
    """_validate_db_state 校验分发器"""

    def setUp(self):
        self.tc = _make_testcase()

    def test_basic_equal(self):
        with patch('case.base.mysql') as m_mysql, patch('case.base.assert_equal') as m_eq:
            m_mysql.selectUserInfoSql.return_value = 5
            self.tc._validate_db_state([{'field': 'bean', 'uid': 123, 'expected': 5}])
        m_mysql.selectUserInfoSql.assert_called_once_with('bean', 123)
        m_eq.assert_called_once_with(5, 5)

    def test_default_uid_is_pay_uid(self):
        with patch('case.base.mysql') as m_mysql, patch('case.base.assert_equal'):
            m_mysql.selectUserInfoSql.return_value = 0
            self.tc._validate_db_state([{'field': 'bean', 'expected': 0}])
        m_mysql.selectUserInfoSql.assert_called_once_with('bean', config.payUid)

    def test_money_type_and_cid_passed_as_kwargs(self):
        with patch('case.base.mysql') as m_mysql, patch('case.base.assert_equal'):
            m_mysql.selectUserInfoSql.return_value = 1
            self.tc._validate_db_state([{
                'field': 'single_money', 'uid': 1, 'expected': 1,
                'money_type': 'money_cash', 'cid': 9,
            }])
        m_mysql.selectUserInfoSql.assert_called_once_with(
            'single_money', 1, money_type='money_cash', cid=9)

    def test_extra_kwargs_merged(self):
        with patch('case.base.mysql') as m_mysql, patch('case.base.assert_equal'):
            m_mysql.selectUserInfoSql.return_value = 1
            self.tc._validate_db_state([{
                'field': 'x', 'uid': 1, 'expected': 1, 'kwargs': {'q': 2},
            }])
        m_mysql.selectUserInfoSql.assert_called_once_with('x', 1, q=2)

    def test_min_value_uses_assert_len(self):
        with patch('case.base.mysql') as m_mysql, \
                patch('case.base.assert_len') as m_len, \
                patch('case.base.assert_equal') as m_eq:
            m_mysql.selectUserInfoSql.return_value = 5
            self.tc._validate_db_state(
                [{'field': 'popularity', 'uid': 1, 'min_value': 3}])
        m_len.assert_called_once_with(5, 3)
        m_eq.assert_not_called()

    def test_assert_func_custom_check(self):
        custom = Mock()
        with patch('case.base.mysql') as m_mysql:
            m_mysql.selectUserInfoSql.return_value = 7
            self.tc._validate_db_state([{
                'field': 'x', 'uid': 1, 'expected': 9, 'assert_func': custom,
            }])
        custom.assert_called_once_with(7, 9)
