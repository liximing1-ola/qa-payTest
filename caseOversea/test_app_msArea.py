# coding=utf-8
"""
APP 海外版支付测试 - 马来西亚区域验证

验证马来区消费差异化分成体系（马来大区已关闭合并到印尼，保留历史参考）。
"""
import unittest
from common.conPtMysql import conMysql
from caseOversea.base import OverseaAreaTestBase, PayScene, AREA_RID, RECEIVER_BROKER


SCENES = [
    PayScene(
        des='马来区家族房/个人房礼物非主播打赏 80% 分成',
        rid=AREA_RID,
        clear_extend=True,
        income_money_type='money_cash_personal',
        income_expect=480,
    ),
    PayScene(
        des='马来区家族房打赏非主播送箱子 80% 分成场景',
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
    PayScene(
        des='马来区私聊打赏主播分成 50%',
        receiver=RECEIVER_BROKER,
        pay_type='chat-gift',
        income_account='single_money',
        income_money_type='money_cash_b',
        income_expect=300,
    ),
]


@unittest.skip('马来大区已关闭合并到印尼')
class TestPayCreate(OverseaAreaTestBase):
    """马来区消费差异化验证"""

    bigarea_id = 9
    clear_redis_on_setup = True

    @classmethod
    def setUpClass(cls):
        """查询马来区个人房 rid（每类只查一次）"""
        super().setUpClass()
        cls.area_rid = conMysql.select_user_chatroom(property='vip', bigarea_id=9)

    def test_01_msAreaFleetRoomPay(self):
        """马来区家族房/个人房礼物非主播打赏 80% 分成"""
        self.run_scene(SCENES[0])

    def test_02_msAreaFleetRoomGiveBox(self):
        """马来区家族房打赏非主播送箱子 80% 分成场景"""
        self.run_scene(SCENES[1])

    def test_03_msAreaBrokerMemberIMPay(self):
        """马来区私聊打赏主播分成 50%"""
        self.run_scene(SCENES[2])
