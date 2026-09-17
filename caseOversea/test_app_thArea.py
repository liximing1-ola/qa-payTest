# coding=utf-8
"""
APP 海外版支付测试 - 泰国区域验证

验证泰语区消费差异化分成体系。
"""
from common.Config import config
from caseOversea.base import OverseaAreaTestBase, PayScene
from common.runFailed import Retry


SCENES = [
    PayScene(
        des='泰区联盟房礼物打赏非主播 80% 分成场景',
        rid=config.oversea_room['th_union'],
        clear_extend=True,
        income_money_type='money_cash_personal',
        income_expect=480,
    ),
    PayScene(
        des='泰区联盟房送非主播箱子 80% 场景',
        is_box=True,
        rid=config.oversea_room['th_union'],
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
    """泰语区消费差异化验证"""

    bigarea_id = 6
    room_type = 'union'
    room_rid = config.oversea_room['th_union']
    room_area = 'th'
    clear_redis_on_teardown = True

    def test_01_thaiUnionRoomPay(self):
        """泰区联盟房礼物打赏非主播 80% 分成场景"""
        self.run_scene(SCENES[0])

    def test_02_thaiUnionRoomGiveBox(self):
        """泰区联盟房送非主播箱子 80% 场景"""
        self.run_scene(SCENES[1])
