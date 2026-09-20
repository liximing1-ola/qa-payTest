# coding=utf-8
"""
APP 海外版支付测试 - 背包开箱验证

验证背包内开箱子得到物品的流程。
"""
from caseOversea.base import OverseaBizCase, OverseaBizTestBase
from common.Config import config
from common.runFailed import Retry

# 场景表：背包开箱（铜箱子单开/银箱子多开）
OPEN_BOX_SCENES = [
    OverseaBizCase(
        des='背包开铜箱子场景',
        setup=[
            {'action': 'delete_user_account', 'params': {'table': 'user_box', 'uid': config.oversea_payUid}},
            {'action': 'delete_user_account', 'params': {'table': 'user_commodity', 'uid': config.oversea_payUid}},
            {'action': 'insert_commodity', 'params': {'uid': config.oversea_payUid, 'cid': 2, 'num': 1}},
            {'action': 'insert_box', 'params': {'uid': config.oversea_payUid}},
            {'action': 'update_money', 'params': {'uid': config.oversea_payUid, 'money': 400,
                                                  'money_cash': 100, 'money_cash_b': 100, 'money_b': 100}},
        ],
        data={'payType': 'shop-buy-box'},
        checks=[
            {'field': 'sum_money', 'expected': 100},
            {'field': 'sum_commodity', 'expected': 1},
        ],
    ),
    OverseaBizCase(
        des='背包箱子多开场景',
        setup=[
            {'action': 'delete_user_account', 'params': {'table': 'user_box', 'uid': config.oversea_payUid}},
            {'action': 'delete_user_account', 'params': {'table': 'user_commodity', 'uid': config.oversea_payUid}},
            {'action': 'insert_commodity', 'params': {'uid': config.oversea_payUid, 'cid': 3, 'num': 6}},
            {'action': 'insert_box', 'params': {'uid': config.oversea_payUid}},
            {'action': 'update_money', 'params': {'uid': config.oversea_payUid, 'money': 700,
                                                  'money_cash': 2000, 'money_cash_b': 2000, 'money_b': 2000}},
        ],
        data={'payType': 'shop-buy-box', 'num': 6},
        checks=[
            {'field': 'sum_money', 'expected': 700},
            {'field': 'sum_commodity', 'min': 6},
        ],
    ),
]


@Retry
class TestPayCreate(OverseaBizTestBase):
    """APP 背包开箱测试类"""

    bigarea_id = 2

    def test_01_openBoxPayChange(self, des: str = '背包开铜箱子场景', cid: int = 2):
        """铜箱子开启验证：700-600=100 钻，背包开出 1 个物品"""
        self.run_case(OPEN_BOX_SCENES[0])

    def test_02_openMoreBoxPayChange(self, des: str = '背包箱子多开场景', cid: int = 3):
        """多箱子开启验证：13300-12600=700 钻，背包开出不少于 6 个物品"""
        self.run_case(OPEN_BOX_SCENES[1])
