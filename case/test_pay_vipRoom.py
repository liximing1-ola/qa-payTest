# coding=utf-8
"""
个人房（VIP）支付测试

场景差异通过模块级 SCENES 表声明，由 PayTestBase.run_case 统一执行。
"""
from case.base import PayCase, PayTestBase
from common.Config import config
from common.runFailed import Retry

# 个人房 rid（vip>5级不回收）
VIP_ROOM_RID = config.bb_user.vipRoomRid

SCENES = [
    PayCase(
        des='个人房礼物打赏给用户（mcb）',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 30, 'money_cash': 30,
                                                   'money_cash_b': 30, 'money_b': 10}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ],
        data={'payType': 'package', 'money': 100, 'rid': VIP_ROOM_RID, 'giftId': config.giftId['5']},
        checks=[
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 62},
            {'field': 'sum_money', 'expected': 0}
        ],
        report='case_list_b'),
    PayCase(
        des='个人房打赏box给用户（mcb）',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 400, 'money_cash': 100,
                                                   'money_cash_b': 100, 'money_b': 100}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ],
        data={'payType': 'package', 'money': 600, 'rid': VIP_ROOM_RID,
              'giftId': config.giftId['46'], 'star': 1},
        checks=[
            {'field': 'sum_money', 'expected': 100},
            {'field': 'single_money', 'uid': config.rewardUid, 'min_value': 300 * 0.62},
            {'field': 'sum_money', 'uid': config.rewardUid, 'min_value': 300 * 0.62}
        ],
        report='case_list_b'),
    PayCase(
        des='个人房打赏钻石礼物给GS（mcb）',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money_cash_b': 100}},
            {'action': 'update_money', 'params': {'uid': config.gsUid}}
        ],
        data={'money': 100, 'rid': VIP_ROOM_RID, 'uid': config.gsUid, 'giftId': config.giftId['5']},
        checks=[
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 70},
            {'field': 'sum_money', 'uid': config.gsUid, 'expected': 70},
            {'field': 'sum_money', 'expected': 0}
        ],
        report='case_list_b'),
]


@Retry(max_n=3)
class TestPayVipRoom(PayTestBase):
    """个人房支付测试类"""

    def test_01_personRoomPayGift(self):
        """个人房打赏礼物分成满足师徒收益(非一代宗师)的基础上为：62:38，且收入在个人魅力值"""
        self.run_case(SCENES[0])

    def test_02_personRoomPayBox(self):
        """个人房打赏礼盒分成满足师徒收益(非一代宗师)的基础上为：62:38，且收入在个人魅力值"""
        self.run_case(SCENES[1])

    def test_03_personRoomPayGiftToBrokerUser(self):
        """个人房打赏礼物给工会成员分成为：70:30，且收入在个人魅力值"""
        self.run_case(SCENES[2])
