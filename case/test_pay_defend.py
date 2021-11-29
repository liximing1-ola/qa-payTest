from common.Config import config
from common.method import reason
import unittest
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_equal
from common import basicData
from common.Consts import case_list, result
from common.runFailed import Retry
from common.conMysql import conMysql
@Retry(max_n=3)
class TestPayCreate(unittest.TestCase):

    def test_01_defendPayChangMoney(self, des='开通个人守护场景'):
        """
        用例描述：
        开通个人守护，收益分成在师父收益的基础上为 62:38
        脚本步骤：
        1.构造开通者和被守护者数据
        2.开通价值52000钻守护
        3.校验接口状态和返回值数据
        4.检查打赏者余额
        5.检查被打赏者余额,预期：52000 * 0.62 = 32240
        """
        conMysql.updateMoneySql(config.payUid, money=52000)
        conMysql.updateMoneySql(config.rewardUid)
        data = basicData.encodeData(payType='defend', money=52000, uid=config.rewardUid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 0)
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.rewardUid), 32240)
        case_list[des] = result