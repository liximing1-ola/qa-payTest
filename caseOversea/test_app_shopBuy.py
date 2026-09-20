# coding=utf-8
"""
APP 海外版支付测试 - 商城购买验证

验证商城使用金豆和钻石购买道具的流程。
"""
from caseOversea.base import OverseaBizCase, OverseaBizTestBase
from common.Config import config

# 场景表：商城购买道具（金豆道具/钻石道具）
SHOP_BUY_SCENES = [
    OverseaBizCase(
        des='商城购买金豆道具场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.oversea_payUid, 'gold_coin': 30000}},
            {'action': 'delete_user_account', 'params': {'table': 'user_commodity', 'uid': config.oversea_payUid}},
        ],
        data={'payType': 'coin-shop-buy', 'money': 21000, 'cid': 694},
        checks=[
            {'field': 'single_money', 'money_type': 'gold_coin', 'expected': 9000},
            {'field': 'sum_commodity', 'expected': 1},
        ],
    ),
    OverseaBizCase(
        des='商城购买钻石道具场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.oversea_payUid, 'money': 2000, 'money_cash': 200,
                                                  'money_b': 400, 'money_cash_b': 400}},
            {'action': 'delete_user_account', 'params': {'table': 'user_commodity', 'uid': config.oversea_payUid}},
        ],
        data={'payType': 'shop-buy', 'money': 3000, 'cid': 42671},
        checks=[
            {'field': 'sum_money', 'expected': 0},
            {'field': 'sum_commodity', 'expected': 1},
        ],
    ),
]


class TestPayCreate(OverseaBizTestBase):
    """APP 商城购买测试类"""

    def test_01_shopCoinPayChange(self, des: str = '商城购买金豆道具场景', cid: int = 694):
        """金豆购买道具验证：30000-21000=9000 金豆，背包得到 1 个物品"""
        self.run_case(SHOP_BUY_SCENES[0])

    def test_02_shopMoneyPayChange(self, des: str = '商城购买钻石道具场景', cid: int = 42671):
        """钻石购买道具验证：3000-3000=0 钻，背包得到 1 个物品"""
        self.run_case(SHOP_BUY_SCENES[1])
