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
class TestPayVipRoom(unittest.TestCase):

    # select rid from xs_chatroom where uid=103273407 and property='vip'  个人房，vip＞5级不回收
    vipRoomRid = config.bb_user['vipRoomRid']

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
            expected = check['expected']
            if 'min_value' in check:
                assert_len(mysql.selectUserInfoSql(field, uid), check['min_value'])
            else:
                assert_equal(mysql.selectUserInfoSql(field, uid), expected)

    def test_01_personRoomPayGift(self):
        """
        用例描述：
        验证余额足够时，个人房打赏礼物分成满足师徒收益(非一代宗师)的基础上为：62:38，且收入在个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.个人房房间打赏礼物（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.62 =62 (money_cash_b)
        """
        des = '个人房礼物打赏给用户（mcb）'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 30, 'money_cash': 30, 'money_cash_b': 30, 'money_b': 10}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ])

        # 发送请求
        data = encodeData(payType='package', money=100, rid=self.vipRoomRid, giftId=config.giftId['5'])
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

    def test_02_personRoomPayBox(self):
        """
        用例描述：
        验证余额足够时，个人房打赏礼盒分成满足师徒收益(非一代宗师)的基础上为：62:38，且收入在个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.个人房房间打赏礼盒（打赏铜箱子）
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：700 - 600 = 100
        5.检查收箱用户账户余额，预期值为不小于：186
        """
        des = '个人房打赏box给用户（mcb）'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 400, 'money_cash': 100, 'money_cash_b': 100, 'money_b': 100}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ])

        # 发送请求
        data = encodeData(payType='package', money=600, rid=self.vipRoomRid, giftId=config.giftId['46'], star=1)
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'expected': 100},
            {'field': 'single_money', 'uid': config.rewardUid, 'min_value': 300 * 0.62},
            {'field': 'sum_money', 'uid': config.rewardUid, 'min_value': 300 * 0.62}
        ])

        case_list_b[des] = result

    def test_03_personRoomPayGiftToBrokerUser(self):
        """
        用例描述：
        验证余额足够时，个人房打赏礼物给工会成员分成为：70:30，且收入在个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.个人房房间打赏礼物（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.7 =70 (money_cash_b)
        """
        des = '个人房打赏钻石礼物给GS（mcb）'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money_cash_b': 100}},
            {'action': 'update_money', 'params': {'uid': config.gsUid}}
        ])

        # 发送请求
        data = encodeData(money=100, rid=self.vipRoomRid, uid=config.gsUid, giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 70},
            {'field': 'sum_money', 'uid': config.gsUid, 'expected': 70},
            {'field': 'sum_money', 'expected': 0}
        ])

        case_list_b[des] = result
