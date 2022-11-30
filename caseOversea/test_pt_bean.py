from common.Config import config
from common.conPtMysql import conMysql
from common.Request import post_request_session
import unittest
from common.Assert import assert_code, assert_equal, assert_body
from common.method import reason
from common.basicData import encodePtData
from common.Consts import case_list, result
from common.runFailed import Retry


@Retry(max_n=3, func_prefix='test_01_moneyExchangeCoin')
class TestPayCreate(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        conMysql.checkXsGiftConfig()

    def test_01_moneyExchangeCoin(self, des='余额兑换金豆场景'):
        """
        用例描述：
        验证余额兑换金豆流程
        脚本步骤：
        1.构造用户数据
        2.金豆兑换流程
        3.校验接口状态和返回值数据
        4.检查账户钻石余额：money：300 - 300 = 0
        5.检查账户金豆余额：gold_coin：600
        """
        conMysql.updateMoneySql(config.pt_payUid, money=300)
        data = encodePtData(payType='exchange_gold')
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_payUid, money_type='gold_coin'), 600)
        case_list[des] = result
