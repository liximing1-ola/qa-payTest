from common.Config import config
from common.conMysql import conMysql as mysql
from common.method import reason
import unittest
from time import sleep
from common.Assert import assert_body, assert_code, assert_equal
from common.Request import post_request_session
from common.basicData import encodeData
from common.Consts import case_list_c, result
from common.runFailed import Retry


@Retry(max_n=3)
class TestPayPunish(unittest.TestCase):

    def _prepare_test_data(self, setup_steps):
        """准备测试数据"""
        for step in setup_steps:
            action = step['action']
            params = step.get('params', {})
            if action == 'update_money':
                UserMoneyOperations.update(**params)

    def _validate_db_state(self, checks):
        """验证数据库状态"""
        for check in checks:
            field = check['field']
            uid = check.get('uid', config.payUid)
            money_type = check.get('money_type')
            expected = check['expected']
            assert_equal(mysql.selectUserInfoSql(field, uid, money_type), expected)

    def test_01_PayChangeTriggerPunish(self):
        """
        用例描述：
        验证收到打赏时，触发罚款流程，扣款账户：个人魅力值 -》现金余额 -》公会魅力值 -》APP币
        脚本步骤：
        1.构造打赏者和被罚款者数据
        2.被罚款者欠款：100分
        2.房间内一对一打赏（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.62 = 62
        5.检查消费记录表消费money
        6.检查消费记录表消费方式op
        """
        des = '打赏时触发罚款流程'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 100}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid, 'money': 20, 'money_cash': 20, 'money_debts': 100}}
        ])

        # 发送请求
        data = encodeData(money=100, rid=config.live_role['auto_rid'], giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))

        # 延迟处理NSQ消息
        sleep(2)

        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': config.rewardUid, 'money_type': 'money', 'expected': 2},
            {'field': 'single_money', 'uid': config.rewardUid, 'money_type': 'money_cash', 'expected': 0},
            {'field': 'single_money', 'uid': config.rewardUid, 'money_type': 'money_debts', 'expected': 0}
        ])

        case_list_c[des] = result
