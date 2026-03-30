# coding=utf-8
"""
APP 海外版支付测试 - 日本区域验证

验证日语区消费差异化分成体系。
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
    """日语区消费差异化验证"""

    @classmethod
    def setUpClass(cls) -> None:
        """测试前准备：设置用户大区为日语区"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()), bigarea_id=10)

    @classmethod
    def tearDownClass(cls) -> None:
        """测试后清理：恢复用户大区"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()))

    def test_01_jaAreaNoBrokerMemberIMPay(self, des: str = '日语区私聊打赏非公会私聊分成 70%'):
        """
        私聊非公会成员打赏验证
        
        用例描述：
        检查日语区私聊一对一打赏礼物，非公会成员是一代宗师的用户收到打赏的 70%
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 私聊一对一打赏流程
        3. 校验接口和返回值数据，到账 money_cash_personal
        4. 检查打赏者数据，预期：600 - 600 = 0
        5. 检查被打赏者余额，预期：600 * 0.7 = 420
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, money=600)
        conMysql.updateMoneySql(config.app_testUid)
        conMysql.updateUserextendMoneyClearSql(config.app_testUid)  # 非主播钱包附加表账户余额清空
        
        # 2. 私聊打赏
        data = encodeAppData(payType='chat-gift')
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 0)
        assert_equal(
            conMysql.selectUserInfoSql('money_cash_personal', config.app_testUid, money_type='money_cash_personal'), 420)
        
        case_list[des] = result

    def test_02_jaAreaBrokerMemberIMPayGiveBox(self, des: str = '日语区私聊打赏公会主播私聊箱子分成 60%'):
        """
        私聊公会主播箱子打赏验证
        
        用例描述：
        检查日语区私聊一对一打赏箱子，公会成员收到打赏的 60%
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 私聊一对一打赏流程
        3. 校验接口和返回值数据，到账 money_cash_b
        4. 检查打赏者数据，预期：600 - 600 = 0
        5. 检查被打赏者余额，预期：不小于 300*60% = 180
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, money=600)
        conMysql.updateMoneySql(config.app_brokerUid)
        
        # 2. 私聊打赏箱子（给公会主播）
        data = encodeAppData(payType='chat-gift',
                            giftId=config.giftId['46'],
                            uid=config.app_brokerUid)
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 0)
        assert_len(conMysql.selectUserInfoSql('sum_money', config.app_brokerUid), 180)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.app_brokerUid, money_type='money_cash_b'),
                     conMysql.selectUserInfoSql(accountType='pay_change', uid=config.app_brokerUid))
        
        case_list[des] = result

    def test_03_jaAreaNoBrokerMemberRoomPay(self, des: str = '日语区房间打赏非公会私聊分成 70%'):
        """
        房间非公会成员打赏验证
        
        用例描述：
        检查日语区房间一对一打赏礼物，非公会成员是一代宗师的用户收到打赏的 70%
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 房间一对一打赏流程
        3. 校验接口和返回值数据，到账 money_cash_personal
        4. 检查打赏者数据，预期：600 - 600 = 0
        5. 检查被打赏者余额，预期：600 * 0.7 = 420
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, money=600)
        conMysql.updateMoneySql(config.app_testUid)
        conMysql.updateUserextendMoneyClearSql(config.app_testUid)  # 非主播钱包附加表账户余额清空
        
        # 2. 房间打赏
        data = encodeAppData(payType='package')
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 0)
        assert_equal(
            conMysql.selectUserInfoSql('money_cash_personal', config.app_testUid, money_type='money_cash_personal'), 420)
        
        case_list[des] = result
