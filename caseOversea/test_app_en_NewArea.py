# coding=utf-8
"""
APP 海外版支付测试 - 英语新区域验证

验证英语区新消费差异化分成体系。
"""
from caseOversea.base import OverseaAreaTestBase, PayScene, RECEIVER_BROKER
from common.runFailed import Retry


SCENES = [
    PayScene(
        des='英语大区私聊礼物打赏主播 55 分成场景',
        receiver=RECEIVER_BROKER,
        pay_type='chat-gift',
        income_account='single_money',
        income_money_type='money_cash',
        income_expect=300,
    ),
    PayScene(
        des='英语大区私聊礼物打赏非主播 73 分成场景',
        pay_type='chat-gift',
        clear_extend=True,
        income_money_type='money_cash_personal',
        income_expect=420,
    ),
    PayScene(
        des='英语区私聊打赏非主播箱子 73 分成场景',
        pay_type='chat-gift',
        is_box=True,
        payer_money=300,
        payer_box_extra=True,
        clear_extend=True,
        payer_expect=0,
        income_money_type='money_cash_personal',
        income_expect=210,
        income_min=True,
        check_pay_change=True,
    ),
]


@Retry
class TestPayCreate(OverseaAreaTestBase):
    """英语区消费差异化验证"""

    bigarea_id = 1

    def test_01_enNewAreaChatPay(self):
        """英语大区私聊礼物打赏主播 55 分成场景"""
        self.run_scene(SCENES[0])

    def test_02_enNewAreaChatPay(self):
        """英语大区私聊礼物打赏非主播 73 分成场景"""
        self.run_scene(SCENES[1])

    def test_03_enNewAreaIMPayGiveBox(self):
        """英语区私聊打赏非主播箱子 73 分成场景"""
        self.run_scene(SCENES[2])
