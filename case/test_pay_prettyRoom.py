# coding=utf-8
"""
靓号房支付测试

场景差异通过模块级 SCENES 表声明，由 PayTestBase.run_case 统一执行。
"""
from case.base import PayCase, PayTestBase
from common.Config import config
from common.runFailed import Retry

# 靓号房 rid
PRETTY_RID = config.bb_user.prettyRid

SCENES = [
    PayCase(
        des='靓号房打赏礼物GS分62%进公会魅力值',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money_cash_b': 250}},
            {'action': 'clear_user_money', 'params': {'uid1': config.gsUid}}
        ],
        data={'money': 100, 'rid': PRETTY_RID, 'uid': config.gsUid, 'giftId': config.giftId['5']},
        checks=[
            {'field': 'single_money', 'uid': config.gsUid, 'money_type': 'money_cash', 'expected': 100 * config.rate},
            {'field': 'sum_money', 'uid': config.gsUid, 'expected': 100 * config.rate},
            {'field': 'sum_money', 'expected': 150}
        ],
        report='case_list_b'),
    PayCase(
        des='靓号房打赏礼盒GS分62%进公会魅力值',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 400, 'money_cash': 100,
                                                   'money_cash_b': 100, 'money_b': 100}},
            {'action': 'clear_user_money', 'params': {'uid1': config.gsUid}}
        ],
        data={'money': 600, 'uid': config.gsUid, 'rid': PRETTY_RID,
              'giftId': config.giftId['46'], 'star': 1},
        checks=[
            {'field': 'sum_money', 'expected': 100},
            {'field': 'single_money', 'uid': config.gsUid, 'money_type': 'money_cash', 'min_value': 300 * config.rate}
        ],
        report='case_list_b'),
    PayCase(
        des='靓号房打赏普通用户进个人魅力值',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money_cash': 100}},
            {'action': 'clear_user_money', 'params': {'uid1': config.rewardUid}}
        ],
        data={'money': 100, 'rid': PRETTY_RID, 'uid': config.rewardUid, 'giftId': config.giftId['5']},
        checks=[
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 62},
            {'field': 'sum_money', 'expected': 0}
        ],
        report='case_list_b'),
]


@Retry(max_n=3)
class TestPayPrettyRoom(PayTestBase):
    """靓号房支付测试类"""

    def test_01_prettyRoomPayGiftToBrokerUser(self):
        """靓号房打赏礼物给公会成员分成为62%且收入进公会魅力值"""
        self.run_case(SCENES[0])

    def test_02_prettyRoomPayBox(self):
        """靓号房打赏礼盒给公会成员分成为62%且收入进公会魅力值"""
        self.run_case(SCENES[1])

    def test_03_prettyRoomPayGiftToNormalUser(self):
        """靓号房打赏礼物给普通用户（非一代宗师）分成为62%且收入进个人魅力值"""
        self.run_case(SCENES[2])
