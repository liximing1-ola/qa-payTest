from common.Config import config
from common.conPtMysql import conMysql
from common.Request import post_request_session
import unittest
from common.Assert import assert_code, assert_equal, assert_body
from common.method import reason
from common.basicData import encodePtData
from common.Consts import case_list, result
from common.runFailed import Retry
@Retry(max_n=2)
class TestPayCreate(unittest.TestCase):

    def test_01_IMPayNoMoney(self, des='私聊打赏余额不足的场景'):
        """
        用例描述：
        检查账户余额不足时，私聊一对一打赏
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊一对一打赏流程
        3.校验接口和返回值数据
        4.检查预期返回msg，预期：支付失败，提示Toast
        5.检查被打赏者余额,预期：0
        """
        conMysql.updateUserMoneyClearSql(config.pt_payUid, config.pt_testUid)
        conMysql.deleteUserAccountSql('broker_user', config.pt_testUid)
        conMysql.deleteUserAccountSql('chatroom', config.pt_testUid)
        data = encodePtData(payType='chat-gift', uid=config.pt_testUid)
        res = post_request_session(config.pt_pay_url, data, tokenName=config.appName['Partying'])
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, reason(des, res))
        assert_body(res['body'], 'msg', '餘額不足，無法支付', reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.pt_testUid), 0)
        case_list[des] = result

    def test_02_IMPayChangeMoney(self, des='私聊打赏场景'):
        """
        用例描述：
        检查账户余额充足时，私聊一对一打赏
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊一对一打赏流程
        3.校验接口和返回值数据
        4.检查打赏者数据，预期：600 - 600 = 0
        5.检查被打赏者余额,预期：600 * 0.8 = 480
        """
        conMysql.updateMoneySql(config.pt_payUid, money=600)
        conMysql.updateMoneySql(config.pt_testUid)
        data = encodePtData(payType='chat-gift', uid=config.pt_testUid)
        res = post_request_session(config.pt_pay_url, data, tokenName=config.appName['Partying'])
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('single_money', config.pt_testUid), 480)
        case_list[des] = result