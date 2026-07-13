# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "经验值相关用例"

import time
import unittest

from caseSlp.config import business_room_rid, default_money, giftId, juewei_level, normal_uid, payUid, pay_url
from common.Assert import assert_code, assert_equal, assert_body
from common.Consts import case_list_b, result
from common.Request import post_request_session
from common.basicSlpData import encodeData
from common.conSlpMysql import conMysql as mysql
from common.runFailed import Retry
from common.sqlScript import UserMoneyOperations
from common.method import format_reason


@Retry(max_n=3)
class TestPayCreate(unittest.TestCase):
	"""贵族爵位消费后 vip 经验值增长数据驱动测试"""

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

	def _run_exp_case(self, des, level_name):
		"""单条爵位经验值用例执行逻辑"""
		rid = business_room_rid
		uid = normal_uid
		assert_equal(mysql.checkUserBroker(uid), False)  # 确认 uid不是工会成员
		mysql.deleteUserAccountSql('user_title_new', payUid)  # 关闭贵族,还原数据
		mysql.deleteUserAccountSql('pay_room_money', payUid)  # 修改vip值,还原数据
		level_info = juewei_level[level_name]
		mysql.updateUserInfoSql('user_title_new', payUid, level=level_info['level'])
		UserMoneyOperations.update(payUid, default_money)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		old_vip = mysql.selectUserInfoSql('pay_room_money', payUid)
		old_pop = mysql.selectUserInfoSql('popularity', uid)
		data = encodeData(
			rid=rid,
			payType='package',
			uid=uid,
			giftId=giftId['69']['gid']
		)
		res = post_request_session(pay_url, data, token_name='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, format_reason(des, res))
		time.sleep(0.5)
		assert_equal(mysql.selectUserInfoSql('pay_room_money', payUid),
		             old_vip + level_info['update'] * giftId['69']['price'] / 100)
		assert_equal(mysql.selectUserInfoSql('popularity', uid), old_pop + giftId['69']['price'])
		case_list_b[des] = result

	def test_exp_all(self, des='不同贵族爵位消费对应的vip经验值增加'):
		"""数据驱动：覆盖各贵族爵位消费后 vip 经验值增长场景"""
		for case_des, level_name in self.EXP_CASES:
			with self.subTest(des=case_des, level_name=level_name):
				self._run_exp_case(case_des, level_name)
