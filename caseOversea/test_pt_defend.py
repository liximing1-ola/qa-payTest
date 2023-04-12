from common.Config import config
from common.conPtMysql import conMysql
from common.Request import post_request_session
import unittest
from common.Assert import assert_code, assert_equal, assert_body
from common.method import reason
from common.basicData import encodePtData
from common.Consts import case_list, result
from common.runFailed import Retry


@Retry
# @unittest.skip('cn大区有调整，待处理')
class TestPayCreate(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()), bigarea_id=2)

    @classmethod
    def tearDownClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()))

    def test_01_defendPayChangMoney(self, des='给非主播开通个人守护场景80%'):
        """
        用例描述：
        开通个人守护，收益分成在给非主播的基础上为 80%
        脚本步骤：
        1.构造开通者和被守护者数据
        2.开通价值66600钻守护
        3.校验接口状态和返回值数据
        4.检查打赏者余额
        5.检查被打赏者余额,预期：66600 * 0.8 = 53280
        """
        conMysql.updateMoneySql(config.pt_payUid, money=66600)
        conMysql.updateMoneySql(config.pt_testUid)
        conMysql.updateUserextendMoneyClearSql(config.pt_testUid)  # 非主播钱包附加表账户余额清空
        data = encodePtData(payType='defend', money=66600)
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'), 53280)
        case_list[des] = result

    def test_02_defendPayChangMoney(self, des='给主播开通个人守护场景70%'):
        """
        用例描述：
        开通个人守护，收益分成在给主播的基础上为 70%
        脚本步骤：
        1.构造开通者和被守护者数据
        2.开通价值66600钻守护
        3.校验接口状态和返回值数据
        4.检查打赏者余额
        5.检查被打赏者余额,预期：66600 * 0.7 = 46620
        """
        conMysql.updateMoneySql(config.pt_payUid, money=66600)
        conMysql.updateMoneySql(config.pt_brokerUid)
        data = encodePtData(payType='defend', money=66600,uid=config.pt_brokerUid)
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_brokerUid, money_type='money_cash_b'), 46620)
        case_list[des] = result
