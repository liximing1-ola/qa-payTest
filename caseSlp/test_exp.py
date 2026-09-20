# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "经验值相关用例"

from caseSlp.base import SlpCase, SlpTestBase
from caseSlp.config import business_room_rid, default_money, giftId, juewei_level, normal_uid, payUid
from common.conSlpMysql import conMysql as mysql
from common.runFailed import Retry

# 消费后等待 vip 经验值/人气值落库的时长（秒）
PROFILE_UPDATE_WAIT = 0.5


def _make_exp_case(des, level_name):
	"""构造单条爵位消费经验值增长场景"""
	level_info = juewei_level[level_name]
	return SlpCase(
		des=des,
		setup=[
			{'action': 'check_user_broker', 'uid': normal_uid, 'expected': False},  # 确认 uid不是工会成员
			{'action': 'delete_user_account',
			 'params': {'table': 'user_title_new', 'uid': payUid}},  # 关闭贵族,还原数据
			{'action': 'delete_user_account',
			 'params': {'table': 'pay_room_money', 'uid': payUid}},  # 修改vip值,还原数据
			{'action': 'update_user_title', 'params': {'uid': payUid, 'level': level_info['level']}},
			{'action': 'update_money', 'params': {'uid': payUid, 'money': default_money}},
			{'action': 'delete_commodity', 'uid': payUid},
		],
		queries=[
			('old_vip', lambda: mysql.selectUserInfoSql('pay_room_money', payUid)),
			('old_pop', lambda: mysql.selectUserInfoSql('popularity', normal_uid)),
		],
		data={'rid': business_room_rid, 'payType': 'package', 'uid': normal_uid,
		      'gift_id': giftId['69']['gid']},
		post_wait=PROFILE_UPDATE_WAIT,
		checks=[
			{'field': 'pay_room_money', 'uid': payUid,
			 'expected': lambda ctx: ctx['old_vip'] + level_info['update'] * giftId['69']['price'] / 100},
			{'field': 'popularity', 'uid': normal_uid,
			 'expected': lambda ctx: ctx['old_pop'] + giftId['69']['price']},
		],
		report='case_list_b',
	)


EXP_CASES = [
	('打赏者,贵族爵位=骑士(lv1,1倍)消费,vip经验值1:1增加', '骑士'),
	('打赏者,贵族爵位=男爵(lv1,1倍)消费,vip经验值1:1增加', '男爵'),
	('打赏者,贵族爵位=子爵(lv1,1倍)消费,vip经验值1:1增加', '子爵'),
	('打赏者,贵族爵位=伯爵(lv4,1.05倍)消费,vip经验值1:1.05增加', '伯爵'),
	('打赏者,贵族爵位=侯爵(lv4,1.1倍)消费,vip经验值1:1.1增加', '侯爵'),
	('打赏者,贵族爵位=公爵(lv4,1.15倍)消费,vip经验值1:1.15增加', '公爵'),
	('打赏者,贵族爵位=亲王(lv4,1.2倍)消费,vip经验值1:1.2增加', '亲王'),
	('打赏者,贵族爵位=国王(lv4,1.25倍)消费,vip经验值1:1.25增加', '国王'),
	('打赏者,贵族爵位=皇帝(lv4,1.3倍)消费,vip经验值1:1.3增加', '皇帝'),
]

EXP_SCENES = [_make_exp_case(*case) for case in EXP_CASES]


@Retry(max_n=3)
class TestPayCreate(SlpTestBase):
	"""贵族爵位消费后 vip 经验值增长数据驱动测试"""

	def test_exp_all(self, des='不同贵族爵位消费对应的vip经验值增加'):
		"""数据驱动：覆盖各贵族爵位消费后 vip 经验值增长场景"""
		for scene in EXP_SCENES:
			with self.subTest(des=scene.des):
				self.run_case(scene)
