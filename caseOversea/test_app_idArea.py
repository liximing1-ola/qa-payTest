# coding=utf-8
"""
APP 海外版支付测试 - 印度尼西亚区域验证

验证印尼区消费差异化分成体系。
"""
from common.Config import config
from common.conPtMysql import conMysql
from caseOversea.base import OverseaAreaTestBase, PayScene, AREA_RID
from common.runFailed import Retry


SCENES = [
    PayScene(
        des='印尼区家族房礼物非主播打赏 80% 分成',
        rid=AREA_RID,
        clear_extend=True,
        income_money_type='money_cash_personal',
        income_expect=480,
    ),
    PayScene(
        des='印尼区家族房打赏非主播送箱子 80% 分成场景',
        is_box=True,
        rid=AREA_RID,
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
    """印尼区消费差异化验证"""

    bigarea_id = 5
    room_type = 'fleet'
    room_rid = config.oversea_room['id_fleet']
    room_area = 'id'
    clear_redis_on_setup = True

    @classmethod
    def setUpClass(cls):
        """查询印尼区家族房 rid（每类只查一次）"""
        super().setUpClass()
        cls.area_rid = conMysql.select_user_chatroom(property='fleet', bigarea_id=5)

    def test_01_idAreaFleetRoomPay(self):
        """印尼区家族房礼物非主播打赏 80% 分成"""
        self.run_scene(SCENES[0])

    def test_02_idAreaFleetRoomGiveBox(self):
        """印尼区家族房打赏非主播送箱子 80% 分成场景"""
        self.run_scene(SCENES[1])
