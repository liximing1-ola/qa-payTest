# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "异常/边界值用例"

from caseSlp.base import SlpCase, SlpTestBase
from caseSlp.config import default_money, default_num, giftId, normal_uid, payUid
from common.runFailed import Retry


def _make_balance_case(des, balance, pay_type, expected_success, check_insufficient):
	"""构造单条余额边界值场景"""
	setup = [{'action': 'clear_user_money', 'uids': [payUid, normal_uid]}]
	if balance > 0:
		setup.append({'action': 'update_money', 'params': {'uid': payUid, 'money': balance}})
	setup.append({'action': 'delete_commodity', 'uid': payUid})

	if check_insufficient:
		msg = '余额不足，无法支付'
		checks = [{'field': 'sum_money', 'uid': normal_uid, 'expected': 0}]
	else:
		msg = None
		checks = [{'field': 'sum_money', 'uid': payUid, 'expected': 0}]

	return SlpCase(
		des=des,
		setup=setup,
		data={'payType': pay_type, 'num': default_num, 'gift_id': giftId['69']['gid']},
		success=expected_success,
		msg=msg,
		checks=checks,
	)


BALANCE_CASES = [
	# (描述, 余额, payType, 预期success, 是否断言余额不足msg)
	('余额=0,私聊打赏的场景', 0, 'chat-gift', 0, True),
	('余额=0,房间打赏的场景', 0, 'package', 0, True),
	('余额<礼物价值-私聊打赏的场景', giftId['69']['price'] - 1, 'chat-gift', 0, True),
	('余额<礼物价值-房间打赏的场景', giftId['69']['price'] - 1, 'package', 0, True),
	('余额=礼物价值-私聊打赏的场景', giftId['69']['price'], 'chat-gift', 1, False),
	('余额=礼物价值-房间打赏的场景', giftId['69']['price'], 'package', 1, False),
]

BALANCE_SCENES = [_make_balance_case(*case) for case in BALANCE_CASES]

# 场景：验证扣费顺序,money>mcb>mc
SCENE_007 = SlpCase(
	des='验证扣费顺序,money>mcb>mc',
	setup=[
		{'action': 'clear_user_money', 'uids': [payUid, normal_uid]},
		{'action': 'update_money', 'params': {'uid': payUid, 'money': giftId['69']['price'],
		                                      'money_cash_b': giftId['69']['price'],
		                                      'money_cash': giftId['69']['price']}},
		{'action': 'delete_commodity', 'uid': payUid},
	],
	data={'payType': 'package', 'num': default_num, 'gift_id': giftId['69']['gid']},
	checks=[
		{'field': 'single_money', 'uid': payUid, 'money_type': 'money', 'expected': 0},
		{'field': 'single_money', 'uid': payUid, 'money_type': 'money_cash_b',
		 'expected': giftId['69']['price']},
		{'field': 'single_money', 'uid': payUid, 'money_type': 'money_cash',
		 'expected': giftId['69']['price']},
	],
)

# 场景：验证扣费顺序,mcb>mc
SCENE_008 = SlpCase(
	des='验证扣费顺序,mcb>mc',
	setup=[
		{'action': 'clear_user_money', 'uids': [payUid, normal_uid]},
		{'action': 'update_money', 'params': {'uid': payUid, 'money': 0,
		                                      'money_cash_b': giftId['69']['price'],
		                                      'money_cash': giftId['69']['price']}},
		{'action': 'delete_commodity', 'uid': payUid},
	],
	data={'payType': 'package', 'num': default_num, 'gift_id': giftId['69']['gid']},
	checks=[
		{'field': 'single_money', 'uid': payUid, 'money_type': 'money', 'expected': 0},
		{'field': 'single_money', 'uid': payUid, 'money_type': 'money_cash_b', 'expected': 0},
		{'field': 'single_money', 'uid': payUid, 'money_type': 'money_cash',
		 'expected': giftId['69']['price']},
	],
)

# 组合支付场景的礼物数量
_NUM = 3

# 场景：验证组合支付,m,mc,mcb同时扣费的场景
SCENE_009 = SlpCase(
	des='验证组合支付,m,mc,mcb同时扣费的场景',
	setup=[
		{'action': 'clear_user_money', 'uids': [payUid, normal_uid]},
		{'action': 'update_money', 'params': {'uid': payUid, 'money': giftId['69']['price'],
		                                      'money_cash_b': giftId['69']['price'],
		                                      'money_cash': giftId['69']['price']}},
		{'action': 'delete_commodity', 'uid': payUid},
	],
	data={'money': giftId['69']['price'] * _NUM, 'payType': 'package', 'num': _NUM,
	      'gift_id': giftId['69']['gid']},
	checks=[
		{'field': 'single_money', 'uid': payUid, 'money_type': 'money', 'expected': 0},
		{'field': 'single_money', 'uid': payUid, 'money_type': 'money_cash_b', 'expected': 0},
		{'field': 'single_money', 'uid': payUid, 'money_type': 'money_cash', 'expected': 0},
	],
)

# 场景：api,自己打赏自己
SCENE_010 = SlpCase(
	des='api,自己打赏自己',
	setup=[
		{'action': 'clear_user_money', 'uids': [payUid]},
		{'action': 'update_money', 'params': {'uid': payUid, 'money': default_money}},
		{'action': 'delete_commodity', 'uid': payUid},
	],
	data={'payType': 'chat-gift', 'num': default_num, 'uid': payUid,
	      'gift_id': giftId['69']['gid']},
	success=0,
	msg='不能给自己打赏',
	checks=[{'field': 'sum_money', 'uid': payUid, 'expected': default_money}],
)


@Retry(max_n=3)
class TestPayCreate(SlpTestBase):
	"""异常/边界值用例数据驱动测试"""

	def test_balance_all(self, des='不同余额边界值下打赏场景组合'):
		"""数据驱动：覆盖余额=0/不足/恰好时的私聊和房间打赏场景"""
		for scene in BALANCE_SCENES:
			with self.subTest(des=scene.des):
				self.run_case(scene)

	def test_007(self, des='验证扣费顺序,money>mcb>mc'):
		"""验证扣费顺序：money优先扣，其次mcb，最后mc"""
		self.run_case(SCENE_007)

	def test_008(self, des='验证扣费顺序,mcb>mc'):
		"""验证扣费顺序：money=0时，mcb优先扣，最后mc"""
		self.run_case(SCENE_008)

	def test_009(self, des='验证组合支付,m,mc,mcb同时扣费的场景'):
		"""验证组合支付：三种货币同时扣费"""
		self.run_case(SCENE_009)

	def test_010(self, des='api,自己打赏自己'):
		"""验证不能给自己打赏"""
		self.run_case(SCENE_010)
