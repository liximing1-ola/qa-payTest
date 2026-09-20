# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "打赏多人多礼物"

from caseSlp.base import SlpCase, SlpTestBase
from caseSlp.config import giftId, gs_A_uid, gs_B_ceo_rid, gs_B_uid, normal_uid, payUid, rates
from common.runFailed import Retry

# 打赏人数与礼物个数
_uids = tuple(str(i) for i in [gs_A_uid, gs_B_uid, normal_uid])
_num = 5

# 场景表：打赏多人多礼物
SCENES = [
	SlpCase(
		des='房间内打赏多人(gs+normal)多礼物场景',
		setup=[
			{'action': 'check_user_broker', 'uid': gs_A_uid, 'expected': True},
			{'action': 'check_user_broker', 'uid': gs_B_uid, 'expected': True},
			{'action': 'check_user_broker', 'uid': normal_uid, 'expected': False},
			{'action': 'update_user_god', 'params': {'uid': gs_A_uid, 'god': 0}},
			{'action': 'update_user_god', 'params': {'uid': gs_B_uid, 'god': 1}},
			{'action': 'update_money',
			 'params': {'uid': payUid, 'money': giftId['69']['price'] * _num * len(_uids)}},
			{'action': 'clear_user_money', 'uids': [gs_A_uid, gs_B_uid, normal_uid]},
		],
		data={
			'rid': gs_B_ceo_rid,
			'payType': 'package-more',
			'num': _num,
			'uids': _uids,
		},
		checks=[
			{'field': 'single_money', 'uid': gs_A_uid,
			 'expected': giftId['69']['price'] * rates['gs']['default'] * _num},
			{'field': 'single_money', 'uid': gs_B_uid, 'money_type': 'money_cash',
			 'expected': giftId['69']['price'] * rates['gs']['default'] * _num},
			{'field': 'single_money', 'uid': normal_uid,
			 'expected': giftId['69']['price'] * rates['normal']['default'] * _num},
			{'field': 'sum_money', 'uid': payUid, 'expected': 0},
		],
	),
]


@Retry(max_n=3)
class TestPayCreate(SlpTestBase):

	def test_001(self, des='房间内打赏多人(gs+normal)多礼物场景'):
		"""
		用例描述：
		验证非直播类型房间内一对多打赏场景
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间内一对多打赏流程
		3.校验接口状态和返回值数据
		4.检查打赏者余额,预期为：20000-1000*6*3 = 2000
		5.检查被打赏者余额，预期为：1000*6*0.62 = 3720(非一代宗师) 1000*6*0.7=4200(一代宗师) 1000*6*0.62=3720（公会）
		"""
		self.run_case(SCENES[0])
