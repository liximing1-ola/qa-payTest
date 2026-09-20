# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "普通用户-房间打赏"

from caseSlp.base import SlpCase, SlpTestBase
from caseSlp.config import business_room_rid, business_room_uid, default_money, default_num, giftId, gs_friend_rid, gs_soundchat_rid, normal_uid, payUid, rates
from common.conSlpMysql import conMysql as mysql
from common.runFailed import Retry


def _make_room_case(des, rid, room_type, gift_type):
	"""构造单条房间打赏场景"""
	setup = []
	if room_type:
		setup.append({'action': 'check_rid_type', 'rid': rid, 'expected': room_type})
	setup.append({'action': 'update_money', 'params': {'uid': payUid, 'money': default_money}})
	setup.append({'action': 'update_money', 'params': {'uid': normal_uid}})
	setup.append({'action': 'delete_commodity', 'uid': payUid})
	if gift_type == 'gift':
		setup.append({'action': 'insert_commodity',
		              'params': {'uid': payUid, 'cid': giftId['69']['cid'],
		                         'num': default_num}})

	queries = [('rid', lambda: rid if rid is not None else mysql.selectUserInfoSql('vip'))]
	data = {'rid': lambda ctx: ctx['rid'], 'payType': 'package', 'uid': normal_uid,
	        'gift_id': giftId['69']['gid']}
	if gift_type == 'gift':
		data['package_cid'] = lambda ctx: ctx['box_cid']
		data['ctype'] = 'gift'
		queries.append(('box_cid', lambda: int(mysql.selectUserInfoSql(
			'id_commodity', payUid, cid=giftId['69']['cid']))))

	return SlpCase(
		des=des,
		setup=setup,
		queries=queries,
		data=data,
		checks=[
			{'field': 'single_money', 'uid': normal_uid,
			 'expected': giftId['69']['price'] * default_num * rates['normal']['default']},
			{'field': 'sum_money', 'uid': normal_uid,
			 'expected': giftId['69']['price'] * default_num * rates['normal']['default']},
			{'field': 'sum_money', 'uid': payUid,
			 'expected': (default_money if gift_type == 'gift'
			              else default_money - giftId['69']['price'] * default_num)},
		],
	)


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

ROOM_SCENES = [_make_room_case(*case) for case in ROOM_CASES]

# 用例：商业房房主（不签大神/不加工会）收 60% mc
SCENE_010 = SlpCase(
	des='***商业房-非直播,礼物打赏普通用户(不签署大神,不加工会且是商业房房主)到账60%(mc)',
	setup=[
		{'action': 'check_rid_type', 'rid': business_room_rid, 'expected': 'business-friend'},
		{'action': 'check_user_broker', 'uid': business_room_uid, 'expected': False},
		{'action': 'update_money', 'params': {'uid': payUid, 'money': default_money}},
		{'action': 'update_money', 'params': {'uid': business_room_uid}},
		{'action': 'update_user_god', 'params': {'uid': business_room_uid, 'god': 0}},
		{'action': 'delete_commodity', 'uid': payUid},
	],
	# 沿用原用例的礼物引用：78 号礼物在 config 中未定义，行为与原实现一致
	data={'rid': business_room_rid, 'payType': 'package', 'uid': business_room_uid,
	      'gift_id': lambda ctx: giftId['78']['gid']},
	checks=[
		{'field': 'single_money', 'uid': business_room_uid, 'money_type': 'money_cash',
		 'expected': giftId['69']['price'] * default_num * rates['normal']['default']},
		{'field': 'sum_money', 'uid': business_room_uid,
		 'expected': giftId['69']['price'] * default_num * rates['normal']['default']},
		{'field': 'sum_money', 'uid': payUid,
		 'expected': default_money - giftId['69']['price'] * default_num},
	],
)


@Retry(max_n=3)
class TestPayCreate(SlpTestBase):
	"""普通用户-房间打赏数据驱动测试"""

	def test_room_all(self, des='不同房间类型下普通用户打赏场景组合'):
		"""数据驱动：覆盖直播/非直播商业房及个人房的礼物/私聊/背包打赏场景"""
		for scene in ROOM_SCENES:
			with self.subTest(des=scene.des):
				self.run_case(scene)

	def test_010(self, des='***商业房-非直播,礼物打赏普通用户(不签署大神,不加工会且是商业房房主)到账60%(mc)'):
		"""
		用例描述：
		***商业房-非直播,礼物打赏普通用户(不签署大神,不加工会且是商业房房主)到账60%(mc)
		"""
		self.run_case(SCENE_010)
