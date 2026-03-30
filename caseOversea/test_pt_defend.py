# coding=utf-8
"""
APP 海外版支付测试 - 守护开通验证

验证个人守护开通的收益分成场景。
"""
import unittest
from common.Config import config
from common.conPtMysql import conMysql
from common.Request import post_request_session
from common.Assert import assert_code, assert_equal, assert_body
from common.method import format_reason
from common.basicData import encodeAppData
from common.Consts import case_list, result
from common.runFailed import Retry


@Retry
class TestPayCreate(unittest.TestCase):
    """APP 守护支付测试类"""

    @classmethod
    def setUpClass(cls) -> None:
        """测试前准备：设置用户大区"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()), bigarea_id=2)

    @classmethod
    def tearDownClass(cls) -> None:
        """测试后清理：恢复用户大区"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()))

    def test_01_defendPayChangMoney(self, des: str = '给非主播开通个人守护场景 80%'):
        """
        非主播守护开通验证
        
        用例描述：
        开通个人守护，收益分成在给非主播的基础上为 80%
        
        脚本步骤：
        1. 构造开通者和被守护者数据
        2. 开通价值 66600 钻守护
        3. 校验接口状态和返回值数据
        4. 检查打赏者余额
        5. 检查被打赏者余额，预期：66600 * 0.8 = 53280
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, money=66600)
        conMysql.updateMoneySql(config.app_testUid)
        conMysql.updateUserextendMoneyClearSql(config.app_testUid)  # 非主播钱包附加表账户余额清空
        
        # 2. 开通守护
        data = encodeAppData(payType='defend', money=66600)
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.app_testUid, money_type='money_cash_personal'), 53280)
        
        case_list[des] = result

    def test_02_defendPayChangMoney(self, des: str = '给主播开通个人守护场景 70%'):
        """
        主播守护开通验证
        
        用例描述：
        开通个人守护，收益分成在给主播的基础上为 70%
        
        脚本步骤：
        1. 构造开通者和被守护者数据
        2. 开通价值 66600 钻守护
        3. 校验接口状态和返回值数据
        4. 检查打赏者余额
        5. 检查被打赏者余额，预期：66600 * 0.7 = 46620
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, money=66600)
        conMysql.updateMoneySql(config.app_brokerUid)
        
        # 2. 开通守护（给主播）
        data = encodeAppData(payType='defend', money=66600, uid=config.app_brokerUid)
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.app_brokerUid, money_type='money_cash_b'), 46620)
        
        case_list[des] = result
