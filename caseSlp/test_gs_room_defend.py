# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "公会主播-房间守护"

from caseSlp.base import SlpCase, SlpTestBase
from caseSlp.config import default_money, gsUid, gs_A_ceo_uid, gs_soundchat_rid, payUid, rates, room_defend
from common.runFailed import Retry

# 真爱守护-月（开通档位）
_ZHENAI_MONTH = room_defend['zhenai']['month']

# 场景表：公会主播-房间守护
SCENES = [
    SlpCase(
        des='商业房-直播,开通房间守护给GS收60%（mc）',
        setup=[
            {'action': 'check_user_broker', 'uid': gsUid, 'expected': True},
            {'action': 'check_rid_type', 'rid': gs_soundchat_rid, 'expected': 'business-soundchat'},
            {'action': 'update_user_god', 'params': {'uid': gsUid, 'god': 1}},
            {'action': 'update_user_god', 'params': {'uid': gs_A_ceo_uid, 'god': 1}},
            {'action': 'update_money', 'params': {'uid': payUid, 'money': default_money}},
            {'action': 'clear_user_money', 'uids': [gsUid, gs_A_ceo_uid]},
        ],
        data={
            'payType': 'package-knightDefend',
            'money': _ZHENAI_MONTH['price'],
            'uid': gsUid,
            'rid': gs_soundchat_rid,
            'knight_level': _ZHENAI_MONTH['knight_level'],
            'duration_level': _ZHENAI_MONTH['duration_level'],
            'price': _ZHENAI_MONTH['price'],
        },
        checks=[
            {'field': 'sum_money', 'uid': payUid,
             'expected': default_money - _ZHENAI_MONTH['price']},
            {'field': 'single_money', 'uid': gsUid, 'money_type': 'money_cash',
             'expected': _ZHENAI_MONTH['price'] * rates['gs']['default']},
            {'field': 'sum_money', 'uid': gs_A_ceo_uid, 'expected': 0},
        ],
    ),
]


@Retry(max_n=3)
class TestPayCreate(SlpTestBase):

    def test_001(self, des='商业房-直播,开通房间守护给GS收60%（mc）'):
        """
		 用例描述：
		商业房-直播,开通房间守护给GS收60%（mc）
		 脚本步骤：
		 1.构造开通者和被守护者数据
		 2.开通真爱守护 月
		 3.校验接口状态和返回值数据
		 4.检查打赏者余额，预期：100000 - 99900 = 100
		 5.检查公会长余额，预期为： 0(不分成)
		 6.检查被打赏者余额.预期为：99900 * 0.6 = 59940
		 """
        self.run_case(SCENES[0])
