# coding=utf-8
"""
APP 海外版支付测试 - 马来西亚区域验证

验证马来区消费差异化分成体系。
"""
import unittest
from common.Config import config
from common.method import format_reason
from common.conPtMysql import conMysql
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_len, assert_equal
from common.basicData import encodeAppData
from common.Consts import result, case_list
from common.conRedis import conRedis


@unittest.skip('马来大区已关闭合并到印尼')
class TestPayCreate(unittest.TestCase):
    """马来区消费差异化验证"""

    @classmethod
    def setUpClass(cls) -> None:
        """测试前准备：设置用户大区为马来区，清理 Redis 缓存"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()), bigarea_id=9)
        conRedis.delKey('User.Big.Area.Id', config.app_user.values())
        conRedis.delKey('User.Big.Area', config.app_user.values())

    @classmethod
    def tearDownClass(cls) -> None:
        """测试后清理：恢复用户大区"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()))

    def test_01_msAreaFleetRoomPay(self, des: str = '马来区家族房/个人房礼物非主播打赏 80% 分成'):
        """
        家族房礼物打赏验证
        
        用例描述：
        1. 构造打赏者和被打赏者数据
        2. 房间内一对一打赏（打赏 600 分）
        3. 校验接口状态和返回值数据，到账 money_cash_personal
        4. 检查被打赏者余额，预期为：600 * 0.8 = 480
        5. 检查打赏者余额，预期为：700 - 600 = 100
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, 700)
        conMysql.updateMoneySql(config.app_testUid)
        conMysql.updateUserextendMoneyClearSql(config.app_testUid)  # 非主播钱包附加表账户余额清空
        
        # 2. 房间打赏
        rid = conMysql.select_user_chatroom(property='vip', bigarea_id=9)
        data = encodeAppData(payType='package', rid=rid)
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.app_testUid, money_type='money_cash_personal'), 480)
        
        case_list[des] = result

    def test_02_msAreaFleetRoomGiveBox(self, des: str = '马来区家族房打赏非主播送箱子 80% 分成场景'):
        """
        家族房箱子打赏验证
        
        用例描述：
        验证余额足够时，马来区家族房 1 对 1 打赏箱子，打赏分成满足非主播上为 80%
        
        脚本步骤：
        1. 构造数据（更新 xs_user_money，xs_user_commodity，xs_user_box）
        2. giveBox
        3. 校验接口状态和返回值数据，到账 money_cash_personal
        4. 检查打赏者账户余额，预期值为：700 - 600 = 100
        5. 检查收箱用户账户余额，预期值为：不小于 240
        
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
                            rid=conMysql.select_user_chatroom(property='vip', bigarea_id=9))
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 100)
        assert_len(conMysql.selectUserInfoSql('money_cash_personal', config.app_testUid, money_type='money_cash_personal'), 240)
        assert_equal(
            conMysql.selectUserInfoSql('money_cash_personal', config.app_testUid, money_type='money_cash_personal'),
            conMysql.selectUserInfoSql(accountType='pay_change', uid=config.app_testUid))
        
        case_list[des] = result

    def test_03_msAreaBrokerMemberIMPay(self, des: str = '马来区私聊打赏主播分成 50%'):
        """
        私聊主播打赏验证
        
        用例描述：
        检查马来区私聊一对一打赏礼物，公会成员是一代宗师的用户收到打赏的 50%
        
        脚本步骤：
        1. 构造打赏者和被打赏者数据
        2. 私聊一对一打赏流程
        3. 校验接口和返回值数据，到账 money_cash_b
        4. 检查打赏者数据，预期：700 - 600 = 100
        5. 检查被打赏者余额，预期：600 * 0.5 = 300
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, 700)
        conMysql.updateMoneySql(config.app_brokerUid)  # 非主播账户余额清空
        
        # 2. 私聊打赏（给主播）
        data = encodeAppData(payType='chat-gift', uid=config.app_brokerUid)
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.app_brokerUid, money_type='money_cash_b'), 300)
        
        case_list[des] = result
