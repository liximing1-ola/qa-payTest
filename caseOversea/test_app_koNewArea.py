# coding=utf-8
"""
APP 海外版支付测试 - 韩国区域验证

验证韩语区消费差异化分成体系。
"""
import unittest
from common.Config import config
from common.method import format_reason
from common.conPtMysql import conMysql
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_len, assert_equal
from common.basicData import encodeAppData
from common.Consts import result, case_list
from common.runFailed import Retry


@Retry
class TestPayCreate(unittest.TestCase):
    """韩语区消费差异化验证"""

    @classmethod
    def setUpClass(cls) -> None:
        """测试前准备：设置用户大区为韩语区"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()), bigarea_id=4)

    @classmethod
    def tearDownClass(cls) -> None:
        """测试后清理：恢复用户大区"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()))

    def test_01_koAreaNoBrokerMemberIMPay(self, des: str = '韩语私聊打赏非主播分成 75%'):
        """
        私聊非公会成员打赏验证
        
        用例描述：
        检查韩语区私聊一对一打赏礼物，非公会成员是一代宗师的用户收到打赏的 75%
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 私聊一对一打赏流程
        3. 校验接口和返回值数据，到账 money_cash_personal
        4. 检查打赏者数据，预期：700 - 600 = 100
        5. 检查被打赏者余额，预期：600 * 0.75 = 450
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, 700)
        conMysql.updateMoneySql(config.app_testUid)  # 非主播账户余额清空
        conMysql.updateUserextendMoneyClearSql(config.app_testUid)  # 非主播钱包附加表账户余额清空
        
        # 2. 私聊打赏
        data = encodeAppData(payType='chat-gift')
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 100)
        assert_equal(
            conMysql.selectUserInfoSql('money_cash_personal', config.app_testUid, money_type='money_cash_personal'), 450)
        
        case_list[des] = result

    def test_02_koAreaBrokerMemberIMPay(self, des: str = '韩语私聊打赏主播分成 70%'):
        """
        私聊公会主播打赏验证
        
        用例描述：
        检查韩语区私聊一对一打赏礼物，公会成员是一代宗师的用户收到打赏的 70%
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 私聊一对一打赏流程
        3. 校验接口和返回值数据，到账 money_cash_b
        4. 检查打赏者数据，预期：700 - 600 = 100
        5. 检查被打赏者余额，预期：600 * 0.7 = 420
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, 700)
        conMysql.updateMoneySql(config.app_brokerUid)  # 非主播账户余额清空
        conMysql.updateUserextendMoneyClearSql(config.app_brokerUid)  # 非主播钱包附加表账户余额清空
        
        # 2. 私聊打赏（给公会主播）
        data = encodeAppData(payType='chat-gift', uid=config.app_brokerUid)
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.app_brokerUid, money_type='money_cash_b'), 420)
        
        case_list[des] = result

    def test_03_koNewAreaFleetRoomPay(self, des: str = '韩语区家族房礼物打赏主播 70% 分成场景'):
        """
        家族房主播打赏验证
        
        用例描述：
        验证余额足够时，韩语区家族房 1 对 1 打赏主播礼物，打赏分成满足师徒收益 (一代宗师) 的基础上为 70%
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 房间内一对一打赏（打赏 600 分）
        3. 校验接口状态和返回值数据，到账 money_cash_b
        4. 检查被打赏者余额，预期为：600 * 0.7 = 420
        5. 检查打赏者余额，预期为：700 - 600 = 100
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, 700)
        conMysql.updateMoneySql(config.app_brokerUid)
        
        # 2. 房间打赏（给主播）
        data = encodeAppData(payType='package', rid=config.app_room['fleet_normal_ar'], uid=config.app_brokerUid)
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.app_brokerUid, money_type='money_cash_b'), 420)
        
        case_list[des] = result
