# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "公会主播-私聊"

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

	def test_01_chatPay(self, des='主播GS-私聊打赏分成60%(mc)'):
		"""
		用例描述：
		主播GS-私聊打赏分成60%进mc
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.私聊一对一打赏流程(礼物:棒棒糖)
		3.校验接口和返回值数据
        4.检查被打赏者余额和账户，预期为：50 * 0.6 = 30(mc)
        5.检查打赏者余额.预期为：1000 - 50 = 950
		"""
		uid = gsUid
		mysql.updateMoneySql(payUid, money=default_money)
		mysql.updateUserMoneyClearSql(uid)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		mysql.updateUserGodSql(uid, 1)
		# mysql.deleteUserAccountSql('broker_user', normal_uid)
		# mysql.deleteUserAccountSql('chatroom', normal_uid)
		data = encodeData(payType='chat-gift',
		                  num=default_num,
		                  uid=uid,
		                  giftId=giftId['69']['gid'])
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', uid, 'money_cash'),
		             giftId['69']['price'] * default_num * rates['gs']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid),
		             default_money - giftId['69']['price'] * default_num)
		case_list[des] = result
