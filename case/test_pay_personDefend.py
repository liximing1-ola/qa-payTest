from common.Config import config
from common.method import reason
import unittest
import pytest
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_equal
from common.basicData import encodeData
from common.Consts import case_list, result
from common.runFailed import Retry
from common.conMysql import conMysql as mysql


@Retry(max_n=3)
class TestPayPersonDefend(unittest.TestCase):

    # {'id': 2, 'name': '小宝贝', 'money_value': 52000, 'break_money': 28800, 'upgrade_money': 99900}
    # {'id': 1, 'name': 'CP', 'money_value': 520000, 'break_money': 99900, 'upgrade_money': 520000}
    defend_520_config = mysql.selectUserInfoSql('relation_config', uid=2)
    defend_cp_config = mysql.selectUserInfoSql('relation_config', uid=1)
    defend_520_id = mysql.selectUserInfoSql('relation_id', cid=2)
    defend_cp_id = mysql.selectUserInfoSql('relation_id', uid=config.gsUid, cid=1)

    def _prepare_test_data(self, setup_steps):
        """准备测试数据"""
        for step in setup_steps:
            mysql.updateMoneySql(**step)

    def _validate_db_state(self, checks):
        """验证数据库状态"""
        for check in checks:
            field = check['field']
            uid = check.get('uid', config.payUid)
            expected = check['expected']
            kwargs = check.get('kwargs', {})
            assert_equal(mysql.selectUserInfoSql(field, uid, **kwargs), expected)

    @pytest.mark.run(order=1)
    def test_01_defendPayChangMoney(self):
        """
        用例描述：
        开通个人守护，收益分成在师父收益(非一代宗师)的基础上为 62:38
        脚本步骤：
        1.构造开通者和被守护者数据
        2.开通价值52000钻小宝贝守护（xs_relation_config id=2）
        3.校验接口状态和返回值数据
        4.检查打赏者余额
        5.检查被打赏者余额,预期：52000 * 0.62 = 32240
        """
        des = '开通个人守护场景'

        # 准备测试数据
        self._prepare_test_data([
            {'uid': config.payUid, 'money': 52000},
            {'uid': config.rewardUid}
        ])

        # 发送请求
        data = encodeData(
            payType='defend',
            defend_id=self.defend_520_config['id'],
            money=self.defend_520_config['money_value']
        )
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'expected': 0},
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 32240}
        ])

        case_list[des] = result

    @pytest.mark.run(order=2)
    def test_02_defendUpgradePayChangeMoney(self):
        """
         用例描述：
         个人守护关系开通后，购买进阶版特权，收益分成在师父收益（非一代宗师）的基础上为：62:38
         脚本步骤：
         1.接test_01
         2.购买进阶版（99900钻），黄金小宝贝对应进阶价格
         3.校验接口状态和返回值数据
         4.检查打赏者余额，预期：100000 - 99900 = 100
         5.检查被打赏者余额,预期： 99900 * 0.62 = 61938
         """
        des = '守护进阶场景'

        # 准备测试数据
        self._prepare_test_data([
            {'uid': config.payUid, 'money': 100000},
            {'uid': config.rewardUid}
        ])

        # 发送请求
        data = encodeData(
            payType='defend-upgrade',
            money=self.defend_520_config['upgrade_money'],
            defend_id=self.defend_520_id
        )
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'expected': 100},
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 61938}
        ])

        case_list[des] = result

    @pytest.mark.run(order=3)
    def test_03_defendBreakPayChangeMoney(self):
        """
         用例描述：
         个人守护关系开通后，购买进阶版特权后，强行解除关系，收益归官方
         脚本步骤：
         1.接test_01，test_02
         2.强制解除关系
         3.校验接口状态和返回值数据
         4.检查打赏者余额，预期：40000 - 36000 = 4000
         """
        des = '守护解除场景'

        # 准备测试数据
        self._prepare_test_data([
            {'uid': config.payUid, 'money': 40000}
        ])

        # 发送请求
        data = encodeData(
            payType='defend-break',
            money=self.defend_520_config['break_money'],
            defend_id=self.defend_520_id
        )
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'expected': 11200}
        ])

        case_list[des] = result

    @pytest.mark.run(order=4)
    def test_04_defendPayToGs(self):
        """
        用例描述：
        给公会用户开通个人守护
        脚本步骤：
        1.构造开通者和被守护者数据
        2.开通价值520000钻CP守护（xs_relation_config id=1）
        3.校验接口状态和返回值数据
        4.检查打赏者余额
        5.检查被打赏者余额,预期：520000 * 0.62 = 322400
        """
        des = '守护消费GS收62%（mc）'

        # 准备测试数据
        self._prepare_test_data([
            {'uid': config.payUid, 'money': 520000},
            {'uid': config.gsUid}
        ])

        # 发送请求
        data = encodeData(
            payType='defend',
            uid=config.gsUid,
            defend_id=self.defend_cp_config['id'],
            money=self.defend_cp_config['money_value']
        )
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'expected': 0},
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 520000 * config.rate, 'kwargs': {'money_type': 'money_cash'}}
        ])

        case_list[des] = result

    @pytest.mark.run(order=5)
    def test_05_defendUpgradeToGs(self):
        """
         用例描述：
         个人守护关系开通后，购买进阶版特权，收益分成给公会用户分成为62%
         脚本步骤：
         1.接test_04
         2.购买进阶版（520000钻），黄金CP对应进阶价格
         3.校验接口状态和返回值数据
         4.检查打赏者余额，预期：1000000 - 520000 = 480000
         5.检查被打赏者余额,预期： 520000 * 0.62 = 322400
         """
        des = '守护进阶消费GS收62%（mc）'

        # 准备测试数据
        self._prepare_test_data([
            {'uid': config.payUid, 'money': 1000000},
            {'uid': config.gsUid}
        ])

        # 发送请求
        data = encodeData(
            payType='defend-upgrade',
            money=self.defend_cp_config['upgrade_money'],
            defend_id=self.defend_cp_id
        )
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'expected': 480000},
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 520000 * config.rate, 'kwargs': {'money_type': 'money_cash'}}
        ])

        case_list[des] = result

    @pytest.mark.run(order=6)
    def test_06_defendBreakPayMoney(self):
        """
         用例描述：
         个人守护关系开通后，购买进阶版特权后，强行解除关系，收益归官方
         脚本步骤：
         1.接test_04，test_05
         2.强制解除关系
         3.校验接口状态和返回值数据
         4.检查打赏者余额，预期：100000 - 99900 = 100
         """
        des = '守护解除场景'

        # 准备测试数据
        self._prepare_test_data([
            {'uid': config.payUid, 'money': 100000}
        ])

        # 发送请求
        data = encodeData(
            payType='defend-break',
            money=self.defend_cp_config['break_money'],
            defend_id=self.defend_cp_id
        )
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'expected': 100}
        ])

        case_list[des] = result
