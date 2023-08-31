# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "普通用户-房间打赏"

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

	def test_001(self, des='商业房-直播,礼物打赏普通用户到账60%(mcb)'):
		"""
		用例描述：
		验证余额足够时，商业房打赏礼物给普通用户分成为：60，且收入在公会魅力值
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash_b)
		"""
		rid = gs_soundchat_rid
		assert_equal(mysql.checkRidFactoryType(rid), "business-soundchat")  # 确认rid是直播房
		mysql.updateMoneySql(payUid, default_money)
		mysql.updateMoneySql(normal_uid)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		data = encodeData(
			rid=rid,
			payType='package',
			uid=normal_uid,
			giftId=giftId['69']['gid']
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', normal_uid),
		             giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', normal_uid), giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money - giftId['69']['price'] * default_num)
		case_list[des] = result

	def test_002(self, des='商业房-直播,房间私聊打赏普通用户到账60%(mcb)'):
		"""
		用例描述：
		验证余额足够时，商业房房间私聊打赏礼物给普通用户分成为：60，且收入在公会魅力值
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash_b)
		"""
		rid = gs_soundchat_rid
		assert_equal(mysql.checkRidFactoryType(rid), "business-soundchat")  # 确认rid是直播房
		mysql.updateMoneySql(payUid, default_money)
		mysql.updateMoneySql(normal_uid)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		data = encodeData(
			rid=rid,
			payType='package',
			uid=normal_uid,
			giftId=giftId['69']['gid']
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', normal_uid),
		             giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', normal_uid), giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money - giftId['69']['price'] * default_num)
		case_list[des] = result

	def test_003(self, des='商业房-直播,背包礼物打赏普通用户到账60%(mcb)'):
		"""
		用例描述：
		商业房-直播,背包礼物打赏普通用户到账60%(mcb)
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash_b)
		"""
		rid = gs_soundchat_rid
		assert_equal(mysql.checkRidFactoryType(rid), "business-soundchat")  # 确认rid是直播房
		mysql.updateMoneySql(payUid, default_money)
		mysql.updateMoneySql(normal_uid)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		mysql.insertXsUserCommodity(payUid, cid=giftId['69']['cid'], num=default_num)
		cid = int(mysql.selectUserInfoSql('id_commodity', payUid, cid=giftId['69']['cid']))
		data = encodeData(
			rid=rid,
			payType='package',
			uid=normal_uid,
			giftId=giftId['69']['gid'],
			package_cid=cid,
			ctype='gift'
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', normal_uid),
		             giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', normal_uid), giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money)  # 不扣费
		case_list[des] = result

	def test_004(self, des='商业房-非直播,礼物打赏普通用户到账60%(mcb)'):
		"""
		用例描述：
		验证余额足够时，商业房-非直播打赏礼物给普通用户分成为：60，且收入在公会魅力值
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash_b)
		"""
		rid = gs_friend_rid
		assert_equal(mysql.checkRidFactoryType(rid), "business-friend")  # 确认rid不是直播房
		mysql.updateMoneySql(payUid, default_money)
		mysql.updateMoneySql(normal_uid)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		data = encodeData(
			rid=rid,
			payType='package',
			uid=normal_uid,
			giftId=giftId['69']['gid']
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', normal_uid),
		             giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', normal_uid), giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money - giftId['69']['price'] * default_num)
		case_list[des] = result

	def test_005(self, des='商业房-非直播,房间私聊打赏普通用户到账60%(mcb)'):
		"""
		用例描述：
		验证余额足够时，商业房-非直播房间私聊打赏礼物给普通用户分成为：60，且收入在公会魅力值
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash_b)
		"""
		rid = gs_friend_rid
		assert_equal(mysql.checkRidFactoryType(rid), "business-friend")  # 确认rid不是直播房
		mysql.updateMoneySql(payUid, default_money)
		mysql.updateMoneySql(normal_uid)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		data = encodeData(
			rid=rid,
			payType='package',
			uid=normal_uid,
			giftId=giftId['69']['gid']
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', normal_uid),
		             giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', normal_uid), giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money - giftId['69']['price'] * default_num)
		case_list[des] = result

	def test_006(self, des='商业房-非直播,背包礼物打赏普通用户到账60%(mcb)'):
		"""
		用例描述：
		商业房-非直播,背包礼物打赏普通用户到账60%(mcb)
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash_b)
		"""
		rid = gs_friend_rid
		assert_equal(mysql.checkRidFactoryType(rid), "business-friend")  # 确认rid不是直播房
		mysql.updateMoneySql(payUid, default_money)
		mysql.updateMoneySql(normal_uid)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		mysql.insertXsUserCommodity(payUid, cid=giftId['69']['cid'], num=default_num)
		cid = int(mysql.selectUserInfoSql('id_commodity', payUid, cid=giftId['69']['cid']))
		data = encodeData(
			rid=rid,
			payType='package',
			uid=normal_uid,
			giftId=giftId['69']['gid'],
			package_cid=cid,
			ctype='gift'
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', normal_uid),
		             giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', normal_uid), giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money)  # 不扣费
		case_list[des] = result

	def test_007(self, des='个人房,礼物打赏普通用户到账60%(mcb)'):
		"""
		用例描述：
		验证余额足够时，个人房打赏礼物给普通用户分成为：60，且收入在公会魅力值
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash_b)
		"""
		rid = mysql.selectUserInfoSql('vip')
		mysql.updateMoneySql(payUid, default_money)
		mysql.updateMoneySql(normal_uid)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		data = encodeData(
			rid=rid,
			payType='package',
			uid=normal_uid,
			giftId=giftId['69']['gid']
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', normal_uid),
		             giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', normal_uid), giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money - giftId['69']['price'] * default_num)
		case_list[des] = result

	def test_008(self, des='个人房,房间私聊打赏普通用户到账60%(mcb)'):
		"""
		用例描述：
		验证余额足够时，个人房房间私聊打赏礼物给普通用户分成为：60，且收入在公会魅力值
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash_b)
		"""
		rid = mysql.selectUserInfoSql('vip')
		mysql.updateMoneySql(payUid, default_money)
		mysql.updateMoneySql(normal_uid)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		data = encodeData(
			rid=rid,
			payType='package',
			uid=normal_uid,
			giftId=giftId['69']['gid']
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', normal_uid),
		             giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', normal_uid), giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money - giftId['69']['price'] * default_num)
		case_list[des] = result

	def test_009(self, des='个人房,背包礼物打赏普通用户到账60%(mcb)'):
		"""
		用例描述：
		个人房,背包礼物打赏普通用户到账60%(mcb)
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash_b)
		"""
		rid = mysql.selectUserInfoSql('vip')
		mysql.updateMoneySql(payUid, default_money)
		mysql.updateMoneySql(normal_uid)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		mysql.insertXsUserCommodity(payUid, cid=giftId['69']['cid'], num=default_num)
		cid = int(mysql.selectUserInfoSql('id_commodity', payUid, cid=giftId['69']['cid']))
		data = encodeData(
			rid=rid,
			payType='package',
			uid=normal_uid,
			giftId=giftId['69']['gid'],
			package_cid=cid,
			ctype='gift'
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', normal_uid),
		             giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', normal_uid), giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money)  # 不扣费
		case_list[des] = result

	def test_010(self, des='***商业房-非直播,礼物打赏普通用户(不签署大神,不加工会且是商业房房主)到账60%(mc)'):
		"""
		用例描述：
		***商业房-非直播,礼物打赏普通用户(不签署大神,不加工会且是商业房房主)到账60%(mc)		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash)
		"""
		rid = business_room_rid
		assert_equal(mysql.checkRidFactoryType(rid), "business-friend")  # 确认rid不是直播房
		uid = busine_room_uid
		mysql.updateMoneySql(payUid, default_money)
		mysql.updateMoneySql(uid)
		mysql.updateUserGodSql(uid, 0)
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
		             giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', uid), giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money - giftId['69']['price'] * default_num)
		case_list[des] = result
