# coding=utf-8
"""
自定义分成测试

场景差异通过模块级 SCENES 表声明，由 PayTestBase.run_case 统一执行。
"""
from case.base import PayCase, PayTestBase
from common.Config import config
from common.conMysql import conMysql as mysql
from common.runFailed import Retry

# 自定义分成主播 / 打包结算签约主播 / 公会长
CUSTOM_UID = config.bb_user.custom_rate_uid
PACK_CAL_UID = config.bb_user.pack_cal_uid
CEO_UID = config.live_role['pack_ceo']

SCENES = [
    PayCase(
        des='商业房打赏自定义分成:50',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 30, 'money_cash': 30,
                                                   'money_cash_b': 30, 'money_b': 10}},
            {'action': 'clear_user_money', 'uids': (CUSTOM_UID, CEO_UID)},
            {'action': 'check_user_broker', 'params': {'uid': CUSTOM_UID, 'bid': CEO_UID}},
            {'action': 'check_broker_rate', 'params': {'uid': CUSTOM_UID, 'creater': CEO_UID, 'rate': 50}}
        ],
        data={'money': 100, 'uid': CUSTOM_UID, 'giftId': config.giftId['5']},
        checks=[
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0},
            {'field': 'single_money', 'uid': CUSTOM_UID, 'expected': 100 * config.rate * 0.5,
             'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': CEO_UID, 'expected': 100 * config.rate * (1 - 0.5),
             'kwargs': {'money_type': 'money_cash'}}
        ],
        report='case_list_b'),
    PayCase(
        des='私聊打赏自定义分成:80',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 930, 'money_cash': 30,
                                                   'money_cash_b': 30, 'money_b': 10}},
            {'action': 'clear_user_money', 'uids': (CUSTOM_UID, CEO_UID)},
            {'action': 'check_user_broker', 'params': {'uid': CUSTOM_UID, 'bid': CEO_UID}},
            {'action': 'check_broker_rate', 'params': {'uid': CUSTOM_UID, 'creater': CEO_UID, 'rate': 80}}
        ],
        data={'payType': 'chat-gift', 'uid': CUSTOM_UID},
        checks=[
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0},
            {'field': 'sum_money', 'uid': CUSTOM_UID, 'expected': 636},
            {'field': 'single_money', 'uid': CUSTOM_UID, 'expected': 1000 * (config.rate - 0.2) * 0.8,
             'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': CEO_UID, 'expected': 1000 * (config.rate - 0.2) * 0.2,
             'kwargs': {'money_type': 'money_cash'}}
        ],
        report='case_list_b'),
    PayCase(
        des='个人守护打赏自定义分成:25',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 52000}},
            {'action': 'clear_user_money', 'uids': (CUSTOM_UID, CEO_UID)},
            {'action': 'check_user_broker', 'params': {'uid': CUSTOM_UID, 'bid': CEO_UID}},
            {'action': 'check_broker_rate', 'params': {'uid': CUSTOM_UID, 'creater': CEO_UID, 'rate': 25}}
        ],
        data={'payType': 'defend', 'uid': CUSTOM_UID, 'money': 52000, 'defend_id': 2},
        checks=[
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0},
            {'field': 'single_money', 'uid': CUSTOM_UID, 'expected': 7800,
             'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': CEO_UID, 'expected': 24440,
             'kwargs': {'money_type': 'money_cash'}}
        ],
        report='case_list_b'),
    PayCase(
        des='直播公会房间打赏自定义分成比:70',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 30, 'money_cash': 30,
                                                   'money_cash_b': 30, 'money_b': 10}},
            {'action': 'clear_user_money', 'uids': (PACK_CAL_UID, CEO_UID)},
            {'action': 'check_broker_rate', 'params': {'uid': PACK_CAL_UID, 'creater': CEO_UID, 'rate': 70}}
        ],
        data={'money': 100, 'rid': config.live_role['live_rid'], 'uid': PACK_CAL_UID,
              'giftId': config.giftId['5']},
        checks=[
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0},
            {'field': 'single_money', 'uid': PACK_CAL_UID, 'expected': 100 * 0.6 * 0.7,
             'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': CEO_UID, 'expected': 39,
             'kwargs': {'money_type': 'money_cash'}}
        ],
        report='case_list_b'),
    PayCase(
        des='直播公会私聊打赏自定义分成比:0',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 30, 'money_cash': 3000,
                                                   'money_cash_b': 70}},
            {'action': 'clear_user_money', 'uids': (PACK_CAL_UID, CEO_UID)},
            {'action': 'check_broker_rate', 'params': {'uid': PACK_CAL_UID, 'creater': CEO_UID, 'rate': 0}}
        ],
        data={'payType': 'chat-gift', 'uid': PACK_CAL_UID},
        checks=[
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 2100},
            {'field': 'single_money', 'uid': PACK_CAL_UID, 'expected': 0, 'kwargs': {'money_type': 'money_cash'}},
            {'field': 'sum_money', 'uid': PACK_CAL_UID, 'expected': 0},
            {'field': 'single_money', 'uid': CEO_UID, 'expected': 800, 'kwargs': {'money_type': 'money_cash'}}
        ],
        report='case_list_b'),
]


@Retry(max_n=3)
class TestPayCustomRate(PayTestBase):
    """自定义分成测试类"""

    @classmethod
    def tearDownClass(cls) -> None:
        """恢复公会长分成比例"""
        mysql.checkBrokerUserRate(PACK_CAL_UID, CEO_UID, rate=100)

    def test_01_roomPayCustomRate_50(self):
        """后台自定义分成比例为50%，打赏100分"""
        self.run_case(SCENES[0])

    def test_02_chatPayCustomRate_80(self):
        """后台自定义分成比例为80%，私聊打赏1000分"""
        self.run_case(SCENES[1])

    def test_03_defendPayCustomRate_25(self):
        """后台自定义分成比例为25%，开通52000钻个人守护"""
        self.run_case(SCENES[2])

    def test_04_liveRoomPayCustomRate_70(self):
        """后台自定义分成比例为70%，直播间内打赏100分"""
        self.run_case(SCENES[3])

    def test_05_liveChatPayCustomRate_0(self):
        """后台自定义分成比例为0%，直播公会私聊打赏"""
        self.run_case(SCENES[4])
