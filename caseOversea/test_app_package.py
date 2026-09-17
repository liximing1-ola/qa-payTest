# coding=utf-8
"""
APP 海外版支付测试 - 房间打赏验证

验证房间场景下的打赏功能，包括余额不足和正常打赏。
"""
from common.Config import config
from common.conPtMysql import conMysql
from caseOversea.base import OverseaAreaTestBase, PayScene, AREA_RID
from common.runFailed import Retry


SCENES = [
    PayScene(
        des='房间打赏但余额不足的场景',
        clear_all=True,
        success=0,
        msg='餘額不足，無法支付',
        payer_expect=None,
        income_account='sum_money',
        income_expect=0,
    ),
    PayScene(
        des='商业房 1V1 打赏非主播 70% 场景',
        rid=AREA_RID,
        clear_extend=True,
        payer_expect=None,
        income_money_type='money_cash_personal',
        income_expect=420,
    ),
]


@Retry
class TestPayCreate(OverseaAreaTestBase):
    """APP 房间打赏测试类"""

    bigarea_id = 2
    room_type = 'vip'
    room_rid = config.oversea_room['vip_rid']
    room_area = 'cn'

    @classmethod
    def setUpClass(cls):
        """查询 2 区商业房 rid（每类只查一次）"""
        super().setUpClass()
        cls.area_rid = conMysql.select_user_chatroom('business', bigarea_id=2)

    def test_01_RoomPayNoMoney(self):
        """房间打赏但余额不足的场景"""
        self.run_scene(SCENES[0])

    def test_02_RoomPayChangeMoney(self):
        """商业房 1V1 打赏非主播 70% 场景"""
        self.run_scene(SCENES[1])
