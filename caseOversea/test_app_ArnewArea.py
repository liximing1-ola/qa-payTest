# coding=utf-8
"""
APP 海外版支付测试 - 阿拉伯新区域验证

验证阿语区新消费差异化分成体系。
"""
from common.Config import config
from caseOversea.base import OverseaAreaTestBase, PayScene, RECEIVER_BROKER
from common.runFailed import Retry


SCENES = [
    PayScene(
        des='阿语大区商业房礼物打赏主播分成 55 场景',
        receiver=RECEIVER_BROKER,
        rid=config.oversea_room['business_joy_ar'],
        income_account='single_money',
        income_money_type='money_cash',
        income_expect=300,
    ),
    PayScene(
        des='阿语大区商业房箱子打赏主播 55 分成场景',
        receiver=RECEIVER_BROKER,
        is_box=True,
        rid=config.oversea_room['business_joy_ar'],
        payer_money=400,
        payer_box_extra=True,
        income_account='single_money',
        income_money_type='money_cash',
        income_expect=150,
        income_min=True,
        check_pay_change=True,
    ),
    PayScene(
        des='阿语大区私聊礼物打赏主播55分成场景',
        receiver=RECEIVER_BROKER,
        pay_type='chat-gift',
        income_account='single_money',
        income_money_type='money_cash',
        income_expect=300,
    ),
]


@Retry
class TestPayCreate(OverseaAreaTestBase):
    """阿语区消费差异化验证"""

    bigarea_id = 3
    room_type = 'business'
    room_rid = config.oversea_room['business_joy_ar']
    room_area = 'ar'

    def test_01_arNewAreaVipRoomPay(self):
        """阿语大区商业房礼物打赏主播分成 55 场景"""
        self.run_scene(SCENES[0])

    def test_02_arNewAreaVipRoomGiveBox(self):
        """阿语大区商业房箱子打赏主播 55 分成场景"""
        self.run_scene(SCENES[1])

    def test_03_arNewAreaChatPay(self):
        """阿语大区私聊礼物打赏主播55分成场景"""
        self.run_scene(SCENES[2])
