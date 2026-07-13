# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "异常/边界值用例"

import unittest

from caseSlp.config import default_money, default_num, giftId, normal_uid, payUid, pay_url
from common.Assert import assert_code, assert_equal, assert_body
from common.Consts import case_list, result
from common.Request import post_request_session
from common.basicSlpData import encodeData
from common.conSlpMysql import conMysql as mysql
from common.runFailed import Retry
from common.sqlScript import UserMoneyOperations
from common.method import format_reason


@Retry(max_n=3)
class TestPayCreate(unittest.TestCase):
	"""异常/边界值用例数据驱动测试"""

	BALANCE_CASES = [
		# (描述, 余额, payType, 预期success, 是否断言余额不足msg)
		('余额=0,私聊打赏的场景', 0, 'chat-gift', 0, True),
		('余额=0,房间打赏的场景', 0, 'package', 0, True),
		('余额<礼物价值-私聊打赏的场景', giftId['69']['price'] - 1, 'chat-gift', 0, True),
		('余额<礼物价值-房间打赏的场景', giftId['69']['price'] - 1, 'package', 0, True),
		('余额=礼物价值-私聊打赏的场景', giftId['69']['price'], 'chat-gift', 1, False),
		('余额=礼物价值-房间打赏的场景', giftId['69']['price'], 'package', 1, False),
	]

	def _run_balance_case(self, des, balance, pay_type, expected_success, check_insufficient):
		"""单条余额边界值用例执行逻辑"""
		mysql.updateUserMoneyClearSql(payUid, normal_uid)
		if balance > 0:
			UserMoneyOperations.update(payUid, balance)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		data = encodeData(payType=pay_type, num=default_num, giftId=giftId['69']['gid'])
		res = post_request_session(pay_url, data, token_name='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', expected_success, format_reason(des, res))
		if check_insufficient:
			assert_body(res['body'], 'msg', '余额不足，无法支付', format_reason(des, res))
			assert_equal(mysql.selectUserInfoSql('sum_money', normal_uid), 0)
		else:
			assert_equal(mysql.selectUserInfoSql('sum_money', payUid), 0)
		case_list[des] = result

	def test_balance_all(self, des='不同余额边界值下打赏场景组合'):
		"""数据驱动：覆盖余额=0/不足/恰好时的私聊和房间打赏场景"""
		for case_des, balance, pay_type, expected_success, check_insufficient in self.BALANCE_CASES:
			with self.subTest(des=case_des, balance=balance, pay_type=pay_type):
				self._run_balance_case(case_des, balance, pay_type, expected_success, check_insufficient)

	def test_007(self, des='验证扣费顺序,money>mcb>mc'):
		"""验证扣费顺序：money优先扣，其次mcb，最后mc"""
		mysql.updateUserMoneyClearSql(payUid, normal_uid)
		UserMoneyOperations.update(payUid,
		                     money=giftId['69']['price'],
		                     money_cash_b=giftId['69']['price'],
		                     money_cash=giftId['69']['price'])
		mysql.deleteUserAccountSql('user_commodity', payUid)
		data = encodeData(payType='package', num=default_num, giftId=giftId['69']['gid'])
		res = post_request_session(pay_url, data, token_name='slp')
		assert_code(res['code'])
		assert_body(res['body'],'success', 1, format_reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', payUid, money_type='money'), 0)
		assert_equal(mysql.selectUserInfoSql('single_money', payUid, money_type='money_cash_b'), giftId['69']['price'])
		assert_equal(mysql.selectUserInfoSql('single_money', payUid, money_type='money_cash'), giftId['69']['price'])
		case_list[des] = result

	def test_008(self, des='验证扣费顺序,mcb>mc'):
		"""验证扣费顺序：money=0时，mcb优先扣，最后mc"""
		mysql.updateUserMoneyClearSql(payUid, normal_uid)
		UserMoneyOperations.update(payUid,
		                     money=0,
		                     money_cash_b=giftId['69']['price'],
		                     money_cash=giftId['69']['price'])
		mysql.deleteUserAccountSql('user_commodity', payUid)
		data = encodeData(payType='package', num=default_num, giftId=giftId['69']['gid'])
		res = post_request_session(pay_url, data, token_name='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, format_reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', payUid, money_type='money'), 0)
		assert_equal(mysql.selectUserInfoSql('single_money', payUid, money_type='money_cash_b'), 0)
		assert_equal(mysql.selectUserInfoSql('single_money', payUid, money_type='money_cash'), giftId['69']['price'])
		case_list[des] = result

	def test_009(self, des='验证组合支付,m,mc,mcb同时扣费的场景'):
		"""验证组合支付：三种货币同时扣费"""
		num = 3
		mysql.updateUserMoneyClearSql(payUid, normal_uid)
		UserMoneyOperations.update(payUid,
		                     money=giftId['69']['price'],
		                     money_cash_b=giftId['69']['price'],
		                     money_cash=giftId['69']['price'])
		mysql.deleteUserAccountSql('user_commodity', payUid)
		data = encodeData(
			money=giftId['69']['price'] * num,
			payType='package',
			num=num,
			giftId=giftId['69']['gid']
		)
		res = post_request_session(pay_url, data, token_name='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, format_reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', payUid, money_type='money'), 0)
		assert_equal(mysql.selectUserInfoSql('single_money', payUid, money_type='money_cash_b'), 0)
		assert_equal(mysql.selectUserInfoSql('single_money', payUid, money_type='money_cash'), 0)
		case_list[des] = result

	def test_010(self, des='api,自己打赏自己'):
		"""验证不能给自己打赏"""
		mysql.updateUserMoneyClearSql(payUid)
		UserMoneyOperations.update(payUid, money=default_money)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		data = encodeData(payType='chat-gift',
		                  num=default_num,
		                  uid=payUid,
		                  giftId=giftId['69']['gid'])
		res = post_request_session(pay_url, data, token_name='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 0, format_reason(des, res))
		assert_body(res['body'], 'msg', '不能给自己打赏', format_reason(des, res))
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money)
		case_list[des] = result
