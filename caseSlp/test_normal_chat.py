# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "普通用户-私聊"

from caseSlp.base import SlpCase, SlpTestBase
from caseSlp.config import default_money, default_num, giftId, normal_uid, payUid, rates, rewardUid
from common.runFailed import Retry

# 场景表：普通用户-私聊打赏
SCENES = [
	SlpCase(
		des='普通用户-私聊打赏分成60%(mcb)',
		setup=[
			{'action': 'check_user_broker', 'uid': rewardUid, 'expected': False},
			{'action': 'update_money', 'params': {'uid': payUid, 'money': default_money}},
			{'action': 'clear_user_money', 'uids': [normal_uid]},
			{'action': 'delete_commodity', 'uid': payUid},
		],
		data={'payType': 'chat-gift', 'num': default_num, 'uid': rewardUid,
		      'gift_id': giftId['69']['gid']},
		checks=[
			{'field': 'single_money', 'uid': normal_uid,
			 'expected': giftId['69']['price'] * default_num * rates['normal']['default']},
			{'field': 'sum_money', 'uid': payUid,
			 'expected': default_money - giftId['69']['price'] * default_num},
		],
	),
]


@Retry(max_n=3)
class TestPayCreate(SlpTestBase):

	def test_001(self, des='普通用户-私聊打赏分成60%(mcb)'):
		"""
		用例描述：
		普通用户-私聊打赏分成60%(mcb)
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.私聊一对一打赏流程(礼物:棒棒糖)
		3.校验接口和返回值数据
        4.检查被打赏者余额和账户，预期为：50 * 0.6 = 30(mcb)
        5.检查打赏者余额.预期为：1000 - 50 = 950
		"""
		self.run_case(SCENES[0])
