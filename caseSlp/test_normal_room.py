# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "普通用户-房间打赏"

import unittest

from caseSlp.config import business_room_rid, business_room_uid, default_money, default_num, giftId, gs_friend_rid, gs_soundchat_rid, normal_uid, payUid, pay_url, rates
from common.Assert import assert_code, assert_equal, assert_body
from common.Consts import case_list, result
from common.Request import post_request_session
from common.basicSlpData import encodeData
from common.conSlpMysql import conMysql as mysql
from common.runFailed import Retry
from common.sqlScript import UserMoneyOperations, UserCommodityOperations
from common.method import format_reason


@Retry(max_n=3)
class TestPayCreate(unittest.TestCase):
	"""普通用户-房间打赏数据驱动测试"""

	ROOM_CASES = [
		# (描述, rid, 房间类型断言, 礼物类型: package=普通/gift=背包)
		('商业房-直播,礼物打赏普通用户到账60%(mcb)', gs_soundchat_rid, 'business-soundchat', 'package'),
		('直播商业房,房间私聊打赏普通用户到账60%(mcb)', gs_soundchat_rid, 'business-soundchat', 'package'),
		('直播商业房,背包礼物打赏普通用户到账60%(mcb)', gs_soundchat_rid, 'business-soundchat', 'gift'),
		('非直播商业房,礼物打赏普通用户到账60%(mcb)', gs_friend_rid, 'business-friend', 'package'),
		('非直播商业房,房间私聊打赏普通用户到账60%(mcb)', gs_friend_rid, 'business-friend', 'package'),
		('非直播商业房,背包礼物打赏普通用户到账60%(mcb)', gs_friend_rid, 'business-friend', 'gift'),
		('个人房礼物打赏普通用户到账60%(mcb)', None, None, 'package'),
		('个人房私聊打赏普通用户到账60%(mcb)', None, None, 'package'),
		('个人房,背包礼物打赏普通用户到账60%(mcb)', None, None, 'gift'),
	]

	def _run_room_case(self, des, rid, room_type, gift_type):
		"""单条房间打赏用例执行逻辑"""
		if rid is None:
			rid = mysql.selectUserInfoSql('vip')
		if room_type:
			assert_equal(mysql.checkRidFactoryType(rid), room_type)
		UserMoneyOperations.update(payUid, default_money)
		UserMoneyOperations.update(normal_uid)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		if gift_type == 'gift':
			UserCommodityOperations.insert(payUid, cid=giftId['69']['cid'], num=default_num)
			cid = int(mysql.selectUserInfoSql('id_commodity', payUid, cid=giftId['69']['cid']))
			data = encodeData(
				rid=rid,
				payType='package',
				uid=normal_uid,
				giftId=giftId['69']['gid'],
				package_cid=cid,
				ctype='gift'
			)
		else:
			data = encodeData(
				rid=rid,
				payType='package',
				uid=normal_uid,
				giftId=giftId['69']['gid']
			)
		res = post_request_session(pay_url, data, token_name='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, format_reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', normal_uid),
		             giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', normal_uid),
		             giftId['69']['price'] * default_num * rates['normal']['default'])
		if gift_type == 'gift':
			assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money)  # 不扣费
		else:
			assert_equal(mysql.selectUserInfoSql('sum_money', payUid),
			             default_money - giftId['69']['price'] * default_num)
		case_list[des] = result

	def test_room_all(self, des='不同房间类型下普通用户打赏场景组合'):
		"""数据驱动：覆盖直播/非直播商业房及个人房的礼物/私聊/背包打赏场景"""
		for case_des, rid, room_type, gift_type in self.ROOM_CASES:
			with self.subTest(des=case_des, rid=rid, gift_type=gift_type):
				self._run_room_case(case_des, rid, room_type, gift_type)

	def test_010(self, des='***商业房-非直播,礼物打赏普通用户(不签署大神,不加工会且是商业房房主)到账60%(mc)'):
		"""
		用例描述：
		***商业房-非直播,礼物打赏普通用户(不签署大神,不加工会且是商业房房主)到账60%(mc)
		"""
		rid = business_room_rid
		assert_equal(mysql.checkRidFactoryType(rid), "business-friend")  # 确认rid不是直播房
		uid = business_room_uid
		assert_equal(mysql.checkUserBroker(uid), False)  # 确认 uid是工会成员
		UserMoneyOperations.update(payUid, default_money)
		UserMoneyOperations.update(uid)
		mysql.updateUserGodSql(uid, 0)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		data = encodeData(
			rid=rid,
			payType='package',
			uid=uid,
			giftId=giftId['78']['gid']
		)
		res = post_request_session(pay_url, data, token_name='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, format_reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', uid, money_type='money_cash'),
		             giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', uid), giftId['69']['price'] * default_num * rates['normal']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money - giftId['69']['price'] * default_num)
		case_list[des] = result
