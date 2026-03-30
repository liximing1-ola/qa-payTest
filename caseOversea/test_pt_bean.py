# coding=utf-8
"""
APP 海外版支付测试 - 金豆兑换验证

验证余额兑换金豆的流程和账户余额变化。
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


@Retry(max_n=3, func_prefix='test_01_moneyExchangeCoin')
class TestPayCreate(unittest.TestCase):
    """APP 支付创建测试类"""

    @classmethod
    def setUpClass(cls) -> None:
        """测试前准备：检查礼物配置"""
        conMysql.checkXsGiftConfig()

    def test_01_moneyExchangeCoin(self, des: str = '余额兑换金豆场景'):
        """
        余额兑换金豆验证
        
        用例描述：
        验证余额兑换金豆流程
        
        脚本步骤：
        1. 构造用户数据
        2. 金豆兑换流程
        3. 校验接口状态和返回值数据
        4. 检查账户钻石余额：money: 300 - 300 = 0
        5. 检查账户金豆余额：gold_coin: 600
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, money=300)
        
        # 2. 金豆兑换
        data = encodeAppData(payType='exchange_gold')
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查账户余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.app_payUid, money_type='gold_coin'), 600)
        
        case_list[des] = result
