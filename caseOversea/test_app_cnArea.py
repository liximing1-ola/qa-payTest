# coding=utf-8
"""
APP 海外版支付测试 - 中文区域验证

验证中文区消费差异化分成体系。
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
    """中文区消费差异化验证"""

    @classmethod
    def setUpClass(cls) -> None:
        """测试前准备：设置用户大区为中文区"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()), bigarea_id=2)
        conMysql.updateUserRidInfoSql('vip', config.app_room['vip_rid'], area='cn')

    @classmethod
    def tearDownClass(cls) -> None:
        """测试后清理：恢复用户大区"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()))

    def test_01_cnAreaVipRoomPay(self, des: str = '中文大区个人房内打赏主播分成比例 70% 场景'):
        """
        个人房主播打赏验证
        
        用例描述：
        验证余额足够时，中文大区个人房打赏主播钻石礼物，打赏分成 70%
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 房间内一对一打赏普通礼物（打赏 600 分）
        3. 校验接口状态和返回值数据
        4. 检查被打赏者余额，预期为：600 * 0.7 = 420
        5. 检查打赏者余额，预期为：700 - 600 = 100
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, 700)
        conMysql.updateMoneySql(config.app_brokerUid)  # 账户余额清空
        
        # 2. 房间打赏（给主播）
        data = encodeAppData(payType='package', rid=config.app_room['vip_rid'], uid=config.app_brokerUid)
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.app_brokerUid, money_type='money_cash_b'), 420)
        
        case_list[des] = result

    def test_02_cnAreaVipRoomPay(self, des: str = '中文大区个人房内打赏非主播分成比例 80% 场景'):
        """
        个人房非主播打赏验证
        
        用例描述：
        验证余额足够时，中文大区个人房打赏非主播钻石礼物，打赏分成 80%
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 房间内一对一打赏普通礼物（打赏 600 分）
        3. 校验接口状态和返回值数据
        4. 检查被打赏者余额，预期为：600 * 0.8 = 480
        5. 检查打赏者余额，预期为：700 - 600 = 100
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, 700)
        conMysql.updateMoneySql(config.app_testUid)  # 账户余额清空
        conMysql.updateUserextendMoneyClearSql(config.app_testUid)  # 非主播钱包附加表账户余额清空
        
        # 2. 房间打赏（给非主播）
        data = encodeAppData(payType='package', rid=config.app_room['vip_rid'])
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.app_testUid, money_type='money_cash_personal'), 480)
        
        case_list[des] = result

    def test_03_CnAreaVipRoomGiveBox(self, des: str = '中文大区个人房内打赏非主播分成比例 80%（开箱子盲盒打赏）'):
        """
        个人房箱子打赏验证
        
        用例描述：
        验证余额足够时，中文大区个人房 1 对 1 打赏箱子，打赏分成非主播箱子为 80%
        
        脚本步骤：
        1. 构造数据（更新 xs_user_money，xs_user_commodity，xs_user_box）
        2. giveBox
        3. 校验接口状态和返回值数据
        4. 检查打赏者账户余额，预期值为：700 - 600 = 100
        5. 检查收箱用户账户余额，得到箱子/盲盒开出物品价值的 80%，预期 money 值为：不小于 240。开铜箱子最小为 30 钻。
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, money=400, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(config.app_testUid)
        conMysql.updateUserextendMoneyClearSql(config.app_testUid)  # 非主播钱包附加表账户余额清空
        
        # 2. 打赏箱子
        data = encodeAppData(payType='package',
                            giftId=config.giftId['46'],
                            rid=config.app_room['vip_rid'])
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 100)
        assert_len(conMysql.selectUserInfoSql('money_cash_personal', config.app_testUid, money_type='money_cash_personal'), 240)
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.app_testUid, money_type='money_cash_personal'),
                     conMysql.selectUserInfoSql(accountType='pay_change', uid=config.app_testUid))
        
        case_list[des] = result
