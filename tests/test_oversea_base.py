# coding=utf-8
"""
caseOversea/base.py 单元测试（PayScene 参数载体 / run_scene 执行模板）

基于现行实现的行为刻画（characterization）测试：重构前后行为必须一致；
全程 mock 数据库与请求，可在无后端环境下直接运行：
    python -m pytest tests/test_oversea_base.py -v
"""
import unittest
from dataclasses import FrozenInstanceError
from unittest.mock import call, patch

from caseOversea.base import (AREA_RID, RECEIVER_BROKER, RECEIVER_NORMAL,
                              OverseaAreaTestBase, PayScene)
from common.Config import config
from common.Consts import result

# 任意占位房间号（模拟 setUpClass 查询结果）
AREA_RID_VALUE = 987654321


class _DummyOverseaTest(OverseaAreaTestBase):
    """仅用于承载被测方法的空测试类（不定义任何 test_ 方法）"""


class TestPaySceneContract(unittest.TestCase):
    """PayScene 数据载体的默认值与不可变性"""

    def test_field_defaults(self):
        """未显式赋值的字段应取默认值"""
        scene = PayScene(des='场景')
        self.assertEqual(scene.receiver, RECEIVER_NORMAL)
        self.assertEqual(scene.pay_type, 'package')
        self.assertFalse(scene.is_box)
        self.assertIsNone(scene.rid)
        self.assertEqual(scene.payer_money, 700)
        self.assertFalse(scene.payer_box_extra)
        self.assertFalse(scene.clear_extend)
        self.assertFalse(scene.clear_all)
        self.assertEqual(scene.success, 1)
        self.assertIsNone(scene.msg)
        self.assertEqual(scene.payer_expect, 100)
        self.assertEqual(scene.income_account, 'money_cash_personal')
        self.assertIsNone(scene.income_money_type)
        self.assertEqual(scene.income_expect, 0)
        self.assertFalse(scene.income_min)
        self.assertFalse(scene.check_pay_change)
        self.assertIsNone(scene.reconcile_account)
        self.assertIsNone(scene.reconcile_money_type)

    def test_frozen_instance(self):
        """PayScene 为 frozen dataclass，禁止运行期修改"""
        scene = PayScene(des='场景')
        with self.assertRaises(FrozenInstanceError):
            scene.des = '修改'


class _RunSceneTestBase(unittest.TestCase):
    """run_scene 测试公共夹具：统一 mock 数据库 / 请求 / 断言 / 报告表"""

    def setUp(self):
        self.tc = _DummyOverseaTest.__new__(_DummyOverseaTest)
        self.tc.area_rid = AREA_RID_VALUE

        self.m_db = self._start_patch('caseOversea.base.conMysql')
        self.m_encode = self._start_patch('caseOversea.base.encodeOverseaData',
                                          side_effect=lambda **kw: kw)
        self.m_post = self._start_patch('caseOversea.base.post_request_session',
                                        return_value={'code': 200, 'body': {}})
        self.m_code = self._start_patch('caseOversea.base.assert_code')
        self.m_body = self._start_patch('caseOversea.base.assert_body')
        self.m_len = self._start_patch('caseOversea.base.assert_len')
        self.m_equal = self._start_patch('caseOversea.base.assert_equal')
        self.m_case_list = self._start_patch('caseOversea.base.case_list', new={})

    def _start_patch(self, target, **kwargs):
        """启动 patcher 并登记清理，返回其 mock 对象"""
        patcher = patch(target, **kwargs)
        mock = patcher.start()
        self.addCleanup(patcher.stop)
        return mock


class TestRunSceneAccountSetup(_RunSceneTestBase):
    """run_scene 第一步：余额构造分支"""

    def test_normal_scene_resets_both_wallets(self):
        """普通场景：打赏者按 payer_money 充值，收礼人余额清零"""
        self.tc.run_scene(PayScene(des='普通场景'))
        self.assertEqual(self.m_db.updateMoneySql.call_args_list, [
            call(config.oversea_payUid, 700),
            call(config.oversea_testUid),
        ])
        self.m_db.updateUserMoneyClearSql.assert_not_called()
        self.m_db.updateUserextendMoneyClearSql.assert_not_called()

    def test_payer_box_extra_adds_box_wallets(self):
        """箱子场景：打赏者附加三钱包各 100"""
        self.tc.run_scene(PayScene(des='箱子余额', payer_box_extra=True))
        self.assertEqual(self.m_db.updateMoneySql.call_args_list, [
            call(config.oversea_payUid, 700, money_cash=100, money_cash_b=100, money_b=100),
            call(config.oversea_testUid),
        ])

    def test_clear_all_skips_balance_writes(self):
        """余额不足场景：仅清空双方余额，不做任何充值"""
        self.tc.run_scene(PayScene(des='余额不足', clear_all=True, success=0))
        self.m_db.updateUserMoneyClearSql.assert_called_once_with(
            config.oversea_payUid, config.oversea_testUid)
        self.m_db.updateMoneySql.assert_not_called()
        self.m_db.updateUserextendMoneyClearSql.assert_not_called()

    def test_clear_extend_clears_receiver_extend(self):
        """clear_extend 场景：清空被打赏者钱包附加表"""
        self.tc.run_scene(PayScene(des='清附加表', clear_extend=True))
        self.m_db.updateUserextendMoneyClearSql.assert_called_once_with(config.oversea_testUid)


class TestRunSceneRequestBuilding(_RunSceneTestBase):
    """run_scene 第二步：打赏参数组装（rid 三态 / broker uid / is_box）"""

    def test_area_rid_uses_setup_class_value(self):
        """rid 为 AREA_RID 哨兵时取 setUpClass 查询的房间号"""
        self.tc.run_scene(PayScene(des='区域房', rid=AREA_RID))
        self.m_encode.assert_called_once_with(payType='package', rid=AREA_RID_VALUE)

    def test_explicit_rid_overrides(self):
        """rid 为具体值时原样传递"""
        self.tc.run_scene(PayScene(des='指定房', rid=123456))
        self.m_encode.assert_called_once_with(payType='package', rid=123456)

    def test_default_scene_passes_no_rid(self):
        """rid 为 None 时不传房间参数（走 encodeOverseaData 默认房）"""
        self.tc.run_scene(PayScene(des='默认房'))
        self.m_encode.assert_called_once_with(payType='package')

    def test_broker_receiver_passes_uid(self):
        """公会主播收礼：额外传递 uid=brokerUid，余额与到账均查 broker"""
        self.tc.run_scene(PayScene(des='公会场景', receiver=RECEIVER_BROKER))
        self.m_encode.assert_called_once_with(payType='package', uid=config.oversea_brokerUid)
        self.assertEqual(self.m_db.updateMoneySql.call_args_list, [
            call(config.oversea_payUid, 700),
            call(config.oversea_brokerUid),
        ])

    def test_is_box_injects_gift_id(self):
        """箱子场景：注入幸运星 giftId['46']"""
        self.tc.run_scene(PayScene(des='箱子打赏', is_box=True))
        self.m_encode.assert_called_once_with(payType='package', giftId=config.giftId['46'])

    def test_post_uses_oversea_url_and_app_token(self):
        """请求固定使用海外版支付 URL 与 app token"""
        self.tc.run_scene(PayScene(des='请求参数'))
        self.m_post.assert_called_once_with(
            config.oversea_pay_url, {'payType': 'package'}, token_name='app')


class TestRunSceneAssertions(_RunSceneTestBase):
    """run_scene 第三/四/五步：接口断言、余额校验与结果记录"""

    def test_success_and_msg_assertions(self):
        """失败场景：断言 success=0 与 msg 文案"""
        body = {'success': 0, 'msg': '余额不足，无法支付'}
        self.m_post.return_value = {'code': 200, 'body': body}
        self.tc.run_scene(PayScene(des='失败场景', clear_all=True,
                                   success=0, msg='余额不足，无法支付'))
        self.m_code.assert_called_once_with(200)
        self.assertEqual(self.m_body.call_args_list, [
            call(body, 'success', 0),
            call(body, 'msg', '余额不足，无法支付'),
        ])

    def test_msg_none_skips_msg_assertion(self):
        """msg 为 None 时只断言 success"""
        self.tc.run_scene(PayScene(des='无文案'))
        self.assertEqual(self.m_body.call_args_list, [call({}, 'success', 1)])

    def test_payer_expect_none_skips_wallet_check(self):
        """payer_expect 为 None 时不查询打赏者余额"""
        self.tc.run_scene(PayScene(des='跳过打赏者校验', payer_expect=None))
        self.m_db.selectUserInfoSql.assert_called_once_with(
            'money_cash_personal', config.oversea_testUid)

    def test_income_min_uses_assert_len(self):
        """箱子到账：income_min=True 时断言最小值而非相等"""
        self.m_db.selectUserInfoSql.return_value = 0
        self.tc.run_scene(PayScene(des='箱子到账', payer_expect=None,
                                   income_min=True, income_expect=30))
        self.m_len.assert_called_once_with(0, 30)
        self.m_equal.assert_not_called()

    def test_income_money_type_passed(self):
        """income_money_type 非空时作为关键字参数传入查询"""
        self.tc.run_scene(PayScene(des='带钱包类型', payer_expect=None,
                                   income_money_type='money'))
        self.m_db.selectUserInfoSql.assert_called_once_with(
            'money_cash_personal', config.oversea_testUid, money_type='money')

    def test_check_pay_change_reconciles(self):
        """对账：到账字段值与 pay_change 流水相等"""
        self.m_db.selectUserInfoSql.side_effect = [62, 62, 62]
        self.tc.run_scene(PayScene(des='对账', payer_expect=None,
                                   check_pay_change=True, income_expect=62))
        self.assertEqual(self.m_db.selectUserInfoSql.call_args_list, [
            call('money_cash_personal', config.oversea_testUid),
            call('money_cash_personal', config.oversea_testUid),
            call(accountType='pay_change', uid=config.oversea_testUid),
        ])
        self.assertEqual(self.m_equal.call_args_list, [call(62, 62), call(62, 62)])

    def test_check_pay_change_custom_reconcile_fields(self):
        """对账查询支持独立账户与钱包类型（reconcile_*）"""
        self.m_db.selectUserInfoSql.return_value = 0
        self.tc.run_scene(PayScene(des='自定义对账', payer_expect=None,
                                   check_pay_change=True,
                                   reconcile_account='money',
                                   reconcile_money_type='money_cash'))
        self.assertIn(call('money', config.oversea_testUid, money_type='money_cash'),
                      self.m_db.selectUserInfoSql.call_args_list)

    def test_result_recorded_in_case_list(self):
        """场景描述作为报告键写入 case_list"""
        self.tc.run_scene(PayScene(des='记录结果'))
        self.assertEqual(self.m_case_list, {'记录结果': result})


class TestQueryAccountHelper(unittest.TestCase):
    """_query_account 静态方法：money_type 为空时不传该参数"""

    def test_without_money_type(self):
        with patch('caseOversea.base.conMysql') as m_db:
            m_db.selectUserInfoSql.return_value = 7
            self.assertEqual(OverseaAreaTestBase._query_account(1, 'money', None), 7)
            m_db.selectUserInfoSql.assert_called_once_with('money', 1)

    def test_with_money_type(self):
        with patch('caseOversea.base.conMysql') as m_db:
            m_db.selectUserInfoSql.return_value = 7
            self.assertEqual(OverseaAreaTestBase._query_account(1, 'money', 'money_cash'), 7)
            m_db.selectUserInfoSql.assert_called_once_with('money', 1, money_type='money_cash')


if __name__ == '__main__':
    unittest.main()
