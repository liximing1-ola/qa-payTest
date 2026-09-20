# coding=utf-8
"""
caseSlp/base.py 单元测试（SlpCase 数据载体 / run_case 执行模板 / 域分发器）

全程 mock 数据库与请求，可在无后端环境下直接运行：
    python -m pytest tests/test_slp_base.py -v
"""
import unittest
from dataclasses import FrozenInstanceError
from unittest.mock import Mock, call, patch

from caseSlp import base as slp_base
from caseSlp.base import SlpCase, SlpTestBase
from caseSlp.config import payUid, pay_url


class _DummySlpTest(SlpTestBase):
    """仅用于承载被测方法的空测试类（不定义任何 test_ 方法）"""


def _make_testcase():
    """绕过 unittest.TestCase.__init__ 构造实例，仅用于调用被测方法"""
    return _DummySlpTest.__new__(_DummySlpTest)


class TestSlpCase(unittest.TestCase):
    """SlpCase 数据载体的默认值与不可变性"""

    def test_field_defaults(self):
        """未显式赋值的字段应取默认值"""
        case = SlpCase(des='场景')
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
        """SlpCase 为 frozen dataclass，禁止运行期修改"""
        case = SlpCase(des='场景')
        with self.assertRaises(FrozenInstanceError):
            case.des = '修改'

    def test_mutable_defaults_are_independent(self):
        """可变默认值由 factory 提供，实例间互不共享"""
        first = SlpCase(des='a')
        second = SlpCase(des='b')
        first.setup.append('x')
        first.data['k'] = 1
        self.assertEqual(second.setup, [])
        self.assertEqual(second.data, {})


class TestRunCaseFlow(unittest.TestCase):
    """run_case 七步模板：执行顺序、ctx 传递、SLP 域请求参数与结果记录"""

    def setUp(self):
        self.tc = _make_testcase()

    def test_full_flow_order_and_deferred_values(self):
        """完整场景应按 准备->查询->请求->断言->等待->校验->记录 顺序执行，
        且请求走 pay_url + token_name='slp'"""
        events = []
        fake_table = {}
        body = {'success': 1, 'msg': 'ok'}

        def _query():
            events.append('query')
            return 7

        case = SlpCase(
            des='完整场景',
            prepare=lambda _t: events.append('prepare'),
            setup=[{'action': 'update_money', 'params': {'uid': 1}}],
            queries=[('q', _query)],
            data={'money': lambda ctx: ctx['q'] + 1,
                  'cls_ok': lambda ctx: ctx['cls'] is _DummySlpTest},
            checks=[{'field': 'single_money', 'expected': lambda ctx: ctx['q'] * 2}],
            success=1, msg='ok', post_wait=0.01,
        )
        with patch('caseSlp.base.UserMoneyOperations') as m_money, \
                patch('caseSlp.base.encodeData',
                      side_effect=lambda **kw: events.append(('data', kw)) or kw), \
                patch('caseSlp.base.post_request_session',
                      side_effect=lambda url, d, token_name=None:
                      events.append(('req', url, d, token_name)) or {'code': 200, 'body': body}), \
                patch('caseSlp.base.assert_code') as m_code, \
                patch('caseSlp.base.assert_body') as m_body, \
                patch('caseSlp.base.time.sleep', side_effect=lambda s: events.append(('sleep', s))), \
                patch.object(_DummySlpTest, '_validate_db_state',
                             side_effect=lambda checks, ctx=None: events.append(('check', checks))), \
                patch.dict('caseSlp.base.REPORT_TABLES', {'case_list': fake_table}):
            m_money.update.side_effect = lambda **kw: events.append('setup')
            self.tc.run_case(case)

        self.assertEqual(len(events), 7)
        self.assertEqual(events[0], 'prepare')
        self.assertEqual(events[1], 'setup')
        self.assertEqual(events[2], 'query')
        self.assertEqual(events[3], ('data', {'money': 8, 'cls_ok': True}))
        self.assertEqual(events[4], ('req', pay_url, {'money': 8, 'cls_ok': True}, 'slp'))
        self.assertEqual(events[5], ('sleep', 0.01))
        self.assertEqual(events[6], ('check', [{'field': 'single_money', 'expected': 14}]))
        m_code.assert_called_once_with(200)
        self.assertEqual(m_body.call_args_list,
                         [call(body, 'success', 1), call(body, 'msg', 'ok')])
        self.assertEqual(fake_table, {'完整场景': slp_base.result})

    def test_msg_none_skips_msg_assertion(self):
        """msg 为 None 时只断言 success 不检查文案"""
        body = {'success': 1}
        case = SlpCase(des='无msg场景', data={'a': 1}, msg=None)
        with patch.object(_DummySlpTest, '_prepare_test_data') as m_prep, \
                patch('caseSlp.base.encodeData', return_value={'a': 1}), \
                patch('caseSlp.base.post_request_session',
                      return_value={'code': 200, 'body': body}), \
                patch('caseSlp.base.assert_code'), \
                patch('caseSlp.base.assert_body') as m_body, \
                patch.dict('caseSlp.base.REPORT_TABLES', {'case_list': {}}):
            self.tc.run_case(case)
        m_prep.assert_not_called()
        m_body.assert_called_once_with(body, 'success', 1)

    def test_optional_steps_skipped_when_absent(self):
        """setup/queries/checks 为空且 post_wait 为 0 时不应产生额外调用"""
        case = SlpCase(des='最小场景')
        with patch.object(_DummySlpTest, '_prepare_test_data') as m_prep, \
                patch('caseSlp.base.encodeData', return_value={}) as m_enc, \
                patch('caseSlp.base.post_request_session',
                      return_value={'code': 200, 'body': {}}) as m_req, \
                patch('caseSlp.base.assert_code'), \
                patch('caseSlp.base.assert_body'), \
                patch('caseSlp.base.time.sleep') as m_sleep, \
                patch.object(_DummySlpTest, '_validate_db_state') as m_check, \
                patch.dict('caseSlp.base.REPORT_TABLES', {'case_list': {}}):
            self.tc.run_case(case)
        m_prep.assert_not_called()
        m_enc.assert_called_once_with()
        m_req.assert_called_once_with(pay_url, {}, token_name='slp')
        m_sleep.assert_not_called()
        m_check.assert_not_called()

    def test_report_routing_to_case_list_b(self):
        """report='case_list_b' 时应写入第二张报告表"""
        fake_b = {}
        case = SlpCase(des='B表场景', report='case_list_b')
        with patch('caseSlp.base.encodeData', return_value={}), \
                patch('caseSlp.base.post_request_session',
                      return_value={'code': 200, 'body': {}}), \
                patch('caseSlp.base.assert_code'), \
                patch('caseSlp.base.assert_body'), \
                patch.dict('caseSlp.base.REPORT_TABLES',
                           {'case_list': {}, 'case_list_b': fake_b}):
            self.tc.run_case(case)
        self.assertEqual(fake_b, {'B表场景': slp_base.result})


class TestPrepareDispatcher(unittest.TestCase):
    """_prepare_test_data 步骤分发器"""

    def setUp(self):
        self.tc = _make_testcase()

    def test_update_money(self):
        with patch('caseSlp.base.UserMoneyOperations') as m:
            self.tc._prepare_test_data(
                [{'action': 'update_money', 'params': {'uid': 1, 'money': 5}}])
        m.update.assert_called_once_with(uid=1, money=5)

    def test_clear_user_money(self):
        with patch('caseSlp.base.mysql') as m:
            self.tc._prepare_test_data(
                [{'action': 'clear_user_money', 'uids': [1, 2, 3]}])
        m.updateUserMoneyClearSql.assert_called_once_with(1, 2, 3)

    def test_delete_user_account_uses_params(self):
        with patch('caseSlp.base.mysql') as m:
            self.tc._prepare_test_data([{
                'action': 'delete_user_account',
                'params': {'table': 'user_title_new', 'uid': 9},
            }])
        m.deleteUserAccountSql.assert_called_once_with('user_title_new', 9)

    def test_delete_commodity(self):
        with patch('caseSlp.base.mysql') as m:
            self.tc._prepare_test_data([{'action': 'delete_commodity', 'uid': 9}])
        m.deleteUserAccountSql.assert_called_once_with('user_commodity', 9)

    def test_insert_commodity_default_uid(self):
        with patch('caseSlp.base.UserCommodityOperations') as m:
            self.tc._prepare_test_data(
                [{'action': 'insert_commodity', 'params': {'cid': 329, 'num': 1}}])
        m.insert.assert_called_once_with(payUid, cid=329, num=1)

    def test_insert_commodity_explicit_uid(self):
        with patch('caseSlp.base.UserCommodityOperations') as m:
            self.tc._prepare_test_data(
                [{'action': 'insert_commodity', 'params': {'uid': 9, 'cid': 329, 'num': 1}}])
        m.insert.assert_called_once_with(9, cid=329, num=1)

    def test_update_user_god(self):
        with patch('caseSlp.base.mysql') as m:
            self.tc._prepare_test_data(
                [{'action': 'update_user_god', 'params': {'uid': 9, 'god': 1}}])
        m.updateUserGodSql.assert_called_once_with(9, 1)

    def test_update_user_title(self):
        with patch('caseSlp.base.mysql') as m:
            self.tc._prepare_test_data(
                [{'action': 'update_user_title', 'params': {'uid': 9, 'level': 70}}])
        m.updateUserInfoSql.assert_called_once_with('user_title_new', 9, level=70)

    def test_check_user_broker(self):
        with patch('caseSlp.base.mysql') as m, patch('caseSlp.base.assert_equal') as m_eq:
            m.checkUserBroker.return_value = True
            self.tc._prepare_test_data(
                [{'action': 'check_user_broker', 'uid': 9, 'expected': True}])
        m.checkUserBroker.assert_called_once_with(9)
        m_eq.assert_called_once_with(True, True)

    def test_check_rid_type(self):
        with patch('caseSlp.base.mysql') as m, patch('caseSlp.base.assert_equal') as m_eq:
            m.checkRidFactoryType.return_value = 'business-friend'
            self.tc._prepare_test_data(
                [{'action': 'check_rid_type', 'rid': 88, 'expected': 'business-friend'}])
        m.checkRidFactoryType.assert_called_once_with(88)
        m_eq.assert_called_once_with('business-friend', 'business-friend')

    def test_unknown_action_noop(self):
        """未知 action 不应触发任何数据库操作"""
        with patch('caseSlp.base.mysql') as m_mysql, \
                patch('caseSlp.base.UserMoneyOperations') as m_money, \
                patch('caseSlp.base.UserCommodityOperations') as m_commodity:
            self.tc._prepare_test_data([{'action': 'not_exists'}])
        self.assertEqual(m_mysql.mock_calls, [])
        self.assertEqual(m_money.mock_calls, [])
        self.assertEqual(m_commodity.mock_calls, [])


class TestValidateDispatcher(unittest.TestCase):
    """_validate_db_state 校验分发器"""

    def setUp(self):
        self.tc = _make_testcase()

    def test_basic_equal(self):
        with patch('caseSlp.base.mysql') as m_mysql, patch('caseSlp.base.assert_equal') as m_eq:
            m_mysql.selectUserInfoSql.return_value = 5
            self.tc._validate_db_state([{'field': 'sum_money', 'uid': 123, 'expected': 5}])
        m_mysql.selectUserInfoSql.assert_called_once_with('sum_money', 123)
        m_eq.assert_called_once_with(5, 5)

    def test_default_uid_is_pay_uid(self):
        with patch('caseSlp.base.mysql') as m_mysql, patch('caseSlp.base.assert_equal'):
            m_mysql.selectUserInfoSql.return_value = 0
            self.tc._validate_db_state([{'field': 'sum_money', 'expected': 0}])
        m_mysql.selectUserInfoSql.assert_called_once_with('sum_money', payUid)

    def test_money_type_and_cid_passed_as_kwargs(self):
        with patch('caseSlp.base.mysql') as m_mysql, patch('caseSlp.base.assert_equal'):
            m_mysql.selectUserInfoSql.return_value = 1
            self.tc._validate_db_state([{
                'field': 'single_money', 'uid': 1, 'expected': 1,
                'money_type': 'money_cash', 'cid': 9,
            }])
        m_mysql.selectUserInfoSql.assert_called_once_with(
            'single_money', 1, money_type='money_cash', cid=9)

    def test_payuid_kwarg_for_relation_query(self):
        with patch('caseSlp.base.mysql') as m_mysql, patch('caseSlp.base.assert_equal'):
            m_mysql.selectUserInfoSql.return_value = 2
            self.tc._validate_db_state([{
                'field': 'relation_id', 'uid': 9, 'cid': 2, 'payuid': 8, 'expected': 2,
            }])
        m_mysql.selectUserInfoSql.assert_called_once_with(
            'relation_id', 9, cid=2, payuid=8)

    def test_extra_kwargs_merged(self):
        with patch('caseSlp.base.mysql') as m_mysql, patch('caseSlp.base.assert_equal'):
            m_mysql.selectUserInfoSql.return_value = 1
            self.tc._validate_db_state([{
                'field': 'x', 'uid': 1, 'expected': 1, 'kwargs': {'q': 2},
            }])
        m_mysql.selectUserInfoSql.assert_called_once_with('x', 1, q=2)

    def test_assert_func_custom_check(self):
        """assert_func 应收到 ctx 且不触发表查询"""
        custom = Mock()
        ctx = {'k': 1}
        with patch('caseSlp.base.mysql') as m_mysql:
            self.tc._validate_db_state([{'assert_func': custom}], ctx)
        custom.assert_called_once_with(ctx)
        m_mysql.selectUserInfoSql.assert_not_called()
