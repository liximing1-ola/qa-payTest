from common.Config import config
from common.conMysql import conMysql
from common.Request import post_request_session
import unittest
from common.Assert import assert_code, assert_equal, assert_body
from common.method import reason
from common import basicData
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
        2.私聊一对一打赏流程(礼物:棒棒糖)
        3.校验接口和返回值数据
        4.检查预期返回msg，预期：支付失败，提示Toast
        5.检查被打赏者余额,预期：0
        """
        conMysql.updateUserMoneyClearSql(config.payUid, config.testUid)
        conMysql.deleteUserAccountSql('broker_user', config.testUid)
        conMysql.deleteUserAccountSql('chatroom', config.testUid)
        data = basicData.encodeData(payType='chat-gift', uid=config.testUid, num=10,
                                    giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, reason(des, res))
        assert_body(res['body'], 'msg', '余额不足，无法支付', reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.testUid), 0)
        case_list[des] = result