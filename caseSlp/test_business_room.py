# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "商业房房主"

import time
import unittest

from caseSlp.config import *
from common.Assert import assert_code, assert_equal, assert_body
from common.Consts import case_list, result, case_list_b
from common.Request import post_request_session
from common.basicSlpData import encodeData
from common.conSlpMysql import conMysql as mysql
from common.method import reason
from common.runFailed import Retry


@Retry(max_n=3)
class TestPayCreate(unittest.TestCase):

	def test_001(self, des='商业房-房主,在自己房内,到账60%(mc)'):
		"""
		用例描述：
		商业房-房主,在自己房内,,到账60%(mc)
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash)
		"""
		rid = business_room_rid
		uid = busine_room_uid
		mysql.updateMoneySql(payUid, default_money)
		mysql.updateMoneySql(uid)
		mysql.updateUserGodSql(uid, 1)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		data = encodeData(
			rid=rid,
			payType='package',
			uid=uid,
			giftId=giftId['69']['gid']
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', uid, money_type='money_cash'),
		             giftId['69']['price'] * default_num * rates['gs']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', uid), giftId['69']['price'] * default_num * rates['gs']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money - giftId['69']['price'] * default_num)
		case_list_b[des] = result

	def test_002(self, des='商业房-房主,不在自己房内,到账60%(mcb)'):
		"""
		用例描述：
		商业房-房主,在自己房内,,到账60%(mc)
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash)
		"""
		rid = gs_A_ceo_rid
		uid = busine_room_uid
		mysql.updateMoneySql(payUid, default_money)
		mysql.updateMoneySql(uid)
		mysql.updateUserGodSql(uid, 1)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		data = encodeData(
			rid=rid,
			payType='package',
			uid=uid,
			giftId=giftId['69']['gid']
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', uid, money_type='money_cash_b'),
		             giftId['69']['price'] * default_num * rates['gs']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', uid), giftId['69']['price'] * default_num * rates['gs']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money - giftId['69']['price'] * default_num)
		case_list_b[des] = result
