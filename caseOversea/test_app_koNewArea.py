# coding=utf-8
"""
APP 海外版支付测试 - 韩国区域验证

验证韩语区消费差异化分成体系。
"""
from common.Config import config
from caseOversea.base import OverseaAreaTestBase, PayScene, RECEIVER_BROKER
from common.runFailed import Retry


SCENES = [
    PayScene(
        des='韩语私聊打赏非主播分成 75%',
        pay_type='chat-gift',
        clear_extend=True,
        income_money_type='money_cash_personal',
        income_expect=450,
    ),
    PayScene(
        des='韩语私聊打赏主播分成 70%',
        receiver=RECEIVER_BROKER,
        pay_type='chat-gift',
        clear_extend=True,
        income_account='single_money',
        income_money_type='money_cash_b',
        income_expect=420,
    ),
    PayScene(
        des='韩语区家族房礼物打赏主播 70% 分成场景',
        receiver=RECEIVER_BROKER,
        rid=config.oversea_room['fleet_normal_ar'],
        income_account='single_money',
        income_money_type='money_cash_b',
        income_expect=420,
    ),
]


@Retry
class TestPayCreate(OverseaAreaTestBase):
    """韩语区消费差异化验证"""

    bigarea_id = 4

    def test_01_koAreaNoBrokerMemberIMPay(self):
        """韩语私聊打赏非主播分成 75%"""
        self.run_scene(SCENES[0])

    def test_02_koAreaBrokerMemberIMPay(self):
        """韩语私聊打赏主播分成 70%"""
        self.run_scene(SCENES[1])

    def test_03_koNewAreaFleetRoomPay(self):
        """韩语区家族房礼物打赏主播 70% 分成场景"""
        self.run_scene(SCENES[2])
