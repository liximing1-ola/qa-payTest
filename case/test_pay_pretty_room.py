"""
靓号房支付测试

场景差异通过模块级 SCENES 表声明，由 PayTestBase.run_case 统一执行。
"""
from case.base import PayCase, PayTestBase

from common.config import config
from common.run_failed import Retry

# 靓号房 rid
PRETTY_RID = config.bb_user.pretty_rid

SCENES = [
    PayCase(
        des='靓号房打赏礼物GS分62%进公会魅力值',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.pay_uid, 'money_cash_b': 250}},
            {'action': 'clear_user_money', 'params': {'uid1': config.gs_uid}}
        ],
        data={'money': 100, 'rid': PRETTY_RID, 'uid': config.gs_uid, 'giftId': config.gift_id['5']},
        checks=[
            {'field': 'single_money', 'uid': config.gs_uid, 'money_type': 'money_cash', 'expected': 100 * config.rate},
            {'field': 'sum_money', 'uid': config.gs_uid, 'expected': 100 * config.rate},
            {'field': 'sum_money', 'expected': 150}
        ],
        report='case_list_b'),
    PayCase(
        des='靓号房打赏礼盒GS分62%进公会魅力值',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.pay_uid, 'money': 400, 'money_cash': 100,
                                                   'money_cash_b': 100, 'money_b': 100}},
            {'action': 'clear_user_money', 'params': {'uid1': config.gs_uid}}
        ],
        data={'money': 600, 'uid': config.gs_uid, 'rid': PRETTY_RID,
              'giftId': config.gift_id['46'], 'star': 1},
        checks=[
            {'field': 'sum_money', 'expected': 100},
            {'field': 'single_money', 'uid': config.gs_uid, 'money_type': 'money_cash', 'min_value': 300 * config.rate}
        ],
        report='case_list_b'),
    PayCase(
        des='靓号房打赏普通用户进个人魅力值',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.pay_uid, 'money_cash': 100}},
            {'action': 'clear_user_money', 'params': {'uid1': config.reward_uid}}
        ],
        data={'money': 100, 'rid': PRETTY_RID, 'uid': config.reward_uid, 'giftId': config.gift_id['5']},
        checks=[
            {'field': 'single_money', 'uid': config.reward_uid, 'expected': 62},
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
