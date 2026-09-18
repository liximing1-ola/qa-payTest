# coding=utf-8
"""
coin 支付测试

场景差异通过模块级 SCENES 表声明，由 PayTestBase.run_case 统一执行。
"""
from case.base import PayCase, PayTestBase
from common.Config import config
from common.conMysql import conMysql as mysql
from common.method import calculate_vip_exp
from common.runFailed import Retry

SCENES = [
    PayCase(
        des='余额兑换金币场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}}
        ],
        data={'payType': 'exchange_gold'},
        checks=[
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 400},
            {'field': 'single_money', 'uid': config.payUid, 'expected': 600, 'kwargs': {'money_type': 'gold_coin'}}
        ]),
    PayCase(
        des='房间打赏金币礼物的场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'gold_coin': 100}},
            {'action': 'clear_user_data', 'uids': (config.rewardUid, config.masterUid)}
        ],
        queries=[('vip_level', lambda: int(mysql.selectUserInfoSql('pay_room_money', config.payUid)))],
        data={'payType': 'package-more', 'money': 20, 'giftId': config.giftId['62'], 'giftType': 'coin'},
        checks=[
            {'field': 'single_money', 'uid': config.payUid, 'expected': 60, 'kwargs': {'money_type': 'gold_coin'}},
            {'field': 'single_money', 'uid': config.masterUid, 'expected': 12, 'kwargs': {'money_type': 'gold_coin'}},
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 12, 'kwargs': {'money_type': 'gold_coin'}},
            {'field': 'pay_room_money', 'uid': config.payUid,
             'expected': lambda ctx: ctx['vip_level'] + calculate_vip_exp(money_type='coin', pay_off=40)}
        ]),
]


@Retry(max_n=3, func_prefix='test_02_roomChangePayCoin')
class TestPayCoin(PayTestBase):
    """coin支付测试类"""

    def test_01_moneyChangeExchangeCoin(self):
        """验证money兑换金币流程"""
        self.run_case(SCENES[0])

    def test_02_roomChangePayCoin(self):
        """验证房间内打赏金币流程"""
        self.run_case(SCENES[1])
