# coding=utf-8
"""
APP 海外版支付测试 - 盲盒打赏验证

验证房间内送盲盒的逻辑。
"""
import unittest
from time import sleep
from common.Config import config
from common.method import format_reason
from common.conPtMysql import conMysql
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_len, assert_equal
from common.basicData import encodeAppData
from common.Consts import result, case_list
from common.runFailed import Retry
from common.conRedis import conRedis


@Retry
class TestPayCreate(unittest.TestCase):
    """房间盲盒打赏测试类"""

    @classmethod
    def setUpClass(cls) -> None:
        """测试前准备：设置用户大区为泰国区"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()), bigarea_id=6)
        conMysql.updateUserRidInfoSql('union', config.app_room['th_union'], area='th')

    @classmethod
    def tearDownClass(cls) -> None:
        """测试后清理：恢复用户大区，清理 Redis 缓存"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()))
        sleep(0.3)
        conRedis.delKey('User.Big.Area.Id', config.app_user.values())
        conRedis.delKey('User.Big.Area', config.app_user.values())

    def test_01_giveBlindPayChange(self, des: str = '房间送盲盒场景'):
        """
        房间送盲盒验证
        
        用例描述：
        验证房间内送盲盒逻辑正常
        
        脚本步骤：
        1. 构造数据（更新 xs_user_money，xs_user_commodity）
        2. giveBlind
        3. 校验接口状态和返回值数据
        4. 检查打赏者账户余额，预期值为：400 - 300 = 100
        5. 检查收盲盒用户账户余额，预期值为：大于 30
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, money=100, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(config.app_testUid)
        conMysql.updateUserextendMoneyClearSql(config.app_testUid)  # 非主播钱包附加表账户余额清空
        
        # 2. 送盲盒
        data = encodeAppData(payType='package',
                            money=300,
                            rid=config.app_room['th_union'],
                            giftId=config.giftId['773'])
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 100)
        assert_len(conMysql.selectUserInfoSql('money_cash_personal', config.app_testUid), 30)
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.app_testUid, money_type='money_cash_personal'),
                     conMysql.selectUserInfoSql(accountType='pay_change', uid=config.app_testUid))
        
        case_list[des] = result

    def test_02_giveBlindMorePeople(self, des: str = '房间送多人多个盲盒场景'):
        """
        房间送多人盲盒验证
        
        用例描述：
        验证房间内送盲盒给多个人时逻辑正常
        
        脚本步骤：
        1. 构造数据（更新 xs_user_money，xs_user_commodity）
        2. giveBox
        3. 校验接口状态和返回值数据
        4. 检查账户余额，预期值为：10000 - 1200*2*2 = 5200
        5. 检查收盲盒用户账户余额，预期值为：大于 60
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, money=10000)
        conMysql.updateMoneySql(config.app_testUid)
        conMysql.updateUserextendMoneyClearSql(config.app_testUid)  # 非主播钱包附加表账户余额清空
        
        # 2. 送多人盲盒
        data = encodeAppData(payType='package-more',
                            num=2,
                            money=1200,
                            rid=config.app_room['th_union'],
                            giftId=config.giftId['774'])
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 5200)
        assert_len(conMysql.selectUserInfoSql('money_cash_personal', config.app_testUid), 60)
        
        case_list[des] = result
