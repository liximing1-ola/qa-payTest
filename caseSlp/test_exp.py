# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "经验值相关用例"
import unittest

from caseSlp.config import *
from common.Assert import assert_code, assert_equal, assert_body
from common.Consts import case_list_b, result
from common.Request import post_request_session
from common.basicSlpData import encodeData
from common.conSlpMysql import conMysql as mysql
from common.method import reason
from common.runFailed import Retry


@Retry(max_n=3)
class TestPayCreate(unittest.TestCase):

	def test_01_businessPayGiftToGs(self, des='打赏者,贵族爵位=骑士(lv1,1倍)消费,vip经验值1:1增加'):
		"""
		用例描述：
		验证余额足够时，商业房打赏礼物给GS分成为：60，且收入在公会魅力值
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash)
		"""
		rid = normal_rid
		uid = normal_uid
		mysql.deleteUserAccountSql('user_title_new', payUid)  # 关闭贵族,还原数据
		mysql.updateUserInfoSql('user_title_new', payUid)  # 开通贵族
		mysql.updateUserInfoSql('level', payUid, level=juewei_level['骑士']['level'])  # 修改贵族等级
		mysql.updateMoneySql(payUid, default_money)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		old_vip = mysql.selectUserInfoSql('pay_room_money', payUid)
		old_pop = mysql.selectUserInfoSql('popularity', uid)
		data = encodeData(
			rid=rid,
			payType='package',
			uid=uid,
			giftId=giftId['69']['gid']
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('pay_room_money', payUid), old_vip + juewei_level['骑士']['update'] * giftId['69']['price'])
		assert_equal(mysql.selectUserInfoSql('popularity', uid), old_pop + giftId['69']['price'])
		case_list_b[des] = result

	def test_02_businessPayGiftToGs(self, des='打赏者,贵族爵位=伯爵(lv4,1.3倍)消费,vip经验值1:1.3增加'):
		"""
		用例描述：
		验证余额足够时，商业房打赏礼物给GS分成为：60，且收入在公会魅力值
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash)
		"""
		rid = normal_rid
		uid = normal_uid
		mysql.deleteUserAccountSql('user_title_new', payUid)  # 关闭贵族,还原数据
		mysql.updateUserInfoSql('user_title_new', payUid)  # 开通贵族
		mysql.updateUserInfoSql('level', payUid, level=juewei_level['伯爵']['level'])  # 修改贵族等级
		mysql.updateMoneySql(payUid, default_money)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		old_vip = mysql.selectUserInfoSql('pay_room_money', payUid)
		old_pop = mysql.selectUserInfoSql('popularity', uid)
		data = encodeData(
			rid=rid,
			payType='package',
			uid=uid,
			giftId=giftId['69']['gid']
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		import time
		time.sleep(2)
		assert_equal(mysql.selectUserInfoSql('pay_room_money', payUid), old_vip + juewei_level['伯爵']['update'] * giftId['69']['price'])
		assert_equal(mysql.selectUserInfoSql('popularity', uid), old_pop + giftId['69']['price'])
		case_list_b[des] = result