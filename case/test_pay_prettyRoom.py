from common.Config import config
from common.method import reason
from common.conMysql import conMysql as mysql
import unittest
from common.Request import post_request_session
from common.Assert import assert_body, assert_code, assert_equal, assert_len
from common.basicData import encodeData
from common.Consts import case_list_b, result
from common.runFailed import Retry


@Retry(max_n=3)
class TestPayPrettyRoom(unittest.TestCase):
    prettyRid = config.bb_user['prettyRid']

    def _prepare_test_data(self, setup_steps):
        """准备测试数据"""
        for step in setup_steps:
            action = step['action']
            params = step.get('params', {})
            if action == 'update_money':
                UserMoneyOperations.update(**params)
            elif action == 'clear_user_money':
                UserMoneyOperations.update(params.get('uid', config.payUid))

    def _validate_db_state(self, checks):
        """验证数据库状态"""
        for check in checks:
            field = check['field']
            uid = check.get('uid', config.payUid)
            expected = check['expected']
            money_type = check.get('money_type')
            if 'min_value' in check:
                assert_len(mysql.selectUserInfoSql(field, uid, money_type=money_type), check['min_value'])
            else:
                assert_equal(mysql.selectUserInfoSql(field, uid, money_type=money_type), expected)

    def test_01_prettyRoomPayGiftToBrokerUser(self):
        """
        用例描述：
        验证靓号房打赏礼物给公会成员分成为62%且收入进公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.靓号房打赏礼物（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.62 = 62 (money_cash)
        """
        des = '靓号房打赏礼物GS分62%进公会魅力值'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money_cash_b': 250}},
            {'action': 'clear_user_money', 'params': {'uid': config.gsUid}}
        ])

        # 发送请求
        data = encodeData(money=100, rid=self.prettyRid, uid=config.gsUid, giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': config.gsUid, 'money_type': 'money_cash', 'expected': 100 * config.rate},
            {'field': 'sum_money', 'uid': config.gsUid, 'expected': 100 * config.rate},
            {'field': 'sum_money', 'expected': 150}
        ])

        case_list_b[des] = result

    def test_02_prettyRoomPayBox(self):
        """
        用例描述：
        验证靓号房打赏礼物给公会成员分成为62%且收入进公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.靓号房打赏（box 600分）
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：700 - 600 = 100
        5.检查收箱用户账户余额，预期值为：不小于186,(300*0.62=186)
        """
        des = '靓号房打赏礼盒GS分62%进公会魅力值'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 400, 'money_cash': 100, 'money_cash_b': 100, 'money_b': 100}},
            {'action': 'clear_user_money', 'params': {'uid': config.gsUid}}
        ])

        # 发送请求
        data = encodeData(money=600, uid=config.gsUid, rid=self.prettyRid, giftId=config.giftId['46'], star=1)
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'expected': 100},
            {'field': 'single_money', 'uid': config.gsUid, 'money_type': 'money_cash', 'min_value': 300 * config.rate}
        ])

        case_list_b[des] = result

    def test_03_prettyRoomPayGiftToNormalUser(self):
        """
        用例描述：
        验证靓号房打赏礼物给普通用户（非一代宗师）分成为62%且收入进个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.靓号房打赏礼物
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：100 - 100 = 0
        5.检查被打赏者账户余额，预期值为：100 * 0.62 = 62
        """
        des = '靓号房打赏普通用户进个人魅力值'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money_cash': 100}},
            {'action': 'clear_user_money', 'params': {'uid': config.rewardUid}}
        ])

        # 发送请求
        data = encodeData(money=100, rid=self.prettyRid, uid=config.rewardUid, giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 62},
            {'field': 'sum_money', 'expected': 0}
        ])

        case_list_b[des] = result
