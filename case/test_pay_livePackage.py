# coding=utf-8
"""
直播打包结算支付测试

场景差异通过模块级 SCENES 表声明，由 PayTestBase.run_case 统一执行；
公会打包结算数据由类方法 _prepare_broker_data 组合准备。
"""
from case.base import PayCase, PayTestBase
from common.Assert import assert_len
from common.Config import config
from common.conMysql import conMysql as mysql
from common.runFailed import Retry
from common.sqlScript import UserMoneyOperations

# 打包结算主播 / 公会长 / 直播频道
TEST_UID = config.live_role['pack_cal_uid']
CEO_UID = config.live_role['pack_ceo']
LIVE_RID = config.live_role['live_rid']

SCENES = [
    PayCase(
        des='直播间内礼物打赏主播-公会长分成60:21',
        prepare=lambda t: t._prepare_broker_data(TEST_UID, CEO_UID, pay_money=1000),
        data={'rid': LIVE_RID, 'uid': TEST_UID},
        checks=[
            {'field': 'single_money', 'uid': TEST_UID, 'expected': 600,
             'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': CEO_UID, 'expected': 210,
             'kwargs': {'money_type': 'money_cash'}},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ],
        report='case_list_b'),
    PayCase(
        des='直播间内箱子打赏主播-公会长分成60:21',
        prepare=lambda t: t._prepare_broker_data(TEST_UID, CEO_UID, pay_money=700),
        data={'money': 600, 'rid': LIVE_RID, 'giftId': config.giftId['46'],
              'uid': TEST_UID, 'star': 1},
        checks=[
            {'field': 'single_money', 'uid': TEST_UID, 'expected': 300 * 0.6,
             'kwargs': {'money_type': 'money_cash'}, 'assert_func': assert_len},
            {'field': 'single_money', 'uid': CEO_UID, 'expected': 300 * 0.21,
             'kwargs': {'money_type': 'money_cash'}, 'assert_func': assert_len},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 100}
        ],
        report='case_list_b'),
    PayCase(
        des='开通房间守护团给GS收60%（公会）',
        prepare=lambda t: t._prepare_broker_data(TEST_UID, CEO_UID, pay_money=100000),
        data={'payType': 'package-knightDefend', 'money': 99900,
              'uid': TEST_UID, 'rid': LIVE_RID},
        checks=[
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 100},
            {'field': 'single_money', 'uid': TEST_UID, 'expected': 59940,
             'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': CEO_UID, 'expected': 20979,
             'kwargs': {'money_type': 'money_cash'}}
        ],
        report='case_list_b'),
    PayCase(
        des='私聊打赏主播-公会长分成60:20',
        prepare=lambda t: t._prepare_broker_data(TEST_UID, CEO_UID, pay_money=1000),
        data={'payType': 'chat-gift', 'uid': TEST_UID},
        checks=[
            {'field': 'single_money', 'uid': TEST_UID, 'expected': 600,
             'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': CEO_UID, 'expected': 200,
             'kwargs': {'money_type': 'money_cash'}},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ],
        report='case_list_b'),
    PayCase(
        des='私聊打赏箱子主播-公会长分成60:20',
        prepare=lambda t: t._prepare_broker_data(TEST_UID, CEO_UID, pay_money=1000),
        data={'payType': 'chat-gift', 'money': 600, 'uid': TEST_UID,
              'giftId': config.giftId['46'], 'star': 1},
        checks=[
            {'field': 'single_money', 'uid': TEST_UID, 'expected': 300 * 0.6,
             'kwargs': {'money_type': 'money_cash'}, 'assert_func': assert_len},
            {'field': 'single_money', 'uid': CEO_UID, 'expected': 300 * 0.20,
             'kwargs': {'money_type': 'money_cash'}, 'assert_func': assert_len},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 400}
        ],
        report='case_list_b'),
    PayCase(
        des='直播公会主播(非宗师)-公会长打赏分成60:21',
        prepare=lambda t: t._prepare_broker_data(
            TEST_UID, CEO_UID, pay_money=1000,
            extra_steps=[lambda: mysql.checkUserXsMentorLevel(TEST_UID, level=1)]),
        data={'rid': LIVE_RID, 'uid': TEST_UID},
        checks=[
            {'field': 'single_money', 'uid': TEST_UID, 'expected': 600,
             'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': CEO_UID, 'expected': 210,
             'kwargs': {'money_type': 'money_cash'}},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ],
        report='case_list_b'),
    PayCase(
        des='直播间打赏麦下用户分成62:38',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 100}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ],
        data={'giftId': config.giftId['5'], 'rid': LIVE_RID, 'money': 100},
        checks=[
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 62,
             'kwargs': {'money_type': 'money_cash_b'}},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ],
        report='case_list_b'),
    PayCase(
        des='主播在非直播间被打赏70%进个人魅力',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': TEST_UID}}
        ],
        data={'uid': TEST_UID},
        checks=[
            {'field': 'single_money', 'uid': TEST_UID, 'expected': 700},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ],
        report='case_list_b'),
]


@Retry(max_n=3)
class TestPayLivePackage(PayTestBase):
    """直播打包结算支付测试类"""

    def _prepare_broker_data(self, test_uid, ceo_uid, pay_money, extra_steps=None):
        """准备公会打包结算测试数据"""
        mysql.updateUserInfoSql('chatroom', test_uid)  # 商业房房主
        mysql.updateUserInfoSql('broker_user', test_uid, ceo_uid)  # 打包结算
        mysql.checkUserXsBroker(ceo_uid)  # 公会长
        UserMoneyOperations.update(config.payUid, money=pay_money)
        mysql.updateUserMoneyClearSql(test_uid, ceo_uid)
        if extra_steps:
            for step in extra_steps:
                step()

    def test_01_liveRoomPayGift_602119(self):
        """直播间内礼物打赏一代宗师主播，主播-公会长分成 60:21"""
        self.run_case(SCENES[0])

    def test_02_liveRoomPayBox_602119(self):
        """直播间内箱子打赏，分成不小于 60:21"""
        self.run_case(SCENES[1])

    def test_03_knightDefendPayChangeMoney(self):
        """开通房间守护团，GS 收 60%（公会）"""
        self.run_case(SCENES[2])

    def test_04_chatPayGift_602020(self):
        """私聊打赏主播，主播-公会长分成 60:20"""
        self.run_case(SCENES[3])

    def test_05_chatPayBox_602020(self):
        """私聊打赏箱子，分成不小于 60:20"""
        self.run_case(SCENES[4])

    def test_06_liveRoomPayGift_602119(self):
        """直播公会非一代宗师主播，公会长打赏分成 60:21"""
        self.run_case(SCENES[5])

    def test_07_liveRoomUnderRolePay_6238(self):
        """直播间打赏麦下用户，师徒收益基础上分成 62:38"""
        self.run_case(SCENES[6])

    def test_08_NotLiveRoomPayAnchor(self):
        """主播在非直播间被打赏，70% 进个人魅力值"""
        self.run_case(SCENES[7])
