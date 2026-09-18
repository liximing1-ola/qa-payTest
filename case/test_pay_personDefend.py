# coding=utf-8
"""
个人守护支付测试

场景差异通过模块级 SCENES 表声明，由 PayTestBase.run_case 统一执行。
"""
import pytest

from case.base import PayCase, PayTestBase
from common.Config import config
from common.conMysql import conMysql as mysql
from common.runFailed import Retry

SCENES = [
    PayCase(
        des='开通个人守护场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 52000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ],
        data={'payType': 'defend',
              'defend_id': lambda ctx: ctx['cls'].defend_520_config['id'],
              'money': lambda ctx: ctx['cls'].defend_520_config['money_value']},
        checks=[
            {'field': 'sum_money', 'expected': 0},
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 32240}
        ]),
    PayCase(
        des='守护进阶场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 100000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ],
        data={'payType': 'defend-upgrade',
              'money': lambda ctx: ctx['cls'].defend_520_config['upgrade_money'],
              'defend_id': lambda ctx: ctx['cls'].defend_520_id},
        checks=[
            {'field': 'sum_money', 'expected': 100},
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 61938}
        ]),
    PayCase(
        des='守护解除场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 40000}}
        ],
        data={'payType': 'defend-break',
              'money': lambda ctx: ctx['cls'].defend_520_config['break_money'],
              'defend_id': lambda ctx: ctx['cls'].defend_520_id},
        checks=[
            {'field': 'sum_money', 'expected': 11200}
        ]),
    PayCase(
        des='守护消费GS收62%（mc）',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 520000}},
            {'action': 'update_money', 'params': {'uid': config.gsUid}}
        ],
        data={'payType': 'defend', 'uid': config.gsUid,
              'defend_id': lambda ctx: ctx['cls'].defend_cp_config['id'],
              'money': lambda ctx: ctx['cls'].defend_cp_config['money_value']},
        checks=[
            {'field': 'sum_money', 'expected': 0},
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 520000 * config.rate,
             'kwargs': {'money_type': 'money_cash'}}
        ]),
    PayCase(
        des='守护进阶消费GS收62%（mc）',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000000}},
            {'action': 'update_money', 'params': {'uid': config.gsUid}}
        ],
        data={'payType': 'defend-upgrade',
              'money': lambda ctx: ctx['cls'].defend_cp_config['upgrade_money'],
              'defend_id': lambda ctx: ctx['cls'].defend_cp_id},
        checks=[
            {'field': 'sum_money', 'expected': 480000},
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 520000 * config.rate,
             'kwargs': {'money_type': 'money_cash'}}
        ]),
    PayCase(
        des='守护解除场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 100000}}
        ],
        data={'payType': 'defend-break',
              'money': lambda ctx: ctx['cls'].defend_cp_config['break_money'],
              'defend_id': lambda ctx: ctx['cls'].defend_cp_id},
        checks=[
            {'field': 'sum_money', 'expected': 100}
        ]),
]


@Retry(max_n=3)
class TestPayPersonDefend(PayTestBase):
    """个人守护支付测试类"""

    @classmethod
    def setUpClass(cls):
        """查询守护关系配置与关系 ID（延迟到运行期，避免 import 阶段依赖数据库）"""
        # {'id': 2, 'name': '小宝贝', 'money_value': 52000, 'break_money': 28800, 'upgrade_money': 99900}
        # {'id': 1, 'name': 'CP', 'money_value': 520000, 'break_money': 99900, 'upgrade_money': 520000}
        cls.defend_520_config = mysql.selectUserInfoSql('relation_config', uid=2)
        cls.defend_cp_config = mysql.selectUserInfoSql('relation_config', uid=1)
        cls.defend_520_id = mysql.selectUserInfoSql('relation_id', cid=2)
        cls.defend_cp_id = mysql.selectUserInfoSql('relation_id', uid=config.gsUid, cid=1)

    @pytest.mark.run(order=1)
    def test_01_defendPayChangMoney(self):
        """开通个人守护，收益分成在师父收益(非一代宗师)的基础上为 62:38"""
        self.run_case(SCENES[0])

    @pytest.mark.run(order=2)
    def test_02_defendUpgradePayChangeMoney(self):
        """个人守护开通后购买进阶版特权（99900钻），收益分成 62:38"""
        self.run_case(SCENES[1])

    @pytest.mark.run(order=3)
    def test_03_defendBreakPayChangeMoney(self):
        """个人守护购买进阶版后强行解除关系，收益归官方"""
        self.run_case(SCENES[2])

    @pytest.mark.run(order=4)
    def test_04_defendPayToGs(self):
        """给公会用户开通 520000 钻 CP 守护"""
        self.run_case(SCENES[3])

    @pytest.mark.run(order=5)
    def test_05_defendUpgradeToGs(self):
        """公会用户守护购买进阶版（520000钻），分成 62%"""
        self.run_case(SCENES[4])

    @pytest.mark.run(order=6)
    def test_06_defendBreakPayMoney(self):
        """公会用户守护购买进阶版后强行解除关系，收益归官方"""
        self.run_case(SCENES[5])
