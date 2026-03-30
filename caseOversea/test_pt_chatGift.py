# coding=utf-8
"""
APP 海外版支付测试 - 私聊打赏验证

验证私聊场景下的打赏功能，包括余额不足、正常打赏和箱子打赏。
"""
import unittest
from common.Config import config
from common.conPtMysql import conMysql
from common.Request import post_request_session
from common.Assert import assert_code, assert_equal, assert_body, assert_len
from common.method import format_reason
from common.basicData import encodeAppData
from common.Consts import case_list, result
from common.runFailed import Retry


@Retry(max_n=2)
class TestPayCreate(unittest.TestCase):
    """APP 私聊打赏测试类"""

    @classmethod
    def setUpClass(cls) -> None:
        """测试前准备：设置用户大区"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()), bigarea_id=2)

    @classmethod
    def tearDownClass(cls) -> None:
        """测试后清理：恢复用户大区"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()))

    def test_01_IMPayNoMoney(self, des: str = '私聊打赏余额不足场景'):
        """
        私聊打赏余额不足验证
        
        用例描述：
        检查账户余额不足时，私聊一对一打赏
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 私聊一对一打赏流程
        3. 校验接口和返回值数据
        4. 检查预期返回 msg，预期：支付失败，提示 Toast
        5. 检查被打赏者余额，预期：0
        
        Args:
            des: 测试描述
        """
        # 1. 清空用户余额
        conMysql.updateUserMoneyClearSql(config.app_payUid, config.app_testUid)
        
        # 2. 尝试私聊打赏
        data = encodeAppData(payType='chat-gift')
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, format_reason(des, res))
        assert_body(res['body'], 'msg', '餘額不足，無法支付', format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_testUid), 0)
        
        case_list[des] = result

    def test_02_IMPayChangeMoney(self, des: str = '私聊打赏礼物场景'):
        """
        私聊打赏正常场景验证
        
        用例描述：
        检查账户余额充足时，私聊一对一打赏礼物
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 私聊一对一打赏流程
        3. 校验接口和返回值数据
        4. 检查打赏者数据，预期：600 - 600 = 0
        5. 检查被打赏者余额，预期：600 * 0.8 = 480
        
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
        
        # 4. 检查账户余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.app_testUid, money_type='money_cash_personal'), 480)
        
        case_list[des] = result

    def test_03_IMPayGiveBox(self, des: str = '私聊打赏箱子场景'):
        """
        私聊打赏箱子验证
        
        用例描述：
        检查账户余额充足时，私聊一对一打赏箱子
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 私聊一对一打赏流程
        3. 校验接口和返回值数据
        4. 检查打赏者数据，预期：600 - 600 = 0
        5. 检查被打赏者余额，预期：不小于 240
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, money=600)
        conMysql.updateMoneySql(config.app_testUid)
        conMysql.updateUserextendMoneyClearSql(config.app_testUid)  # 非主播钱包附加表账户余额清空
        
        # 2. 私聊打赏箱子
        data = encodeAppData(payType='chat-gift', giftId=config.app_giftId['46'])
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查账户余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 0)
        # 5. 检查被打赏者收益（不小于 240）
        personal_money = conMysql.selectUserInfoSql('money_cash_personal', config.app_testUid, money_type='money_cash_personal')
        assert personal_money >= 240, f"预期不小于 240，实际：{personal_money}"
        
        case_list[des] = result
