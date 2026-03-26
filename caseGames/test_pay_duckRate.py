import unittest
from common.basicData import encodeData
from common.Assert import assert_body, assert_code, assert_equal
from common.Config import config
from common.Consts import case_list_b, result
from common.Request import post_request_session
from common.conMysql import conMysql
from common.method import reason
from common.runFailed import Retry
from common.Session import Session


@Retry
@unittest.skip('123')
class TestPayDuckRate(unittest.TestCase):
    rate_role = {
        "bid": 100011021,  # 公会的bid
        'rewardUid': 131554725,  # 打赏者
        'rewardedUid': 131564968,  # 被打赏者
    }

    def _prepare_test_data(self, setup_steps):
        """准备测试数据"""
        for step in setup_steps:
            action = step['action']
            params = step.get('params', {})
            if action == 'update_money':
                conMysql.updateMoneySql(**params)
            elif action == 'clear_user_money':
                conMysql.updateUserMoneyClearSql(params['uid1'], params.get('uid2'))
            elif action == 'check_user_broker':
                conMysql.checkUserBroker(params['uid'], bid=params['bid'])
            elif action == 'check_uid_white':
                conMysql.check_uid_white(params['uid'])

    def _validate_db_state(self, checks):
        """验证数据库状态"""
        for check in checks:
            field = check['field']
            uid = check['uid']
            expected = check['expected']
            assert_equal(conMysql.selectUserInfoSql(field, uid), expected)

    def test_01_roomPayCustomRate_60(self):
        """
        用例描述：
        tdr:后台自定义分成比例为60%
        脚本步骤：
        1.构造打赏者，被打赏者数据
        2.房间内打赏（打赏100分）
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：100 - 100 = 0
        5.检查被打赏者余额，预期为：100 * 0.6 = 60
        """
        des = '商业房打赏自定义分成:60'

        # 初始化session
        Session.getSession('rush')

        testUid = self.rate_role["rewardedUid"]  # 被打赏者
        payUid = self.rate_role["rewardUid"]  # 打赏者

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'clear_user_money', 'params': {'uid1': testUid, 'uid2': payUid}},
            {'action': 'update_money', 'params': {'uid': payUid, 'money': 100}},
            {'action': 'check_user_broker', 'params': {'uid': testUid, 'bid': self.rate_role["bid"]}},
            {'action': 'check_uid_white', 'params': {'uid': testUid}}
        ])

        # 发送请求
        data = encodeData(money=100, rid=200064778, uid=testUid, giftId=config.giftId['5'])
        res = post_request_session(config.rush_pay_url, data, token_name='rush')

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'uid': payUid, 'expected': 0},
            {'field': 'sum_money', 'uid': testUid, 'expected': 60}
        ])

        case_list_b[des] = result

    def test_02_chatPayCustomRate_60(self):
        """
        用例描述：
        tdr:后台自定义分成比例为60%
        脚本步骤：
        1.构造打赏者，被打赏者
        2.私聊打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：1000 - 1000 = 0
        5.检查被打赏者总余额，预期为：1000 * 0.6 = 600
        """
        des = '私聊打赏自定义分成:60'

        testUid = self.rate_role["rewardedUid"]  # 被打赏者
        payUid = self.rate_role["rewardUid"]

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'clear_user_money', 'params': {'uid1': testUid, 'uid2': payUid}},
            {'action': 'update_money', 'params': {'uid': payUid, 'money': 1000}},
            {'action': 'check_user_broker', 'params': {'uid': testUid, 'bid': self.rate_role["bid"]}},
            {'action': 'check_uid_white', 'params': {'uid': testUid}}
        ])

        # 发送请求
        data = encodeData(payType='chat-gift', uid=testUid)
        res = post_request_session(config.rush_pay_url, data, token_name='rush')

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'uid': payUid, 'expected': 0},
            {'field': 'sum_money', 'uid': testUid, 'expected': 600}
        ])

        case_list_b[des] = result

    def test_03_defendPayCustomRate_60(self):
        """
        用例描述：
        tdr:后台自定义分成比例为60%
        脚本步骤：
        1.构造打赏者，被打赏者
        2.开通守护
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：52000 - 52000 = 0
        5.检查被打赏者总余额，预期为：52000 * 0.6 = 31200
        """
        des = '个人守护打赏自定义分成:60'

        testUid = self.rate_role["rewardedUid"]  # 被打赏者
        payUid = self.rate_role["rewardUid"]

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'clear_user_money', 'params': {'uid1': testUid, 'uid2': payUid}},
            {'action': 'update_money', 'params': {'uid': payUid, 'money': 52000}},
            {'action': 'check_user_broker', 'params': {'uid': testUid, 'bid': self.rate_role["bid"]}},
            {'action': 'check_uid_white', 'params': {'uid': testUid}}
        ])

        # 发送请求
        data = encodeData(payType='defend', uid=testUid, money=52000)
        res = post_request_session(config.rush_pay_url, data, token_name='rush')

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'uid': payUid, 'expected': 0},
            {'field': 'sum_money', 'uid': testUid, 'expected': 31200}
        ])

        case_list_b[des] = result
