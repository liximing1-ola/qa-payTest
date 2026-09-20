# coding=utf-8
"""
APP 海外版支付测试 - 私聊打赏验证

验证私聊场景下的打赏功能，包括余额不足、正常打赏和箱子打赏。
"""
from caseOversea.base import OverseaBizCase, OverseaBizTestBase
from common.Config import config
from common.runFailed import Retry

# 场景表：私聊打赏（余额不足/正常打赏/箱子打赏）
CHAT_GIFT_SCENES = [
    OverseaBizCase(
        des='私聊打赏余额不足场景',
        setup=[
            {'action': 'clear_money', 'params': {'uids': [config.oversea_payUid, config.oversea_testUid]}},
        ],
        data={'payType': 'chat-gift'},
        success=0,
        msg='餘額不足，無法支付',
        checks=[{'field': 'sum_money', 'uid': config.oversea_testUid, 'expected': 0}],
    ),
    OverseaBizCase(
        des='私聊打赏礼物场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.oversea_payUid, 'money': 600}},
            {'action': 'update_money', 'params': {'uid': config.oversea_testUid}},
            {'action': 'clear_extend_money', 'params': {'uid': config.oversea_testUid}},
        ],
        data={'payType': 'chat-gift'},
        checks=[
            {'field': 'sum_money', 'expected': 0},
            {'field': 'money_cash_personal', 'uid': config.oversea_testUid, 'expected': 480},
        ],
    ),
    OverseaBizCase(
        des='私聊打赏箱子场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.oversea_payUid, 'money': 600}},
            {'action': 'update_money', 'params': {'uid': config.oversea_testUid}},
            {'action': 'clear_extend_money', 'params': {'uid': config.oversea_testUid}},
        ],
        data={'payType': 'chat-gift', 'giftId': config.oversea_giftId['46']},
        checks=[
            {'field': 'sum_money', 'expected': 0},
            {'field': 'money_cash_personal', 'uid': config.oversea_testUid, 'min': 240},
        ],
    ),
]


@Retry(max_n=2)
class TestPayCreate(OverseaBizTestBase):
    """APP 私聊打赏测试类"""

    bigarea_id = 2

    def test_01_IMPayNoMoney(self, des: str = '私聊打赏余额不足场景'):
        """私聊打赏余额不足：success=0 + 提示文案，收礼人余额为 0"""
        self.run_case(CHAT_GIFT_SCENES[0])

    def test_02_IMPayChangeMoney(self, des: str = '私聊打赏礼物场景'):
        """私聊打赏礼物：打赏者 600-600=0，收礼人到账 600*0.8=480"""
        self.run_case(CHAT_GIFT_SCENES[1])

    def test_03_IMPayGiveBox(self, des: str = '私聊打赏箱子场景'):
        """私聊打赏箱子：打赏者 600-600=0，收礼人到账不小于 240"""
        self.run_case(CHAT_GIFT_SCENES[2])
