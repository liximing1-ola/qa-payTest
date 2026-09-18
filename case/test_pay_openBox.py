# coding=utf-8
"""
开箱子支付测试

场景差异通过模块级 SCENES 表声明，由 PayTestBase.run_case 统一执行。
"""
from case.base import PayCase, PayTestBase
from common.Config import config
from common.runFailed import Retry

SCENES = [
    PayCase(
        des='背包开箱子场景',
        setup=[
            {'action': 'delete_user_account', 'params': {'table': 'user_box'}},
            {'action': 'delete_user_account', 'params': {'table': 'user_commodity'}},
            {'action': 'insert_commodity', 'params': {'cid': 2, 'num': 1}},
            {'action': 'insert_user_box', 'params': {}},
            {'action': 'update_money', 'params': {'money': 400, 'money_cash': 100,
                                                   'money_cash_b': 100, 'money_b': 100}}
        ],
        data={'payType': 'shop-buy-box', 'money': 600, 'boxType': 'copper'},
        checks=[
            {'field': 'sum_money', 'expected': 100},
            {'field': 'sum_commodity', 'expected': 2}
        ]),
    PayCase(
        des='背包box开场景',
        setup=[
            {'action': 'delete_user_account', 'params': {'table': 'user_box'}},
            {'action': 'delete_user_account', 'params': {'table': 'user_commodity'}},
            {'action': 'insert_commodity', 'params': {'cid': 3, 'num': 6}},
            {'action': 'insert_user_box', 'params': {'box_type': 'silver'}},
            {'action': 'update_money', 'params': {'money': 12600}}
        ],
        data={'payType': 'shop-buy-box', 'money': 2100, 'num': 6, 'cid': 6, 'boxType': 'silver'},
        checks=[
            {'field': 'sum_money', 'expected': 0},
            {'field': 'sum_commodity', 'expected': 12}
        ]),
    PayCase(
        des='房间sendBox场景',
        setup=[
            {'action': 'update_money', 'params': {'money': 400, 'money_cash': 100,
                                                   'money_cash_b': 100, 'money_b': 100}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ],
        data={'money': 600, 'giftId': config.giftId['46'], 'star': 1},
        checks=[
            {'field': 'sum_money', 'expected': 100},
            {'field': 'sum_money', 'uid': config.rewardUid, 'min_value': 300 * 0.62}
        ]),
    PayCase(
        des='房间送多人多个box场景',
        setup=[
            {'action': 'update_money', 'params': {'money': 10000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ],
        data={'payType': 'package-more', 'num': 2, 'star': 2, 'money': 2100, 'giftId': config.giftId['47']},
        checks=[
            {'field': 'sum_money', 'expected': 1600},
            {'field': 'sum_money', 'uid': config.rewardUid, 'min_value': 1000}
        ]),
]


@Retry(max_n=3)
class TestPayOpenBox(PayTestBase):
    """开箱子支付测试类"""

    def test_01_openBoxPayChange(self):
        """验证背包内openBox得到物品"""
        self.run_case(SCENES[0])

    def test_02_openMoreBoxPayChange(self):
        """验证背包内开多个箱子得到物品"""
        self.run_case(SCENES[1])

    def test_03_giveBoxPayChange(self):
        """验证房间内sendBox逻辑正常"""
        self.run_case(SCENES[2])

    def test_04_giveBoxMorePeople(self):
        """验证房间内sendBox给多个人时逻辑正常"""
        self.run_case(SCENES[3])
