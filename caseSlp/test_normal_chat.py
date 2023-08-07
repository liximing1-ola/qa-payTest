# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "普通用户-私聊"

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

	def test_01_chatPayNoMoney(self, des='私聊打赏余额不足的场景'):
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
		# mysql.deleteUserAccountSql('broker_user', normal_uid)
		# mysql.deleteUserAccountSql('chatroom', normal_uid)
		data = encodeData(payType='chat-gift',
		                  num=default_num,
		                  giftId=giftId['5'])
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 0, reason(des, res))
		assert_body(res['body'], 'msg', '余额不足，无法支付', reason(des, res))
		assert_equal(mysql.selectUserInfoSql('sum_money', normal_uid), 0)
		case_list[des] = result

	def test_02_chatPay(self, des='私聊打赏分成60%进mcb'):
		"""
		用例描述：
		私聊打赏分成60%进mcb
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.私聊一对一打赏流程(礼物:棒棒糖)
		3.校验接口和返回值数据
        4.检查被打赏者余额和账户，预期为：50 * 0.6 = 30(mcb)
        5.检查打赏者余额.预期为：1000 - 50 = 950
		"""
		mysql.updateMoneySql(payUid, money=default_money)
		mysql.updateUserMoneyClearSql(normal_uid)
		# mysql.deleteUserAccountSql('broker_user', normal_uid)
		# mysql.deleteUserAccountSql('chatroom', normal_uid)
		data = encodeData(payType='chat-gift',
		                  num=default_num,
		                  giftId=giftId['5'])
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', normal_uid),
		             default_money * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid),
		             default_money - giftId['5'] * default_num)
		case_list[des] = result
