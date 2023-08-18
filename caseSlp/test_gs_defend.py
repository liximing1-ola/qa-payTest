# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "公会主播-个人守护"

import unittest

import pytest

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
	@pytest.mark.run(order=1)
	def test_001(self, des='给GS开通个人守护场景60%(mc)'):
		"""
		用例描述：
		给GS开通个人守护场景60%(mc)
		脚本步骤：
		1.构造开通者和被守护者数据
		2.开通价值52000钻小宝贝守护（xs_relation_config id=2）
		3.校验接口状态和返回值数据
		4.检查打赏者余额
		5.检查被打赏者余额,预期：52000 * 0.62 = 32240
		"""
		uid = gsUid
		mysql.updateMoneySql(payUid, money=default_money)
		mysql.updateMoneySql(uid)
		mysql.updateUserGodSql(uid, 1)
		data = encodeData(
			uid=uid,
			payType='defend',
			defend_id=defend['小宝贝']['id'],
			money=defend['小宝贝']['price']
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money - defend['小宝贝']['price'])
		assert_equal(mysql.selectUserInfoSql('single_money', uid, money_type='money_cash'), defend['小宝贝']['price'] * rates['gs']['default'])
		case_list[des] = result

	@pytest.mark.run(order=2)
	def test_002(self, des='给GS开通个人守护进阶场景60%(mc)'):
		"""
		 用例描述：
		给GS开通个人守护进阶场景60(mc)
		 脚本步骤：
		 1.接test_01
		 2.购买进阶版（99900钻），黄金小宝贝对应进阶价格
		 3.校验接口状态和返回值数据
		 4.检查打赏者余额，预期：100000 - 99900 = 100
		 5.检查被打赏者余额,预期： 99900 * 0.62 = 61938
		 """
		uid = gsUid
		mysql.updateMoneySql(payUid, money=default_money)
		mysql.updateMoneySql(uid)
		mysql.updateUserGodSql(uid, 1)
		defend_id = mysql.selectUserInfoSql('relation_id', payuid=payUid, uid=uid, cid=defend['小宝贝']['id'])
		data = encodeData(
			uid=uid,
			payType='defend-upgrade',
			money=defend['小宝贝']['upgrade_price'],
			defend_id=defend_id
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money - defend['小宝贝']['upgrade_price'])
		assert_equal(mysql.selectUserInfoSql('single_money', uid, money_type='money_cash'), defend['小宝贝']['upgrade_price'] * rates['gs']['default'])
		case_list[des] = result

	@pytest.mark.run(order=3)
	def test_003(self, des='GS个人守护解除场景,不分成'):
		"""
		 用例描述：
		GS个人守护解除场景,不分成
		 脚本步骤：
		 1.接test_01，test_02
		 2.强制解除关系
		 3.校验接口状态和返回值数据
		 4.检查打赏者余额，预期：40000 - 36000 = 4000
		 """
		uid = gsUid
		mysql.updateMoneySql(payUid, money=default_money)
		mysql.updateMoneySql(uid)
		mysql.updateUserGodSql(uid, 1)
		mysql.selectUserInfoSql('relation_id', uid=uid, cid=defend['小宝贝']['id'])
		defend_id = mysql.selectUserInfoSql('relation_id', payuid=payUid, uid=uid, cid=defend['小宝贝']['id'])
		data = encodeData(
			uid=uid,
			payType='defend-break',
			money=defend['小宝贝']['break_price'],
			defend_id=defend_id
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money - defend['小宝贝']['break_price'])
		assert_equal(mysql.selectUserInfoSql('sum_money', uid), 0)
		case_list[des] = result
