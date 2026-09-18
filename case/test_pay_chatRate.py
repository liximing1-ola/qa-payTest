# coding=utf-8
"""
私聊打赏分成测试

场景差异通过模块级 SCENES 表声明，由 PayTestBase.run_case 统一执行。
"""
from case.base import PayCase, PayTestBase
from common.Config import config
from common.Assert import assert_len
from common.conMysql import conMysql as mysql
from common.method import calculate_vip_exp
from common.runFailed import Retry

SCENES = [
    PayCase(
        des='私聊打赏钱不足的场景',
        setup=[
            {'action': 'clear_user_data'},
            {'action': 'delete_account', 'table': 'broker_user', 'uid': config.rewardUid},
            {'action': 'delete_account', 'table': 'chatroom', 'uid': config.rewardUid}
        ],
        data={'payType': 'chat-gift', 'num': 10, 'giftId': config.giftId['5']},
        success=0,
        msg='余额不足，无法支付',
        checks=[
            {'field': 'sum_money', 'uid': config.rewardUid, 'expected': 0}
        ]),
    PayCase(
        des='私聊打赏礼物GS收72%',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': config.gsUid}}
        ],
        queries=[('vip_level', lambda: int(mysql.selectUserInfoSql('pay_room_money', config.payUid)))],
        data={'payType': 'chat-gift', 'uid': config.gsUid},
        checks=[
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 1000 * (config.rate - 0.2),
             'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 300,
             'kwargs': {'money_type': 'money_cash_b'}},
            {'field': 'sum_money', 'uid': config.gsUid, 'expected': 720},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0},
            {'field': 'pay_room_money', 'uid': config.payUid,
             'expected': lambda ctx: ctx['vip_level'] + calculate_vip_exp(pay_off=1000)}
        ]),
    PayCase(
        des='私聊打赏boxGS收72%',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 600}},
            {'action': 'update_money', 'params': {'uid': config.gsUid}}
        ],
        data={'payType': 'chat-gift', 'uid': config.gsUid, 'money': 600,
              'giftId': config.giftId['46'], 'star': 1},
        checks=[
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 300 * 0.3, 'assert_func': assert_len},
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 300 * (config.rate - 0.2),
             'kwargs': {'money_type': 'money_cash'}, 'assert_func': assert_len},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ]),
    PayCase(
        des='私聊打赏非一代宗师用户分成72%（mcb）',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ],
        data={'payType': 'chat-gift'},
        checks=[
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 720},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ]),
    PayCase(
        des='私聊打赏一代宗师分成80%（mcb）',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': config.masterUid}}
        ],
        data={'payType': 'chat-gift', 'uid': config.masterUid, 'money': 600,
              'giftId': config.giftId['46'], 'star': 1},
        checks=[
            {'field': 'single_money', 'uid': config.masterUid, 'expected': 300 * 0.8, 'assert_func': assert_len},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 400}
        ]),
]


@Retry(max_n=3)
class TestPayChatRate(PayTestBase):
    """私聊打赏分成测试类"""

    def test_01_chatPayNoMoney(self):
        """账户余额不足时私聊一对一打赏（礼物:棒棒糖）"""
        self.run_case(SCENES[0])

    def test_02_chatPayGiftNormalBroker(self):
        """私聊打赏礼物给GS时，到账为42%公会魅力值+30%个人魅力值"""
        self.run_case(SCENES[1])

    def test_03_chatPayBoxNormalBroker(self):
        """私聊打赏箱box给GS时，到账为42%公会魅力值+30%个人魅力值"""
        self.run_case(SCENES[2])

    def test_04_chatPayGiftNormalUser(self):
        """消费打赏礼物时，非一代宗师用户收72%个人魅力值"""
        self.run_case(SCENES[3])

    def test_05_chatPayBoxNormalUser(self):
        """消费打赏箱子时，一代宗师用户收80%个人魅力值"""
        self.run_case(SCENES[4])
