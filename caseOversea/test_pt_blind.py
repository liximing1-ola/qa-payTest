from common.Config import config
from common.method import reason
from common.conPtMysql import conMysql
import unittest
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_len, assert_equal
from common.basicData import encodePtData
from common.Consts import result, case_list
from common.runFailed import Retry
@Retry
class TestPayCreate(unittest.TestCase):

    def test_01_giveBlindPayChange(self, des='房间送盲盒场景'):
        """
        用例描述：
        验证房间内送盲盒逻辑正常
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity）
        2.giveBlind
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：400 - 300 = 100
        5.检查收盲盒用户账户余额，预期值为：大于50
        """
        conMysql.updateMoneySql(config.pt_payUid, money=100, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(config.pt_testUid)
        data = encodePtData(payType='package',money=300, giftId=config.giftId['773'])
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_len(conMysql.selectUserInfoSql('sum_money', config.pt_testUid), 50)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_testUid, money_type='money_cash_b'),
                     conMysql.selectUserInfoSql(accountType='pay_change', uid=config.pt_testUid))
        case_list[des] = result

    def test_02_giveBlindMorePeople(self, des='房间送多人多个盲盒场景'):
        """
        用例描述：
        验证房间内送盲盒给多个人时逻辑正常
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity）
        2.giveBox
        3.校验接口状态和返回值数据
        4.检查账户余额，预期值为：10000 - 1200*2*2 = 5200
        5.检查收盲盒用户账户余额，预期值为：大于500
        """
        conMysql.updateMoneySql(config.pt_payUid, money=10000)
        conMysql.updateMoneySql(config.pt_testUid)
        data = encodePtData(payType='package-more', num=2, money=1200, giftId=config.giftId['774'])
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 5200)
        assert_len(conMysql.selectUserInfoSql('sum_money', config.pt_testUid), 500)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_testUid, money_type='money_cash_b'),
                     conMysql.selectUserInfoSql(accountType='pay_change', uid=config.pt_testUid))
        case_list[des] = result