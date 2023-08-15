# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "打赏多人多礼物"

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

	def test_01_RoomToMorePayChange(self, des='房间内打赏多人(gs+normal)多礼物场景'):
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
		rid = gs_B_ceo_rid
		uids = tuple([str(i) for i in [gs_A_uid, gs_B_uid, normal_uid]])
		num = 5
		mysql.updateUserGodSql(gs_A_uid, 0)
		mysql.updateUserGodSql(gs_B_uid, 1)
		mysql.updateMoneySql(payUid, giftId['69']['price'] * num * len(uids))
		mysql.updateUserMoneyClearSql(gs_A_uid, gs_B_uid, normal_uid)
		data = encodeData(
			rid=rid,
			payType='package-more',
			num=num,
			uids=uids
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'], 200)
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', gs_A_uid), giftId['69']['price'] * rates['gs']['default'] * num)
		assert_equal(mysql.selectUserInfoSql('single_money', gs_B_uid, money_type='money_cash'), giftId['69']['price'] * rates['gs']['default'] * num)
		assert_equal(mysql.selectUserInfoSql('single_money', normal_uid), giftId['69']['price'] * rates['normal']['default'] * num)
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), 0)
		case_list[des] = result
