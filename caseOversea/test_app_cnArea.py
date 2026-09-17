# coding=utf-8
"""
APP 海外版支付测试 - 中文区域验证

验证中文区消费差异化分成体系。
"""
from common.Config import config
from caseOversea.base import OverseaAreaTestBase, PayScene, RECEIVER_BROKER
from common.runFailed import Retry


SCENES = [
    PayScene(
        des='中文大区个人房内打赏主播分成比例 70% 场景',
        receiver=RECEIVER_BROKER,
        rid=config.oversea_room['vip_rid'],
        income_account='single_money',
        income_money_type='money_cash_b',
        income_expect=420,
    ),
    PayScene(
        des='中文大区个人房内打赏非主播分成比例 80% 场景',
        rid=config.oversea_room['vip_rid'],
        clear_extend=True,
        income_money_type='money_cash_personal',
        income_expect=480,
    ),
    PayScene(
        des='中文大区个人房内打赏非主播分成比例 80%（开箱子盲盒打赏）',
        is_box=True,
        rid=config.oversea_room['vip_rid'],
        payer_money=400,
        payer_box_extra=True,
        clear_extend=True,
        income_money_type='money_cash_personal',
        income_expect=240,
        income_min=True,
        check_pay_change=True,
    ),
]


@Retry
class TestPayCreate(OverseaAreaTestBase):
    """中文区消费差异化验证"""

    bigarea_id = 2
    room_type = 'vip'
    room_rid = config.oversea_room['vip_rid']
    room_area = 'cn'

    def test_01_cnAreaVipRoomPay(self):
        """中文大区个人房内打赏主播分成比例 70% 场景"""
        self.run_scene(SCENES[0])

    def test_02_cnAreaVipRoomPay(self):
        """中文大区个人房内打赏非主播分成比例 80% 场景"""
        self.run_scene(SCENES[1])

    def test_03_CnAreaVipRoomGiveBox(self):
        """中文大区个人房内打赏非主播分成比例 80%（开箱子盲盒打赏）"""
        self.run_scene(SCENES[2])
