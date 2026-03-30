# coding=utf-8
"""
APP 海外版支付测试 - 房间打赏验证

验证房间场景下的打赏功能，包括余额不足和正常打赏。
"""
import unittest
from common.Config import config
from common.method import format_reason
from common.conPtMysql import conMysql
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_equal
from common.basicData import encodeAppData
from common.Consts import case_list, result
from common.runFailed import Retry


@Retry
class TestPayCreate(unittest.TestCase):
    """APP 房间打赏测试类"""

    @classmethod
    def setUpClass(cls) -> None:
        """测试前准备：设置用户大区和房间属性"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()), bigarea_id=2)
        conMysql.updateUserRidInfoSql('vip', config.app_room['vip_rid'], area='cn')

    @classmethod
    def tearDownClass(cls) -> None:
        """测试后清理：恢复用户大区"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()))

    def test_01_RoomPayNoMoney(self, des: str = '房间打赏但余额不足的场景'):
        """
        房间打赏余额不足验证
        
        用例描述：
        验证余额不足时，房间一对一打赏
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 房间内一对一打赏流程
        3. 校验接口状态和返回值数据
        4. 检查预期返回 msg，预期：支付失败
        5. 检查被打赏者余额，预期：0
        
        Args:
            des: 测试描述
        """
        # 1. 清空用户余额
        conMysql.updateUserMoneyClearSql(config.app_payUid, config.app_testUid)
        
        # 2. 尝试房间打赏
        data = encodeAppData(payType='package')
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, format_reason(des, res))
        assert_body(res['body'], 'msg', '餘額不足，無法支付', format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_testUid), 0)
        
        case_list[des] = result

    def test_02_RoomPayChangeMoney(self, des: str = '商业房 1V1 打赏非主播 70% 场景'):
        """
        房间打赏正常场景验证
        
        用例描述：
        验证余额足够时，非直播类型房间一对一打赏非主播，打赏分成满足师徒收益 (一代宗师) 的基础上为：70:30
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 房间内一对一打赏（打赏 600 分）
        3. 校验接口状态和返回值数据
        4. 检查被打赏者余额，预期为：600 * 0.7 = 420
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, 700)
        conMysql.updateMoneySql(config.app_testUid)
        conMysql.updateUserextendMoneyClearSql(config.app_testUid)  # 非主播钱包附加表账户余额清空
        
        # 2. 房间打赏
        rid = conMysql.select_user_chatroom('business', bigarea_id=2)
        data = encodeAppData(payType='package', rid=rid)
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查被打赏者收益
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.app_testUid, money_type='money_cash_personal'), 420)
        
        case_list[des] = result
