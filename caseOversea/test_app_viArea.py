# coding=utf-8
"""
APP 海外版支付测试 - 越南区域验证

验证越南区消费差异化分成体系。
"""
from common.Config import config
from common.conPtMysql import conMysql
from caseOversea.base import OverseaAreaTestBase, PayScene, AREA_RID
from common.runFailed import Retry


SCENES = [
    PayScene(
        des='越南区区商业房礼物打赏非主播 70% 分成场景',
        rid=AREA_RID,
        clear_extend=True,
        income_money_type='money_cash_personal',
        income_expect=420,
    ),
    PayScene(
        des='越南区区商业房箱子打赏非主播 70% 分成场景',
        is_box=True,
        rid=AREA_RID,
        payer_money=400,
        payer_box_extra=True,
        clear_extend=True,
        income_money_type='money_cash_personal',
        income_expect=210,
        income_min=True,
        check_pay_change=True,
    ),
]


@Retry
class TestPayCreate(OverseaAreaTestBase):
    """越南区消费差异化验证"""

    bigarea_id = 7
    room_type = 'business'
    room_rid = config.oversea_room['business_joy_vi']
    room_area = 'vn'

    @classmethod
    def setUpClass(cls):
        """查询越南区商业房 rid（每类只查一次）"""
        super().setUpClass()
        cls.area_rid = conMysql.select_user_chatroom('business', bigarea_id=7)

    def test_01_viAreaVipRoomPay(self):
        """越南区区商业房礼物打赏非主播 70% 分成场景"""
        self.run_scene(SCENES[0])

    def test_02_viAreaVipRoomGiveBox(self):
        """越南区区商业房箱子打赏非主播 70% 分成场景"""
        self.run_scene(SCENES[1])
