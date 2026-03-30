# coding=utf-8
"""
APP 海外版支付测试 - 私聊卡购买验证

验证余额购买私聊卡的流程。
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


@Retry(max_n=3, func_prefix='test_01_chatPayCard')
class TestPayCreate(unittest.TestCase):
    """APP 私聊卡购买测试类"""

    @classmethod
    def setUpClass(cls) -> None:
        """测试前准备：检查礼物配置"""
        conMysql.checkXsGiftConfig()

    def test_01_chatPayCard(self, des: str = '余额购买私聊卡场景'):
        """
        余额购买私聊卡验证
        
        用例描述：
        验证余额兑换私聊卡流程
        
        脚本步骤：
        1. 构造用户数据
        2. 钻石兑换私聊卡流程
        3. 校验接口状态和返回值数据
        4. 检查账户钻石余额：money：160 - 16*10 = 0
        5. 检查账户背包私聊卡余额：cid:42598 10
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, money=100, money_cash=60)
        conMysql.deleteUserAccountSql('user_commodity', config.app_payUid)
        conMysql.deleteUserAccountSql('chat_pay_card_record', config.app_payUid)
        
        # 2. 钻石兑换私聊卡
        data = encodeAppData(payType='chat-pay-card')
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查账户钻石余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 0)
        
        # 5. 检查背包私聊卡余额
        assert_equal(conMysql.selectUserInfoSql('chat-pay-card', config.app_payUid), 10)
        
        case_list[des] = result