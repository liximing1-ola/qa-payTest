# coding=utf-8
"""
caseStarify/base.py 单元测试（StarifyCase 数据载体 / run_case 执行模板 / 域分发器）

全程 mock 数据库与请求，可在无后端环境下直接运行：
    python -m pytest tests/test_starify_base.py -v
"""
import unittest
from dataclasses import FrozenInstanceError
from unittest.mock import patch

from caseStarify import base as starify_base
from caseStarify.base import StarifyCase, StarifyTestBase


class _DummyStarifyTest(StarifyTestBase):
    """仅用于承载被测方法的空测试类（不定义任何 test_ 方法）"""


def _make_testcase():
    """绕过 unittest.TestCase.__init__ 构造实例，仅用于调用被测方法"""
    return _DummyStarifyTest.__new__(_DummyStarifyTest)


class TestStarifyCase(unittest.TestCase):
    """StarifyCase 数据载体的默认值与不可变性"""

    def test_field_defaults(self):
        """未显式赋值的字段应取默认值"""
        case = StarifyCase(des='场景')
        self.assertEqual(case.des, '场景')
        self.assertEqual(case.setup, [])
        self.assertEqual(case.data, {})
        self.assertTrue(case.success)
        self.assertIsNone(case.msg)
        self.assertEqual(case.checks, [])
        self.assertEqual(case.report, 'case_list')

    def test_frozen_instance(self):
        """StarifyCase 为 frozen dataclass，禁止运行期修改"""
        case = StarifyCase(des='场景')
        with self.assertRaises(FrozenInstanceError):
            case.des = '修改'

    def test_mutable_defaults_are_independent(self):
        """可变默认值由 factory 提供，实例间互不共享"""
        first = StarifyCase(des='a')
        second = StarifyCase(des='b')
        first.setup.append('x')
        first.data['k'] = 1
        first.checks.append(lambda: None)
        self.assertEqual(second.setup, [])
        self.assertEqual(second.data, {})
        self.assertEqual(second.checks, [])


class TestRunCaseFlow(unittest.TestCase):
    """run_case 七步模板：执行顺序、请求参数、断言模式与结果记录"""

    def setUp(self):
        self.tc = _make_testcase()

    def test_full_flow_order(self):
        """完整场景应按 准备->请求->断言->校验->记录 顺序执行，
        且请求走 post_starify(case.data)"""
        events = []
        fake_table = {}
        body = {'success': True}
        data = {'op_type': 'room', 'params': '{}'}

        def _check():
            events.append('check')

        case = StarifyCase(
            des='完整场景',
            setup=[{'action': 'update_money', 'params': {'uid': 1, 'money': 100}}],
            data=data,
            checks=[_check],
        )
        with patch('caseStarify.base.conMysql') as m_mysql, \
                patch('caseStarify.base.post_starify',
                      side_effect=lambda d: events.append(('req', d))
                      or {'code': 200, 'body': body}), \
                patch('caseStarify.base.assert_code') as m_code, \
                patch('caseStarify.base.assert_body') as m_body, \
                patch.dict('caseStarify.base.REPORT_TABLES', {'case_list': fake_table}):
            m_mysql.updateMoneySql.side_effect = lambda uid, money: events.append('setup')
            self.tc.run_case(case)

        self.assertEqual(events, ['setup', ('req', data), 'check'])
        m_code.assert_called_once_with(200)
        m_body.assert_called_once_with(body, 'success', True)
        self.assertEqual(fake_table, {'完整场景': starify_base.result})

    def test_success_none_asserts_msg_only(self):
        """success 为 None 时仅断言 msg 不检查 success 字段"""
        body = {'msg': '支付或打赏失败'}
        case = StarifyCase(des='失败场景', data={'a': 1}, success=None,
                           msg='支付或打赏失败')
        with patch('caseStarify.base.post_starify',
                   return_value={'code': 200, 'body': body}), \
                patch('caseStarify.base.assert_code'), \
                patch('caseStarify.base.assert_body') as m_body, \
                patch.dict('caseStarify.base.REPORT_TABLES', {'case_list': {}}):
            self.tc.run_case(case)
        m_body.assert_called_once_with(body, 'msg', '支付或打赏失败')

    def test_success_false_asserted(self):
        """success 为 False 时应断言 success 失败"""
        body = {'success': False}
        case = StarifyCase(des='失败场景', success=False)
        with patch('caseStarify.base.post_starify',
                   return_value={'code': 200, 'body': body}), \
                patch('caseStarify.base.assert_code'), \
                patch('caseStarify.base.assert_body') as m_body, \
                patch.dict('caseStarify.base.REPORT_TABLES', {'case_list': {}}):
            self.tc.run_case(case)
        m_body.assert_called_once_with(body, 'success', False)

    def test_optional_steps_skipped_when_absent(self):
        """setup/checks 为空时不应产生额外调用"""
        case = StarifyCase(des='最小场景')
        with patch.object(_DummyStarifyTest, '_prepare_test_data') as m_prep, \
                patch('caseStarify.base.post_starify',
                      return_value={'code': 200, 'body': {}}) as m_req, \
                patch('caseStarify.base.assert_code'), \
                patch('caseStarify.base.assert_body'), \
                patch.dict('caseStarify.base.REPORT_TABLES', {'case_list': {}}):
            self.tc.run_case(case)
        m_prep.assert_not_called()
        m_req.assert_called_once_with({})

    def test_report_routing_to_case_list_b(self):
        """report='case_list_b' 时应写入第二张报告表"""
        fake_b = {}
        case = StarifyCase(des='B表场景', report='case_list_b')
        with patch('caseStarify.base.post_starify',
                   return_value={'code': 200, 'body': {}}), \
                patch('caseStarify.base.assert_code'), \
                patch('caseStarify.base.assert_body'), \
                patch.dict('caseStarify.base.REPORT_TABLES',
                           {'case_list': {}, 'case_list_b': fake_b}):
            self.tc.run_case(case)
        self.assertEqual(fake_b, {'B表场景': starify_base.result})


class TestPrepareDispatcher(unittest.TestCase):
    """_prepare_test_data 步骤分发器"""

    def setUp(self):
        self.tc = _make_testcase()

    def test_update_money(self):
        with patch('caseStarify.base.conMysql') as m:
            self.tc._prepare_test_data(
                [{'action': 'update_money', 'params': {'uid': 1, 'money': 5}}])
        m.updateMoneySql.assert_called_once_with(1, 5)

    def test_update_wealth(self):
        with patch('caseStarify.base.conMysql') as m:
            self.tc._prepare_test_data(
                [{'action': 'update_wealth', 'params': {'uid': 1, 'wealth': 100}}])
        m.updateWealthSql.assert_called_once_with(1, 100)

    def test_update_charm(self):
        with patch('caseStarify.base.conMysql') as m:
            self.tc._prepare_test_data(
                [{'action': 'update_charm', 'params': {'uid': 1, 'charm': 8}}])
        m.updateCharmSql.assert_called_once_with(1, 8)

    def test_delete_user_account_with_wid(self):
        with patch('caseStarify.base.conMysql') as m:
            self.tc._prepare_test_data([{
                'action': 'delete_user_account',
                'params': {'table': 'user_work_reward', 'uid': 9, 'wid': 9926},
            }])
        m.deleteUserAccountSql.assert_called_once_with('user_work_reward', 9, 9926)

    def test_delete_user_account_default_wid(self):
        with patch('caseStarify.base.conMysql') as m:
            self.tc._prepare_test_data([{
                'action': 'delete_user_account',
                'params': {'table': 'user_commodity', 'uid': 9},
            }])
        m.deleteUserAccountSql.assert_called_once_with('user_commodity', 9, 0)

    def test_insert_commodity(self):
        with patch('caseStarify.base.conMysql') as m:
            self.tc._prepare_test_data(
                [{'action': 'insert_commodity',
                  'params': {'uid': 9, 'cid': 8, 'num': 2}}])
        m.insertXsUserCommodity.assert_called_once_with(9, 8, 2)

    def test_delete_producer_singer(self):
        with patch('caseStarify.base.conMysql') as m:
            self.tc._prepare_test_data(
                [{'action': 'delete_producer_singer', 'params': {'singer_uid': 9}}])
        m.deleteProducerSinger.assert_called_once_with(9)

    def test_update_singer_worth(self):
        with patch('caseStarify.base.conMysql') as m:
            self.tc._prepare_test_data(
                [{'action': 'update_singer_worth',
                  'params': {'singer_uid': 9, 'worth': 100}}])
        m.updateSingerWorth.assert_called_once_with(9, 100)

    def test_unknown_action_noop(self):
        """未知 action 不应触发任何数据库操作"""
        with patch('caseStarify.base.conMysql') as m:
            self.tc._prepare_test_data([{'action': 'not_exists'}])
        self.assertEqual(m.mock_calls, [])
