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
class TestPayCreate(unittest.TestCase):

    def test_01_defendPayChangMoney(self, des='开通个人守护场景'):
        """
        用例描述：
        开通个人守护，收益分成在师父收益(一代宗师)的基础上为 70:30
        脚本步骤：
        1.构造开通者和被守护者数据
        2.开通价值66600钻守护
        3.校验接口状态和返回值数据
        4.检查打赏者余额
        5.检查被打赏者余额,预期：66600 * 0.7 = 36400
        """
        conMysql.updateMoneySql(config.pt_payUid, money=66600)
        conMysql.updateMoneySql(config.pt_testUid)
        data = encodePtData(payType='defend', money=66600)
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_testUid), 46620)
        case_list[des] = result
