# coding=utf-8
"""
APP 海外版支付测试 - 阿拉伯区域验证

验证阿语区消费差异化分成体系（老版本样式，已替换新分成，保留历史参考）。
"""
import unittest
from common.Config import config
from caseOversea.base import OverseaAreaTestBase, PayScene


SCENES = [
    PayScene(
        des='阿语大区商业房礼物打赏 37 分成场景',
        rid=config.oversea_room['business_joy_ar'],
        income_account='single_money',
        income_money_type='money_cash',
        income_expect=420,
    ),
    PayScene(
        des='阿语大区商业房箱子打赏 37 分成场景',
        is_box=True,
        rid=config.oversea_room['business_joy_ar'],
        payer_money=400,
        payer_box_extra=True,
        income_account='single_money',
        income_money_type='money_cash_b',
        income_expect=210,
        income_min=True,
        check_pay_change=True,
    ),
    PayScene(
        des='阿语大区私聊礼物打赏 28 分成场景',
        pay_type='chat-gift',
        income_account='single_money',
        income_money_type='money_cash',
        income_expect=480,
    ),
]


@unittest.skip('老版本样式的阿语分成体系，已替换新分成')
class TestPayCreate(OverseaAreaTestBase):
    """阿语区消费差异化验证"""

    bigarea_id = 3
    room_type = 'business'
    room_rid = config.oversea_room['business_joy_ar']
    room_area = 'ar'

    def test_01_arAreaVipRoomPay(self):
        """阿语大区商业房礼物打赏 37 分成场景"""
        self.run_scene(SCENES[0])

    def test_02_arAreaVipRoomGiveBox(self):
        """阿语大区商业房箱子打赏 37 分成场景"""
        self.run_scene(SCENES[1])

    def test_03_arAreaChatPay(self):
        """阿语大区私聊礼物打赏 28 分成场景"""
        self.run_scene(SCENES[2])
