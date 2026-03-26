from common.Config import config
from common.method import reason
from common.conMysql import conMysql as mysql
from common.Request import post_request_session
from common.method import calculate_vip_exp
import unittest
from common.Assert import assert_body, assert_code, assert_equal
from common.basicData import encodeData
from common.Consts import case_list, result
from common.runFailed import Retry


@Retry(max_n=3, func_prefix='test_02_roomChangePayCoin')
class TestPayCoin(unittest.TestCase):
    """coin支付测试类"""

    def setUp(self):
        """测试前置清理"""
        pass

    def tearDown(self):
        """测试后置清理"""
        pass

    def _prepare_test_data(self, setup_steps):
        """准备测试数据"""
        for step in setup_steps:
            if step['action'] == 'update_money':
                UserMoneyOperations.update(**step['params'])
            elif step['action'] == 'clear_user_data':
                mysql.updateUserMoneyClearSql(*step['uids'])

    def _validate_db_state(self, checks):
        """验证数据库状态"""
        for check in checks:
            field = check['field']
            uid = check['uid']
            expected = check['expected']
            kwargs = check.get('kwargs', {})
            assert_equal(mysql.selectUserInfoSql(field, uid, **kwargs), expected)

    def test_01_moneyChangeExchangeCoin(self):
        """
        用例描述：
        验证money兑换金币流程
        脚本步骤：
        1.构造用户数据
        2.金币兑换流程
        3.校验接口状态和返回值数据
        4.检查账户钻石余额：money：1000 - 600 = 400
        5.检查账户金币余额：gold_coin：600
        """
        des = '余额兑换金币场景'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}}
        ])
        
        # 发送请求
        data = encodeData(payType='exchange_gold')
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 400},
            {'field': 'single_money', 'uid': config.payUid, 'expected': 600, 'kwargs': {'money_type': 'gold_coin'}}
        ])
        
        case_list[des] = result

    def test_02_roomChangePayCoin(self):
        """
        用例描述：
        验证房间内打赏金币流程
        脚本步骤：
        1.构造用户数据
        2.房间打赏金币礼物流程(礼物：人气券)
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额（gold_coin） 100 - 20*2 = 60
        5.检查所有被打赏者账户余额（gold_coin）  20 * 0.6 = 12
        """
        des = '房间打赏金币礼物的场景'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'gold_coin': 100}},
            {'action': 'clear_user_data', 'uids': (config.rewardUid, config.masterUid)}
        ])
        
        # 记录初始VIP等级
        vip_level = int(mysql.selectUserInfoSql('pay_room_money', config.payUid))
        
        # 发送请求
        data = encodeData(
            payType='package-more',
            money=20,
            giftId=config.giftId['62'],
            giftType='coin'
        )
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': config.payUid, 'expected': 60, 'kwargs': {'money_type': 'gold_coin'}},
            {'field': 'single_money', 'uid': config.masterUid, 'expected': 12, 'kwargs': {'money_type': 'gold_coin'}},
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 12, 'kwargs': {'money_type': 'gold_coin'}},
            {'field': 'pay_room_money', 'uid': config.payUid, 'expected': vip_level + calculate_vip_exp(money_type='coin', pay_off=40)}
        ])
        
        case_list[des] = result
