# coding=utf-8
"""
APP 海外版支付测试 - 英语区域验证

验证英语区消费差异化分成体系（老版本样式，已替换上线新分成，保留历史参考）。
"""
import unittest
from common.Config import config
from caseOversea.base import OverseaAreaTestBase, PayScene


SCENES = [
    PayScene(
        des='英语区私聊打赏礼物 55 分成场景',
        pay_type='chat-gift',
        payer_money=600,
        payer_expect=None,
        income_account='single_money',
        income_money_type='money_cash',
        income_expect=300,
    ),
    PayScene(
        des='英语区私聊打赏箱子 55 分成场景',
        pay_type='chat-gift',
        is_box=True,
        payer_money=300,
        payer_box_extra=True,
        payer_expect=0,
        income_account='sum_money',
        income_expect=150,
        income_min=True,
        check_pay_change=True,
        reconcile_account='single_money',
        reconcile_money_type='money_cash_b',
    ),
    PayScene(
        des='英语区家族房礼物打赏 55 分成场景',
        rid=config.oversea_room['fleet_normal_ar'],
        income_account='single_money',
        income_money_type='money_cash',
        income_expect=300,
    ),
]


@unittest.skip('老版本样式的英语分成体系，已替换上线新分成')
class TestPayCreate(OverseaAreaTestBase):
    """英语区消费差异化验证"""

    bigarea_id = 1

    def test_01_enAreaIMPayGift(self):
        """英语区私聊打赏礼物 55 分成场景"""
        self.run_scene(SCENES[0])

    def test_02_enAreaIMPayGiveBox(self):
        """英语区私聊打赏箱子 55 分成场景"""
        self.run_scene(SCENES[1])

    def test_03_enAreaFleetRoomPay(self):
        """英语区家族房礼物打赏 55 分成场景"""
        self.run_scene(SCENES[2])
