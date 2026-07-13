# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "公会主播-房间打赏"

import unittest

from caseSlp.config import default_money, default_num, giftId, gsUid, gs_A_ceo_rid, gs_A_rid, gs_A_uid, gs_B_ceo_rid, gs_B_rid, gs_B_uid, gs_friend_rid, gs_soundchat_rid, payUid, pay_url, rates
from common.Assert import assert_code, assert_equal, assert_body
from common.Consts import case_list_b, result
from common.Request import post_request_session
from common.basicSlpData import encodeData
from common.conSlpMysql import conMysql as mysql
from common.runFailed import Retry
from common.sqlScript import UserMoneyOperations, UserCommodityOperations
from common.method import format_reason


@Retry(max_n=3)
class TestPayCreate(unittest.TestCase):
	"""公会主播-房间打赏数据驱动测试"""

	GS_ROOM_CASES = [
		# (描述, rid, uid, god大神状态, gift_type, money_type, room_type)
		('商业房-直播,礼物打赏GS到账60%(mc)', gs_soundchat_rid, gsUid, 1, 'package', 'money_cash', 'business-soundchat'),
		('商业房-直播,房间私聊打赏GS到账60%(mc)', gs_soundchat_rid, gsUid, 1, 'package', 'money_cash', 'business-soundchat'),
		('商业房-直播,背包礼物打赏GS到账60%(mc)', gs_soundchat_rid, gsUid, 1, 'gift', 'money_cash', 'business-soundchat'),
		('商业房-非直播,礼物打赏GS到账60%(mc)', gs_friend_rid, gs_B_uid, 1, 'package', 'money_cash', 'business-friend'),
		('商业房-非直播,房间私聊打赏GS到账60%(mc)', gs_friend_rid, gs_B_uid, 1, 'package', 'money_cash', 'business-friend'),
		('商业房-非直播,背包礼物打赏GS到账60%(mc)', gs_friend_rid, gs_B_uid, 1, 'gift', 'money_cash', 'business-friend'),
		('个人房,礼物打赏GS到账60%(mc)', None, gsUid, 1, 'package', 'money_cash', None),
		('个人房,房间私聊打赏GS到账60%(mc)', None, gsUid, 1, 'package', 'money_cash', None),
		('个人房,背包礼物打赏GS到账60%(mc)', None, gsUid, 1, 'gift', 'money_cash', None),
		('商业房-直播,礼物打赏GS(签署大神且是房主),到账60%(mc)', gs_A_rid, gs_A_uid, 1, 'package', 'money_cash', 'business-soundchat'),
		('商业房-直播,礼物打赏GS(签署大神且非房主),到账60%(mc)', gs_A_ceo_rid, gs_A_uid, 1, 'package', 'money_cash', 'business-soundchat'),
		('商业房-直播,礼物打赏GS(不签署大神且是房主),到账60%(mcb)', gs_A_rid, gs_A_uid, 0, 'package', None, 'business-soundchat'),
		('商业房-直播,礼物打赏GS(不签署大神且非房主),到账60%(mcb)', gs_A_ceo_rid, gs_A_uid, 0, 'package', None, 'business-soundchat'),
		('商业房-非直播,礼物打赏GS(签署大神且是房主)到账60%(mc)', gs_B_rid, gs_B_uid, 1, 'package', 'money_cash', 'business-friend'),
		('商业房-非直播,房间私聊打赏GS(签署大神且非房主)到账60%(mc)', gs_B_ceo_rid, gs_B_uid, 1, 'package', 'money_cash', 'business-friend'),
		('***商业房-非直播,礼物打赏GS(不签署大神且是房主)到账60%(mc)', gs_B_rid, gs_B_uid, 0, 'package', 'money_cash', 'business-friend'),
		('商业房-非直播,房间私聊打赏GS(不签署大神且非房主)到账60%(mcb)', gs_B_ceo_rid, gs_B_uid, 0, 'package', None, 'business-friend'),
	]

	def _run_gs_room_case(self, des, rid, uid, god, gift_type, money_type, room_type):
		"""单条公会主播打赏用例执行逻辑"""
		if rid is None:
			rid = mysql.selectUserInfoSql('vip')
		if room_type:
			assert_equal(mysql.checkRidFactoryType(rid), room_type)
		assert_equal(mysql.checkUserBroker(uid), True)  # 确认 uid是工会成员
		UserMoneyOperations.update(payUid, default_money)
		UserMoneyOperations.update(uid)
		mysql.updateUserGodSql(uid, god)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		if gift_type == 'gift':
			UserCommodityOperations.insert(payUid, cid=giftId['69']['cid'], num=default_num)
			cid = int(mysql.selectUserInfoSql('id_commodity', payUid, cid=giftId['69']['cid']))
			data = encodeData(
				rid=rid, payType='package', uid=uid,
				giftId=giftId['69']['gid'], package_cid=cid, ctype='gift'
			)
		else:
			data = encodeData(
				rid=rid, payType='package', uid=uid, giftId=giftId['69']['gid']
			)
		res = post_request_session(pay_url, data, token_name='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, format_reason(des, res))
		if money_type:
			assert_equal(mysql.selectUserInfoSql('single_money', uid, money_type=money_type),
			             giftId['69']['price'] * default_num * rates['gs']['default'])
		else:
			assert_equal(mysql.selectUserInfoSql('single_money', uid),
			             giftId['69']['price'] * default_num * rates['gs']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', uid), giftId['69']['price'] * default_num * rates['gs']['default'])
		if gift_type == 'gift':
			assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money)  # 不扣费
		else:
			assert_equal(mysql.selectUserInfoSql('sum_money', payUid),
			             default_money - giftId['69']['price'] * default_num)
		case_list_b[des] = result

	def test_gs_room_all(self, des='不同房间类型下公会主播打赏场景组合'):
		"""数据驱动：覆盖直播/非直播商业房及个人房的礼物/私聊/背包打赏、大神/房主组合场景"""
		for case_des, rid, uid, god, gift_type, money_type, room_type in self.GS_ROOM_CASES:
			with self.subTest(des=case_des, rid=rid, uid=uid, god=god, gift_type=gift_type, money_type=money_type):
				self._run_gs_room_case(case_des, rid, uid, god, gift_type, money_type, room_type)
