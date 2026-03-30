# coding=utf-8
"""
APP 海外版支付测试 - 英语区域验证

验证英语区消费差异化分成体系。
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


@unittest.skip('老版本样式的英语分成体系，已替换上线新分成')
class TestPayCreate(unittest.TestCase):
    """英语区消费差异化验证"""

    @classmethod
    def setUpClass(cls) -> None:
        """测试前准备：设置用户大区为英语区"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()), bigarea_id=1)

    @classmethod
    def tearDownClass(cls) -> None:
        """测试后清理：恢复用户大区"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()))

    def test_01_enAreaIMPayGift(self, des: str = '英语区私聊打赏礼物 55 分成场景'):
        """
        私聊礼物打赏验证
        
        用例描述：
        检查账户余额充足时，英语区私聊打赏礼物分成为 1：0.5
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 私聊一对一打赏流程
        3. 校验接口和返回值数据
        4. 检查打赏者数据，预期：600 - 600 = 0
        5. 检查被打赏者余额，预期：600 * 0.5 = 300
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, money=600)
        conMysql.updateMoneySql(config.app_testUid)
        
        # 2. 私聊打赏
        data = encodeAppData(payType='chat-gift')
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('single_money', config.app_testUid, money_type='money_cash'), 300)
        
        case_list[des] = result

    def test_02_enAreaIMPayGiveBox(self, des: str = '英语区私聊打赏箱子 55 分成场景'):
        """
        私聊箱子打赏验证
        
        用例描述：
        检查账户余额充足时，英语区私聊打赏箱子分成为 1：0.5
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 私聊一对一打赏流程
        3. 校验接口和返回值数据
        4. 检查打赏者数据，预期：600 - 600 = 0
        5. 检查被打赏者余额，预期为：不小于 150
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, money=300, money_cash=100, money_b=100, money_cash_b=100)
        conMysql.updateMoneySql(config.app_testUid)
        
        # 2. 私聊打赏箱子
        data = encodeAppData(payType='chat-gift', giftId=config.giftId['46'])
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 0)
        assert_len(conMysql.selectUserInfoSql('sum_money', config.app_testUid), 150)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.app_testUid, money_type='money_cash_b'),
                     conMysql.selectUserInfoSql(accountType='pay_change', uid=config.app_testUid))
        
        case_list[des] = result

    def test_03_enAreaFleetRoomPay(self, des: str = '英语区家族房礼物打赏 55 分成场景'):
        """
        家族房礼物打赏验证
        
        用例描述：
        验证余额足够时，英语区家族房 1 对 1 打赏礼物，打赏分成满足师徒收益 (一代宗师) 的基础上为 1:0.5
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 房间内一对一打赏（打赏 600 分）
        3. 校验接口状态和返回值数据
        4. 检查被打赏者余额，预期为：600 * 0.5 = 300
        5. 检查打赏者余额，预期为：700 - 600 = 100
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, 700)
        conMysql.updateMoneySql(config.app_testUid)
        
        # 2. 房间打赏
        data = encodeAppData(payType='package', rid=config.app_room['fleet_normal_ar'])
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.app_testUid, money_type='money_cash'), 300)
        
        case_list[des] = result
