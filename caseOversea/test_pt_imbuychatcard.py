from common.Config import config
from common.conPtMysql import conMysql
from common.Request import post_request_session
import unittest
from common.Assert import assert_code, assert_equal, assert_body
from common.method import reason
from common.basicData import encodePtData
from common.Consts import case_list, result
from common.runFailed import Retry


@Retry(max_n=3, func_prefix='test_01_chatPayCard')
class TestPayCreate(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        conMysql.checkXsGiftConfig()

    def test_01_chatPayCard(self, des='余额购买私聊卡场景'):
        """
        用例描述：
        验证余额兑换私聊卡流程
        脚本步骤：
        1.构造用户数据
        2.钻石兑换私聊卡流程
        3.校验接口状态和返回值数据
        4.检查账户钻石余额：money：160 - 16*10 = 0
        5.检查账户背包私聊卡余额：cid:42598 10
        """
        conMysql.updateMoneySql(config.pt_payUid, money=100,money_cash=60)
        conMysql.deleteUserAccountSql('user_commodity',config.pt_payUid)
        conMysql.deleteUserAccountSql('chat_pay_card_record',config.pt_payUid)
        data = encodePtData(payType='chat-pay-card')
        res = post_request_session(config.pt_pay_url, data, token_name='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('chat-pay-card', config.pt_payUid),10)
        case_list[des] = result
