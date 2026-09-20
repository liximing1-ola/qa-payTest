# coding=utf-8
"""
APP 海外版支付测试 - 守护开通验证

验证个人守护开通的收益分成场景。
"""
from caseOversea.base import OverseaBizCase, OverseaBizTestBase
from common.Config import config
from common.runFailed import Retry

# 场景表：个人守护开通收益分成（非主播 80% / 主播 70%）
DEFEND_SCENES = [
    OverseaBizCase(
        des='给非主播开通个人守护场景 80%',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.oversea_payUid, 'money': 66600}},
            {'action': 'update_money', 'params': {'uid': config.oversea_testUid}},
            {'action': 'clear_extend_money', 'params': {'uid': config.oversea_testUid}},
        ],
        data={'payType': 'defend', 'money': 66600},
        checks=[
            {'field': 'sum_money', 'expected': 0},
            {'field': 'money_cash_personal', 'uid': config.oversea_testUid, 'expected': 53280},
        ],
    ),
    OverseaBizCase(
        des='给主播开通个人守护场景 70%',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.oversea_payUid, 'money': 66600}},
            {'action': 'update_money', 'params': {'uid': config.oversea_brokerUid}},
        ],
        data={'payType': 'defend', 'money': 66600, 'uid': config.oversea_brokerUid},
        checks=[
            {'field': 'sum_money', 'expected': 0},
            {'field': 'single_money', 'uid': config.oversea_brokerUid, 'money_type': 'money_cash_b',
             'expected': 46620},
        ],
    ),
]


@Retry
class TestPayCreate(OverseaBizTestBase):
    """APP 守护支付测试类"""

    bigarea_id = 2

    def test_01_defendPayChangMoney(self, des: str = '给非主播开通个人守护场景 80%'):
        """非主播守护开通验证：66600 钻守护，收益 66600*0.8=53280"""
        self.run_case(DEFEND_SCENES[0])

    def test_02_defendPayChangMoney(self, des: str = '给主播开通个人守护场景 70%'):
        """主播守护开通验证：66600 钻守护，收益 66600*0.7=46620"""
        self.run_case(DEFEND_SCENES[1])
