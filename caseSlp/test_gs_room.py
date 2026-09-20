# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "公会主播-房间打赏"

from caseSlp.base import SlpCase, SlpTestBase
from caseSlp.config import default_money, default_num, giftId, gsUid, gs_A_ceo_rid, gs_A_rid, gs_A_uid, gs_B_ceo_rid, gs_B_rid, gs_B_uid, gs_friend_rid, gs_soundchat_rid, payUid, rates
from common.conSlpMysql import conMysql as mysql
from common.runFailed import Retry


def _make_gs_room_case(des, rid, uid, god, gift_type, money_type, room_type):
	"""构造单条公会主播房间打赏场景"""
	setup = []
	if room_type:
		setup.append({'action': 'check_rid_type', 'rid': rid, 'expected': room_type})
	setup.append({'action': 'check_user_broker', 'uid': uid, 'expected': True})  # 确认 uid是工会成员
	setup.append({'action': 'update_money', 'params': {'uid': payUid, 'money': default_money}})
	setup.append({'action': 'update_money', 'params': {'uid': uid}})
	setup.append({'action': 'update_user_god', 'params': {'uid': uid, 'god': god}})
	setup.append({'action': 'delete_commodity', 'uid': payUid})
	if gift_type == 'gift':
		setup.append({'action': 'insert_commodity',
		              'params': {'uid': payUid, 'cid': giftId['69']['cid'],
		                         'num': default_num}})

	queries = [('rid', lambda: rid if rid is not None else mysql.selectUserInfoSql('vip'))]
	data = {'rid': lambda ctx: ctx['rid'], 'payType': 'package', 'uid': uid,
	        'gift_id': giftId['69']['gid']}
	if gift_type == 'gift':
		data['package_cid'] = lambda ctx: ctx['box_cid']
		data['ctype'] = 'gift'
		queries.append(('box_cid', lambda: int(mysql.selectUserInfoSql(
			'id_commodity', payUid, cid=giftId['69']['cid']))))

	single_money = {'field': 'single_money', 'uid': uid,
	                'expected': giftId['69']['price'] * default_num * rates['gs']['default']}
	if money_type:
		single_money['money_type'] = money_type

	return SlpCase(
		des=des,
		setup=setup,
		queries=queries,
		data=data,
		checks=[
			single_money,
			{'field': 'sum_money', 'uid': uid,
			 'expected': giftId['69']['price'] * default_num * rates['gs']['default']},
			{'field': 'sum_money', 'uid': payUid,
			 'expected': (default_money if gift_type == 'gift'
			              else default_money - giftId['69']['price'] * default_num)},
		],
		report='case_list_b',
	)


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

GS_ROOM_SCENES = [_make_gs_room_case(*case) for case in GS_ROOM_CASES]


@Retry(max_n=3)
class TestPayCreate(SlpTestBase):
	"""公会主播-房间打赏数据驱动测试"""

	def test_gs_room_all(self, des='不同房间类型下公会主播打赏场景组合'):
		"""数据驱动：覆盖直播/非直播商业房及个人房的礼物/私聊/背包打赏、大神/房主组合场景"""
		for scene in GS_ROOM_SCENES:
			with self.subTest(des=scene.des):
				self.run_case(scene)
