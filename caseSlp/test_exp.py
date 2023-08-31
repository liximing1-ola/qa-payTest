# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "经验值相关用例"

import time
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

	def test_001(self, des='打赏者,贵族爵位=骑士(lv1,1倍)消费,vip经验值1:1增加'):
		"""
		用例描述：
		验证余额足够时，商业房打赏礼物给GS分成为：60，且收入在公会魅力值
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash)
		"""
		rid = business_room_rid
		uid = normal_uid
		mysql.deleteUserAccountSql('user_title_new', payUid)  # 关闭贵族,还原数据
		mysql.deleteUserAccountSql('pay_room_money', payUid)  # 修改vip值,还原数据
		mysql.updateUserInfoSql('user_title_new', payUid, level=juewei_level['骑士']['level'])
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
		time.sleep(0.5)
		assert_equal(mysql.selectUserInfoSql('pay_room_money', payUid), old_vip + juewei_level['骑士']['update'] * giftId['69']['price']/100)
		assert_equal(mysql.selectUserInfoSql('popularity', uid), old_pop + giftId['69']['price'])
		case_list_b[des] = result

	def test_002(self, des='打赏者,贵族爵位=男爵(lv1,1倍)消费,vip经验值1:1增加'):
		"""
		用例描述：
		验证余额足够时，商业房打赏礼物给GS分成为：60，且收入在公会魅力值
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash)
		"""
		rid = business_room_rid
		uid = normal_uid
		mysql.deleteUserAccountSql('user_title_new', payUid)  # 关闭贵族,还原数据
		mysql.deleteUserAccountSql('pay_room_money', payUid)  # 修改vip值,还原数据
		mysql.updateUserInfoSql('user_title_new', payUid, level=juewei_level['男爵']['level'])
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
		time.sleep(0.5)
		assert_equal(mysql.selectUserInfoSql('pay_room_money', payUid), old_vip + juewei_level['男爵']['update'] * giftId['69']['price']/100)
		assert_equal(mysql.selectUserInfoSql('popularity', uid), old_pop + giftId['69']['price'])
		case_list_b[des] = result

	def test_003(self, des='打赏者,贵族爵位=子爵(lv1,1倍)消费,vip经验值1:1增加'):
		"""
		用例描述：
		验证余额足够时，商业房打赏礼物给GS分成为：60，且收入在公会魅力值
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash)
		"""
		rid = business_room_rid
		uid = normal_uid
		mysql.deleteUserAccountSql('user_title_new', payUid)  # 关闭贵族,还原数据
		mysql.deleteUserAccountSql('pay_room_money', payUid)  # 修改vip值,还原数据
		mysql.updateUserInfoSql('user_title_new', payUid, level=juewei_level['子爵']['level'])
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
		time.sleep(0.5)
		assert_equal(mysql.selectUserInfoSql('pay_room_money', payUid), old_vip + juewei_level['子爵']['update'] * giftId['69']['price']/100)
		assert_equal(mysql.selectUserInfoSql('popularity', uid), old_pop + giftId['69']['price'])
		case_list_b[des] = result

	def test_004(self, des='打赏者,贵族爵位=伯爵(lv4,1.05倍)消费,vip经验值1:1.05增加'):
		"""
		用例描述：
		验证余额足够时，商业房打赏礼物给GS分成为：60，且收入在公会魅力值
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash)
		"""
		rid = business_room_rid
		uid = normal_uid
		mysql.deleteUserAccountSql('user_title_new', payUid)  # 关闭贵族,还原数据
		mysql.deleteUserAccountSql('pay_room_money', payUid)  # 修改vip值,还原数据
		mysql.updateUserInfoSql('user_title_new', payUid, level=juewei_level['伯爵']['level'])
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
		time.sleep(0.5)
		assert_equal(mysql.selectUserInfoSql('pay_room_money', payUid), old_vip + juewei_level['伯爵']['update'] * giftId['69']['price']/100)
		assert_equal(mysql.selectUserInfoSql('popularity', uid), old_pop + giftId['69']['price'])
		case_list_b[des] = result

	def test_005(self, des='打赏者,贵族爵位=侯爵(lv4,1.1倍)消费,vip经验值1:1.1增加'):
		"""
		用例描述：
		验证余额足够时，商业房打赏礼物给GS分成为：60，且收入在公会魅力值
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash)
		"""
		rid = business_room_rid
		uid = normal_uid
		mysql.deleteUserAccountSql('user_title_new', payUid)  # 关闭贵族,还原数据
		mysql.deleteUserAccountSql('pay_room_money', payUid)  # 修改vip值,还原数据
		mysql.updateUserInfoSql('user_title_new', payUid, level=juewei_level['侯爵']['level'])
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
		time.sleep(0.5)
		assert_equal(mysql.selectUserInfoSql('pay_room_money', payUid), old_vip + juewei_level['侯爵']['update'] * giftId['69']['price']/100)
		assert_equal(mysql.selectUserInfoSql('popularity', uid), old_pop + giftId['69']['price'])
		case_list_b[des] = result

	def test_006(self, des='打赏者,贵族爵位=公爵(lv4,1.15倍)消费,vip经验值1:1.15增加'):
		"""
		用例描述：
		验证余额足够时，商业房打赏礼物给GS分成为：60，且收入在公会魅力值
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash)
		"""
		rid = business_room_rid
		uid = normal_uid
		mysql.deleteUserAccountSql('user_title_new', payUid)  # 关闭贵族,还原数据
		mysql.deleteUserAccountSql('pay_room_money', payUid)  # 修改vip值,还原数据
		mysql.updateUserInfoSql('user_title_new', payUid, level=juewei_level['公爵']['level'])
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
		time.sleep(0.5)
		assert_equal(mysql.selectUserInfoSql('pay_room_money', payUid), old_vip + juewei_level['公爵']['update'] * giftId['69']['price']/100)
		assert_equal(mysql.selectUserInfoSql('popularity', uid), old_pop + giftId['69']['price'])
		case_list_b[des] = result

	def test_007(self, des='打赏者,贵族爵位=亲王(lv4,1.2倍)消费,vip经验值1:1.2增加'):
		"""
		用例描述：
		验证余额足够时，商业房打赏礼物给GS分成为：60，且收入在公会魅力值
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash)
		"""
		rid = business_room_rid
		uid = normal_uid
		mysql.deleteUserAccountSql('user_title_new', payUid)  # 关闭贵族,还原数据
		mysql.deleteUserAccountSql('pay_room_money', payUid)  # 修改vip值,还原数据
		mysql.updateUserInfoSql('user_title_new', payUid, level=juewei_level['亲王']['level'])
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
		time.sleep(0.5)
		assert_equal(mysql.selectUserInfoSql('pay_room_money', payUid), old_vip + juewei_level['亲王']['update'] * giftId['69']['price']/100)
		assert_equal(mysql.selectUserInfoSql('popularity', uid), old_pop + giftId['69']['price'])
		case_list_b[des] = result

	def test_008(self, des='打赏者,贵族爵位=国王(lv4,1.25倍)消费,vip经验值1:1.25增加'):
		"""
		用例描述：
		验证余额足够时，商业房打赏礼物给GS分成为：60，且收入在公会魅力值
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash)
		"""
		rid = business_room_rid
		uid = normal_uid
		mysql.deleteUserAccountSql('user_title_new', payUid)  # 关闭贵族,还原数据
		mysql.deleteUserAccountSql('pay_room_money', payUid)  # 修改vip值,还原数据
		mysql.updateUserInfoSql('user_title_new', payUid, level=juewei_level['国王']['level'])
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
		time.sleep(0.5)
		assert_equal(mysql.selectUserInfoSql('pay_room_money', payUid), old_vip + juewei_level['国王']['update'] * giftId['69']['price']/100)
		assert_equal(mysql.selectUserInfoSql('popularity', uid), old_pop + giftId['69']['price'])
		case_list_b[des] = result

	def test_009(self, des='打赏者,贵族爵位=皇帝(lv4,1.3倍)消费,vip经验值1:1.3增加'):
		"""
		用例描述：
		验证余额足够时，商业房打赏礼物给GS分成为：60，且收入在公会魅力值
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash)
		"""
		rid = business_room_rid
		uid = normal_uid
		mysql.deleteUserAccountSql('user_title_new', payUid)  # 关闭贵族,还原数据
		mysql.deleteUserAccountSql('pay_room_money', payUid)  # 修改vip值,还原数据
		mysql.updateUserInfoSql('user_title_new', payUid, level=juewei_level['皇帝']['level'])
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
		time.sleep(0.5)
		assert_equal(mysql.selectUserInfoSql('pay_room_money', payUid), old_vip + juewei_level['皇帝']['update'] * giftId['69']['price']/100)
		assert_equal(mysql.selectUserInfoSql('popularity', uid), old_pop + giftId['69']['price'])
		case_list_b[des] = result
