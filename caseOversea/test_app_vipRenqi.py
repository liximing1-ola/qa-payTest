# coding=utf-8
"""
APP 海外版支付测试 - VIP 人气值验证

验证房间打赏和私聊打赏赠送礼物时的人气值和 VIP 等级变化。
"""
from caseOversea.base import OverseaBizCase, OverseaBizTestBase
from common.Config import config
from common.runFailed import Retry

# 人气值由定时 task 异步更新，校验前需等待的时长（秒）
POPULARITY_TASK_WAIT = 2


def _make_vip_renqi_case(des, pay_type):
    """构造单条人气值&VIP 等级验证场景"""
    return OverseaBizCase(
        des=des,
        setup=[
            {'action': 'update_money', 'params': {'uid': config.oversea_payUid, 'money': 600}},
            {'action': 'clear_pay_room_money', 'params': {'uid': config.oversea_payUid}},
            {'action': 'clear_popularity', 'params': {'uid': config.oversea_testUid}},
        ],
        data={'payType': pay_type},
        post_wait=POPULARITY_TASK_WAIT,
        checks=[
            {'field': 'sum_money', 'expected': 0},
            {'field': 'pay_room_money', 'expected': 600},
            {'field': 'popularity', 'uid': config.oversea_testUid, 'min': 600},
        ],
    )


# 场景表：打赏 600 分=60 钻的人气值&VIP 等级校验（房间/私聊）
VIP_RENQI_SCENES = [
    _make_vip_renqi_case('房间打赏礼物校验人气值&自身的 vip 等级', 'package'),
    _make_vip_renqi_case('私聊打赏礼物校验人气值&自身的 vip 等级', 'chat-gift'),
]


@Retry(max_n=3, func_prefix='test_01_payRoomgiftVip')
class TestPayCreate(OverseaBizTestBase):
    """APP 支付创建测试类"""

    check_gift_config = True

    def test_01_payRoomgiftVip(self, des: str = '房间打赏礼物校验人气值&自身的 vip 等级'):
        """房间打赏礼物验证：pay_room_money 新增 600，人气值增加不小于 600"""
        self.run_case(VIP_RENQI_SCENES[0])

    def test_02_payChatgiftVip(self, des: str = '私聊打赏礼物校验人气值&自身的 vip 等级'):
        """私聊打赏礼物验证：pay_room_money 新增 600，人气值增加不小于 600"""
        self.run_case(VIP_RENQI_SCENES[1])
