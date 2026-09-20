# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "公会主播-个人守护"

import pytest

from caseSlp.base import SlpCase, SlpTestBase
from caseSlp.config import default_money, defend, gsUid, payUid, rates
from common.conSlpMysql import conMysql as mysql
from common.runFailed import Retry

# 场景表：公会主播-个人守护（开通 -> 进阶 -> 解除，按 test 顺序执行）
SCENES = [
	SlpCase(
		des='给GS开通个人守护场景60%(mc)',
		setup=[
			{'action': 'check_user_broker', 'uid': gsUid, 'expected': True},
			{'action': 'update_money', 'params': {'uid': payUid, 'money': default_money}},
			{'action': 'update_money', 'params': {'uid': gsUid}},
			{'action': 'update_user_god', 'params': {'uid': gsUid, 'god': 1}},
		],
		data={'uid': gsUid, 'payType': 'defend',
		      'defend_id': defend['小宝贝']['id'], 'money': defend['小宝贝']['price']},
		checks=[
			{'field': 'sum_money', 'uid': payUid,
			 'expected': default_money - defend['小宝贝']['price']},
			{'field': 'single_money', 'uid': gsUid, 'money_type': 'money_cash',
			 'expected': defend['小宝贝']['price'] * rates['gs']['default']},
		],
	),
	SlpCase(
		des='给GS开通个人守护进阶场景60%(mc)',
		setup=[
			{'action': 'check_user_broker', 'uid': gsUid, 'expected': True},
			{'action': 'update_money', 'params': {'uid': payUid, 'money': default_money}},
			{'action': 'update_money', 'params': {'uid': gsUid}},
			{'action': 'update_user_god', 'params': {'uid': gsUid, 'god': 1}},
		],
		queries=[('defend_id', lambda: mysql.selectUserInfoSql(
			'relation_id', payuid=payUid, uid=gsUid, cid=defend['小宝贝']['id']))],
		data={'uid': gsUid, 'payType': 'defend-upgrade',
		      'money': defend['小宝贝']['upgrade_price'],
		      'defend_id': lambda ctx: ctx['defend_id']},
		checks=[
			{'field': 'sum_money', 'uid': payUid,
			 'expected': default_money - defend['小宝贝']['upgrade_price']},
			{'field': 'single_money', 'uid': gsUid, 'money_type': 'money_cash',
			 'expected': defend['小宝贝']['upgrade_price'] * rates['gs']['default']},
		],
	),
	SlpCase(
		des='GS个人守护解除场景,不分成',
		setup=[
			{'action': 'check_user_broker', 'uid': gsUid, 'expected': True},
			{'action': 'update_money', 'params': {'uid': payUid, 'money': default_money}},
			{'action': 'update_money', 'params': {'uid': gsUid}},
			{'action': 'update_user_god', 'params': {'uid': gsUid, 'god': 1}},
		],
		queries=[
			# 原用例的探询查询（结果不使用），保留执行以保持行为一致
			('_relation_id_probe', lambda: mysql.selectUserInfoSql(
				'relation_id', uid=gsUid, cid=defend['小宝贝']['id'])),
			('defend_id', lambda: mysql.selectUserInfoSql(
				'relation_id', payuid=payUid, uid=gsUid, cid=defend['小宝贝']['id'])),
		],
		data={'uid': gsUid, 'payType': 'defend-break',
		      'money': defend['小宝贝']['break_price'],
		      'defend_id': lambda ctx: ctx['defend_id']},
		checks=[
			{'field': 'sum_money', 'uid': payUid,
			 'expected': default_money - defend['小宝贝']['break_price']},
			{'field': 'sum_money', 'uid': gsUid, 'expected': 0},
		],
	),
]


@Retry(max_n=3)
class TestPayCreate(SlpTestBase):
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
		self.run_case(SCENES[0])

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
		self.run_case(SCENES[1])

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
		self.run_case(SCENES[2])
