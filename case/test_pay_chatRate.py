from common.Config import config
from common.conMysql import conMysql as mysql
from common.Request import post_request_session
from common.method import checkUserVipExp
import unittest
from common.Assert import assert_code, assert_equal, assert_body, assert_len
from common.method import reason
from common.basicData import encodeData
from common.Consts import case_list, result
from common.runFailed import Retry


@Retry(max_n=3)
class TestPayChatRate(unittest.TestCase):
    """私聊打赏分成测试类"""

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
                mysql.updateMoneySql(**step['params'])
            elif step['action'] == 'clear_user_data':
                mysql.updateUserMoneyClearSql(config.payUid, config.rewardUid)
            elif step['action'] == 'delete_account':
                mysql.deleteUserAccountSql(step['table'], step['uid'])

    def _validate_db_state(self, checks):
        """验证数据库状态"""
        for check in checks:
            field = check['field']
            uid = check['uid']
            expected = check['expected']
            kwargs = check.get('kwargs', {})
            if 'assert_func' in check:
                check['assert_func'](mysql.selectUserInfoSql(field, uid, **kwargs), expected)
            else:
                assert_equal(mysql.selectUserInfoSql(field, uid, **kwargs), expected)

    def test_01_chatPayNoMoney(self):
        """
        用例描述：
        检查账户余额不足时，私聊一对一打赏
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊一对一打赏流程(礼物:棒棒糖)
        3.校验接口和返回值数据
        4.检查预期返回msg，预期：支付失败，提示Toast
        5.检查被打赏者余额,预期：0
        """
        des = '私聊打赏钱不足的场景'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'clear_user_data'},
            {'action': 'delete_account', 'table': 'broker_user', 'uid': config.rewardUid},
            {'action': 'delete_account', 'table': 'chatroom', 'uid': config.rewardUid}
        ])
        
        # 发送请求
        data = encodeData(payType='chat-gift', num=10, giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, reason(des, res))
        assert_body(res['body'], 'msg', '余额不足，无法支付', reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'uid': config.rewardUid, 'expected': 0}
        ])
        
        case_list[des] = result

    def test_02_chatPayGiftNormalBroker(self):
        """
        用例描述：
        验证私聊打赏礼物给GS时，到账为42%公会魅力值+30%个人魅力值
        脚本步骤：
        1.构造打赏者和主播数据
        2.私聊打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为：1000 * 0.42 = 420(money_cash) + 100 * 0.3 = 300（money_cash_b）
        6.检查打赏者余额.预期为：1000 - 1000 = 0
        """
        des = '私聊打赏礼物GS收72%'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': config.gsUid}}
        ])
        
        # 记录初始VIP等级
        vip_level = int(mysql.selectUserInfoSql('pay_room_money', config.payUid))
        
        # 发送请求
        data = encodeData(payType='chat-gift', uid=config.gsUid)
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 1000 * (config.rate - 0.2), 'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 300, 'kwargs': {'money_type': 'money_cash_b'}},
            {'field': 'sum_money', 'uid': config.gsUid, 'expected': 720},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0},
            {'field': 'pay_room_money', 'uid': config.payUid, 'expected': vip_level + checkUserVipExp(pay_off=1000)}
        ])
        
        case_list[des] = result

    def test_03_chatPayBoxNormalBroker(self):
        """
        用例描述：
        验证私聊打赏箱box给GS时，到账为42%公会魅力值+30%个人魅力值
        脚本步骤：
        1.构造打赏者和主播数据
        2.私聊打赏
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为不小于： 300 * 0.42 = 126(money_cash) + 300 * 0.3 = 90（money_cash_b）
        5.检查打赏者余额.预期为：600 - 600 = 0
        """
        des = '私聊打赏boxGS收72%'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 600}},
            {'action': 'update_money', 'params': {'uid': config.gsUid}}
        ])
        
        # 发送请求
        data = encodeData(
            payType='chat-gift',
            uid=config.gsUid,
            money=600,
            giftId=config.giftId['46'],
            star=1
        )
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 300 * 0.3, 'assert_func': assert_len},
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 300 * (config.rate - 0.2), 'kwargs': {'money_type': 'money_cash'}, 'assert_func': assert_len},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ])
        
        case_list[des] = result

    def test_04_chatPayGiftNormalUser(self):
        """
        用例描述：
        验证消费打赏礼物时，非一代宗师用户收72%个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为：1000 * 0.72 = 720(money_cash_b)
        5.检查打赏者余额.预期为：1000 - 1000 = 0
        """
        des = '私聊打赏非一代宗师用户分成72%（mcb）'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ])
        
        # 发送请求
        data = encodeData(payType='chat-gift')
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 720},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ])
        
        case_list[des] = result

    def test_05_chatPayBoxNormalUser(self):
        """
        用例描述：
        验证消费打赏箱子时，一代宗师用户收80%个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊打赏（打赏box）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为不小于：300 * 0.8 = 240(money_cash_b)
        5.检查打赏者余额.预期为：1000 - 600 = 400
        """
        des = '私聊打赏一代宗师分成80%（mcb）'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': config.masterUid}}
        ])
        
        # 发送请求
        data = encodeData(
            payType='chat-gift',
            uid=config.masterUid,
            money=600,
            giftId=config.giftId['66'],
            star=1
        )
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': config.masterUid, 'expected': 300 * 0.8, 'assert_func': assert_len},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 400}
        ])
        
        case_list[des] = result


