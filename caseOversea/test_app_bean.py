# coding=utf-8
"""
APP 海外版支付测试 - 金豆兑换验证

验证余额兑换金豆的流程和账户余额变化。
"""
from caseOversea.base import OverseaBizCase, OverseaBizTestBase
from common.Config import config
from common.runFailed import Retry

# 场景：验证余额兑换金豆流程（money 300 全量兑换为 gold_coin 600）
SCENE_001 = OverseaBizCase(
    des='余额兑换金豆场景',
    setup=[
        {'action': 'update_money', 'params': {'uid': config.oversea_payUid, 'money': 300}},
    ],
    data={'payType': 'exchange_gold'},
    checks=[
        {'field': 'sum_money', 'expected': 0},
        {'field': 'single_money', 'money_type': 'gold_coin', 'expected': 600},
    ],
)


@Retry(max_n=3, func_prefix='test_01_moneyExchangeCoin')
class TestPayCreate(OverseaBizTestBase):
    """APP 支付创建测试类"""

    check_gift_config = True

    def test_01_moneyExchangeCoin(self, des: str = '余额兑换金豆场景'):
        """余额兑换金豆验证：money 300 全量兑换为 gold_coin 600"""
        self.run_case(SCENE_001)
