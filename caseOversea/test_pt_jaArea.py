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

    """
    日语区消费差异化验证：
    1.日语区：非公会成员：52% /公会成员：60% （礼物打赏，箱子打赏）
    """
    @classmethod
    def setUpClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()), bigarea_id=10)

    @classmethod
    def tearDownClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()))

    def test_01_jaAreaNoBrokerMemberIMPay(self, des='日区非公会成员私聊分成52:48'):
        """
        用例描述：
        检查日语区私聊一对一打赏礼物，非公会成员收到打赏的52%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊一对一打赏流程
        3.校验接口和返回值数据
        4.检查打赏者数据，预期：600 - 600 = 0
        5.检查被打赏者余额,预期：600 * 0.52 = 312
        """
        conMysql.updateMoneySql(config.pt_payUid, money=600)
        conMysql.updateMoneySql(config.pt_testUid)
        data = encodePtData(payType='chat-gift')
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_testUid, money_type='money_cash'), 312)
        case_list[des] = result

    def test_02_jaAreaBrokerMemberIMPayGiveBox(self, des='日区公会成员私聊分成60:40'):
        """
        用例描述：
        检查日语区私聊一对一打赏箱子，公会成员收到打赏的60%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊一对一打赏流程
        3.校验接口和返回值数据
        4.检查打赏者数据，预期：600 - 600 = 0
        5.检查被打赏者余额,预期：600 * 0.6 = 360
        """
        conMysql.updateMoneySql(config.pt_payUid, money=600)
        conMysql.updateMoneySql(config.pt_brokerUid)
        data = encodePtData(payType='chat-gift', giftId=config.giftId['46'], uid=config.pt_brokerUid)
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 0)
        assert_len(conMysql.selectUserInfoSql('sum_money', config.pt_brokerUid), 360)
        case_list[des] = result

    def test_03_jaAreaNoBrokerMemberRoomPay(self, des='日区非公会成员房间分成52:48'):
        """
        用例描述：
        验证日语区商业房打赏礼物，非公会成员收到打赏的52%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.52 = 312
        """
        conMysql.updateMoneySql(config.pt_payUid, 600)
        conMysql.updateMoneySql(config.pt_testUid)
        data = encodePtData(payType='package')
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_testUid, money_type='money_cash'), 312)
        case_list[des] = result

    def test_04_jaAreaBrokerMemberGiveBoxPay(self, des='日区公会成员房间分成60:40'):
        """
        用例描述：
        验证日语区商业房打赏箱子，公会成员收到打赏的60%
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
        2.giveBox
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：700 - 600 = 100
        5.检查收箱用户账户余额，预期值为：大于100
        """
        conMysql.updateMoneySql(config.pt_payUid, money=400, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(config.pt_brokerUid)
        data = encodePtData(payType='package', uid=config.pt_brokerUid, giftId=config.giftId['46'])
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_len(conMysql.selectUserInfoSql('sum_money', config.pt_brokerUid), 180)
        case_list[des] = result