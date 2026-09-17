# coding=utf-8
"""
APP 海外版支付测试 - 日本区域验证

验证日语区消费差异化分成体系。
"""
from caseOversea.base import OverseaAreaTestBase, PayScene, RECEIVER_BROKER
from common.runFailed import Retry


SCENES = [
    PayScene(
        des='日语区私聊打赏非公会私聊分成 70%',
        pay_type='chat-gift',
        payer_money=600,
        clear_extend=True,
        payer_expect=0,
        income_money_type='money_cash_personal',
        income_expect=420,
    ),
    PayScene(
        des='日语区私聊打赏公会主播私聊箱子分成 60%',
        receiver=RECEIVER_BROKER,
        pay_type='chat-gift',
        is_box=True,
        payer_money=600,
        payer_expect=0,
        income_account='sum_money',
        income_expect=180,
        income_min=True,
        check_pay_change=True,
        reconcile_account='single_money',
        reconcile_money_type='money_cash_b',
    ),
    PayScene(
        des='日语区房间打赏非公会私聊分成 70%',
        payer_money=600,
        clear_extend=True,
        payer_expect=0,
        income_money_type='money_cash_personal',
        income_expect=420,
    ),
]


@Retry
class TestPayCreate(OverseaAreaTestBase):
    """日语区消费差异化验证"""

    bigarea_id = 10

    def test_01_jaAreaNoBrokerMemberIMPay(self):
        """日语区私聊打赏非公会私聊分成 70%"""
        self.run_scene(SCENES[0])

    def test_02_jaAreaBrokerMemberIMPayGiveBox(self):
        """日语区私聊打赏公会主播私聊箱子分成 60%"""
        self.run_scene(SCENES[1])

    def test_03_jaAreaNoBrokerMemberRoomPay(self):
        """日语区房间打赏非公会私聊分成 70%"""
        self.run_scene(SCENES[2])
