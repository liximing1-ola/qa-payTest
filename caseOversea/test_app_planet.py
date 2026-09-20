# coding=utf-8
"""
APP 海外版支付测试 - 星球之旅验证

验证星球之旅玩法的钻石扣除和礼物获取流程。
"""
import unittest

from caseOversea.base import OverseaBizCase, OverseaBizTestBase
from common.Config import config

# 场景：星球之旅扣钻石获取礼物（2000-1500=500 钻，背包得到 1 个物品）
SCENE_001 = OverseaBizCase(
    des='星球之旅扣钻石获取礼物玩法',
    setup=[
        {'action': 'delete_user_account', 'params': {'table': 'user_commodity', 'uid': config.oversea_payUid}},
        {'action': 'delete_user_account',
         'params': {'table': 'user_journey_planet_record', 'uid': config.oversea_payUid}},
        {'action': 'delete_user_account',
         'params': {'table': 'user_journey_planet_draw_record', 'uid': config.oversea_payUid}},
        {'action': 'update_money', 'params': {'uid': config.oversea_payUid, 'money': 2000}},
    ],
    data={'payType': 'journey_planet_draw'},
    checks=[
        {'field': 'sum_money', 'expected': 500},
        {'field': 'sum_commodity', 'expected': 1},
    ],
)


@unittest.skip('修复')
class TestPayCreate(OverseaBizTestBase):
    """APP 星球之旅测试类"""

    def test_01_journey_planet(self, des: str = '星球之旅扣钻石获取礼物玩法'):
        """星球之旅玩法验证：一轮一关扣 150 钻*10=1500，背包得到 1 个礼物"""
        self.run_case(SCENE_001)
