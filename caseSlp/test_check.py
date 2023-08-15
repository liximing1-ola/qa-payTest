# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "异常/边界值用例"

import unittest

from caseSlp.config import *
from common.Assert import assert_code, assert_equal, assert_body
from common.Consts import case_list, result
from common.Request import post_request_session
from common.basicSlpData import encodeData
from common.conSlpMysql import conMysql as mysql
from common.method import reason
from common.runFailed import Retry


@Retry(max_n=3)
class TestPayCreate(unittest.TestCase):
	def test_01_chatPayNoMoney(self, des='余额=0,私聊打赏的场景'):
		"""
		用例描述：
		检查账户余额不足时，私聊一对一打赏
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.私聊一对一打赏流程(礼物:棒棒糖)
		3.校验接口和返回值数据
		4.检查预期返回msg，预期：支付失败，提示Toast
		5.检查被打赏者余额,预期：0
		"""
		mysql.updateUserMoneyClearSql(payUid, normal_uid)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		# mysql.deleteUserAccountSql('broker_user', normal_uid)
		# mysql.deleteUserAccountSql('chatroom', normal_uid)
		data = encodeData(payType='chat-gift',
		                  num=default_num,
		                  giftId=giftId['69']['gid'])
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 0, reason(des, res))
		assert_body(res['body'], 'msg', '余额不足，无法支付', reason(des, res))
		assert_equal(mysql.selectUserInfoSql('sum_money', normal_uid), 0)
		case_list[des] = result

	def test_02_roomPayNoMoney(self, des='余额=0,房间打赏的场景'):
		"""
		用例描述：
		检查账户余额不足时，房间打赏
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.私聊一对一打赏流程(礼物:棒棒糖)
		3.校验接口和返回值数据
		4.检查预期返回msg，预期：支付失败，提示Toast
		5.检查被打赏者余额,预期：0
		"""
		mysql.updateUserMoneyClearSql(payUid, normal_uid)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		# mysql.deleteUserAccountSql('broker_user', normal_uid)
		# mysql.deleteUserAccountSql('chatroom', normal_uid)
		data = encodeData(payType='package',
		                  num=default_num,
		                  giftId=giftId['69']['gid'])
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 0, reason(des, res))
		assert_body(res['body'], 'msg', '余额不足，无法支付', reason(des, res))
		assert_equal(mysql.selectUserInfoSql('sum_money', normal_uid), 0)
		case_list[des] = result

	def test_03_chatPayNoMoney(self, des='余额<礼物价值-私聊打赏的场景'):
		"""
		用例描述：
		余额<礼物价值-私聊打赏的场景
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.私聊一对一打赏流程(礼物:棒棒糖)
		3.校验接口和返回值数据
		4.检查预期返回msg，预期：支付失败，提示Toast
		5.检查被打赏者余额,预期：0
		"""
		mysql.updateUserMoneyClearSql(payUid, normal_uid)
		mysql.updateMoneySql(payUid, giftId['69']['price'] - 1)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		# mysql.deleteUserAccountSql('broker_user', normal_uid)
		# mysql.deleteUserAccountSql('chatroom', normal_uid)
		data = encodeData(payType='chat-gift',
		                  num=default_num,
		                  giftId=giftId['69']['gid'])
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 0, reason(des, res))
		assert_body(res['body'], 'msg', '余额不足，无法支付', reason(des, res))
		assert_equal(mysql.selectUserInfoSql('sum_money', normal_uid), 0)
		case_list[des] = result

	def test_04_roomPayNoMoney(self, des='余额<礼物价值-房间打赏的场景'):
		"""
		用例描述：
		检查账户余额不足时，房间打赏
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.私聊一对一打赏流程(礼物:棒棒糖)
		3.校验接口和返回值数据
		4.检查预期返回msg，预期：支付失败，提示Toast
		5.检查被打赏者余额,预期：0
		"""
		mysql.updateUserMoneyClearSql(payUid, normal_uid)
		mysql.updateMoneySql(payUid, giftId['69']['price'] - 1)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		# mysql.deleteUserAccountSql('broker_user', normal_uid)
		# mysql.deleteUserAccountSql('chatroom', normal_uid)
		data = encodeData(payType='package',
		                  num=default_num,
		                  giftId=giftId['69']['gid'])
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 0, reason(des, res))
		assert_body(res['body'], 'msg', '余额不足，无法支付', reason(des, res))
		assert_equal(mysql.selectUserInfoSql('sum_money', normal_uid), 0)
		case_list[des] = result

	def test_05_chatPayNoMoney(self, des='余额=礼物价值-私聊打赏的场景'):
		"""
		用例描述：
		余额=礼物价值-私聊打赏的场景
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.私聊一对一打赏流程(礼物:棒棒糖)
		3.校验接口和返回值数据
		4.检查预期返回msg，预期：支付失败，提示Toast
		5.检查被打赏者余额,预期：0
		"""
		mysql.updateUserMoneyClearSql(payUid, normal_uid)
		mysql.updateMoneySql(payUid, giftId['69']['price'])
		mysql.deleteUserAccountSql('user_commodity', payUid)
		# mysql.deleteUserAccountSql('broker_user', normal_uid)
		# mysql.deleteUserAccountSql('chatroom', normal_uid)
		data = encodeData(payType='chat-gift',
		                  num=default_num,
		                  giftId=giftId['69']['gid'])
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), 0)
		case_list[des] = result

	def test_06_roomPayNoMoney(self, des='余额=礼物价值-房间打赏的场景'):
		"""
		用例描述：
		余额=礼物价值-房间打赏的场景
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.私聊一对一打赏流程(礼物:棒棒糖)
		3.校验接口和返回值数据
		4.检查预期返回msg，预期：支付失败，提示Toast
		5.检查被打赏者余额,预期：0
		"""
		mysql.updateUserMoneyClearSql(payUid, normal_uid)
		mysql.updateMoneySql(payUid, giftId['69']['price'])
		mysql.deleteUserAccountSql('user_commodity', payUid)
		# mysql.deleteUserAccountSql('broker_user', normal_uid)
		# mysql.deleteUserAccountSql('chatroom', normal_uid)
		data = encodeData(payType='package',
		                  num=default_num,
		                  giftId=giftId['69']['gid'])
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), 0)
		case_list[des] = result

	def test_07_roomPayNoMoney(self, des='验证扣费顺序,money>mcb>mc'):
		"""
		用例描述：
		验证扣费顺序,money>mcb>mc
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.私聊一对一打赏流程(礼物:棒棒糖)
		3.校验接口和返回值数据
		4.检查预期返回msg，预期：支付失败，提示Toast
		5.检查被打赏者余额,预期：0
		"""
		mysql.updateUserMoneyClearSql(payUid, normal_uid)
		mysql.updateMoneySql(payUid,
		                     money=giftId['69']['price'],
		                     money_cash_b=giftId['69']['price'],
		                     money_cash=giftId['69']['price'])
		mysql.deleteUserAccountSql('user_commodity', payUid)
		# mysql.deleteUserAccountSql('broker_user', normal_uid)
		# mysql.deleteUserAccountSql('chatroom', normal_uid)
		data = encodeData(payType='package',
		                  num=default_num,
		                  giftId=giftId['69']['gid'])
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		# money>mcb>mc
		assert_equal(mysql.selectUserInfoSql('single_money', payUid, money_type='money'), 0)
		assert_equal(mysql.selectUserInfoSql('single_money', payUid, money_type='money_cash_b'), giftId['69']['price'])
		assert_equal(mysql.selectUserInfoSql('single_money', payUid, money_type='money_cash'), giftId['69']['price'])

	def test_08_roomPayNoMoney(self, des='验证扣费顺序,mcb>mc'):
		"""
		用例描述：
		验证扣费顺序,money>mcb>mc
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.私聊一对一打赏流程(礼物:棒棒糖)
		3.校验接口和返回值数据
		4.检查预期返回msg，预期：支付失败，提示Toast
		5.检查被打赏者余额,预期：0
		"""
		mysql.updateUserMoneyClearSql(payUid, normal_uid)
		mysql.updateMoneySql(payUid,
		                     money=0,
		                     money_cash_b=giftId['69']['price'],
		                     money_cash=giftId['69']['price'])
		mysql.deleteUserAccountSql('user_commodity', payUid)
		# mysql.deleteUserAccountSql('broker_user', normal_uid)
		# mysql.deleteUserAccountSql('chatroom', normal_uid)
		data = encodeData(payType='package',
		                  num=default_num,
		                  giftId=giftId['69']['gid'])
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		# mcb > mc
		assert_equal(mysql.selectUserInfoSql('single_money', payUid, money_type='money'), 0)
		assert_equal(mysql.selectUserInfoSql('single_money', payUid, money_type='money_cash_b'), 0)
		assert_equal(mysql.selectUserInfoSql('single_money', payUid, money_type='money_cash'), giftId['69']['price'])
		case_list[des] = result

	def test_09_roomPayNoMoney(self, des='验证组合支付,m,mc,mcb同时扣费的场景'):
		"""
		用例描述：
		验证扣费顺序,money>mcb>mc
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.私聊一对一打赏流程(礼物:棒棒糖)
		3.校验接口和返回值数据
		4.检查预期返回msg，预期：支付失败，提示Toast
		5.检查被打赏者余额,预期：0
		"""
		num=3
		mysql.updateUserMoneyClearSql(payUid, normal_uid)
		mysql.updateMoneySql(payUid,
		                     money=giftId['69']['price'],
		                     money_cash_b=giftId['69']['price'],
		                     money_cash=giftId['69']['price'])
		mysql.deleteUserAccountSql('user_commodity', payUid)
		# mysql.deleteUserAccountSql('broker_user', normal_uid)
		# mysql.deleteUserAccountSql('chatroom', normal_uid)
		data = encodeData(
			money=giftId['69']['price'] * num,
			payType='package',
			num=num,
			giftId=giftId['69']['gid']
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', payUid, money_type='money'), 0)
		assert_equal(mysql.selectUserInfoSql('single_money', payUid, money_type='money_cash_b'), 0)
		assert_equal(mysql.selectUserInfoSql('single_money', payUid, money_type='money_cash'), 0)

		case_list[des] = result
