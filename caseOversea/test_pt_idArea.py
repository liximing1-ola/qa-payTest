from common.Config import config
from common.method import reason
from common.conPtMysql import conMysql
import unittest
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_len, assert_equal
from common.basicData import encodePtData
from common.Consts import result, case_list
from common.runFailed import Retry
from common.conRedis import conRedis


@Retry
class TestPayCreate(unittest.TestCase):
    """
    印尼区消费差异化验证：
    1.家族房/个人房内打赏主播分成比例70%（钻石礼物打赏，箱子打赏）
    2.家族房/个人房内打赏非主播分成比例80%（钻石礼物打赏，箱子打赏）
    3.私聊打赏主播/非主播，都是50%
    """

    @classmethod
    def setUpClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()), bigarea_id=5)
        conMysql.updateUserRidInfoSql('fleet', config.pt_room['id_fleet'], area='id')
        conRedis.delKey('User.Big.Area.Id', config.pt_user.values())
        conRedis.delKey('User.Big.Area', config.pt_user.values())

    @classmethod
    def tearDownClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()))

    def test_01_idAreaFleetRoomPay(self, des='印尼区家族房礼物非主播打赏80%分成'):
        """
        用例描述：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏（打赏600分）
        3.校验接口状态和返回值数据,到账money_cash_personal
        4.检查被打赏者余额，预期为：600 * 0.8 = 480
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_testUid)
        conMysql.updateUserextendMoneyClearSql(config.pt_testUid)  # 非主播钱包附加表账户余额清空
        data = encodePtData(payType='package', rid=conMysql.select_user_chatroom(property='fleet', bigarea_id=5))
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(
            conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'), 480)
        case_list[des] = result

    def test_02_idAreaFleetRoomGiveBox(self, des='印尼区家族房打赏非主播送箱子80%分成场景'):
        """
        用例描述：
        验证余额足够时，印尼区家族房1对1打赏箱子,打赏分成满足师徒收益(一代宗师)的基础上为80%
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
        2.giveBox
        3.校验接口状态和返回值数据，到账money_cash_personal
        4.检查打赏者账户余额，预期值为：700 - 600 = 100
        5.检查收箱用户账户余额，预期值为：不小于240
        """
        conMysql.updateMoneySql(config.pt_payUid, money=400, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(config.pt_testUid)
        conMysql.updateUserextendMoneyClearSql(config.pt_testUid)  # 非主播钱包附加表账户余额清空
        data = encodePtData(payType='package',
                            giftId=config.giftId['46'],
                            rid=conMysql.select_user_chatroom(property='fleet', bigarea_id=5))
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_len(
            conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'), 240)
        assert_equal(
            conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'),
            conMysql.selectUserInfoSql(accountType='pay_change', uid=config.pt_testUid))
        case_list[des] = result

    def test_03_idAreaBrokerMemberIMPay(self, des='印尼区私聊打赏主播分成50%'):
        """
        用例描述：
        检查印尼区私聊一对一打赏礼物，公会成员是一代宗师的用户收到打赏的50%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊一对一打赏流程
        3.校验接口和返回值数据，到账money_cash_b
        4.检查打赏者数据，预期：700 - 600 = 100
        5.检查被打赏者余额,预期：600 * 0.5 = 300
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_brokerUid)  # 非主播账户余额清空
        data = encodePtData(payType='chat-gift', uid=config.pt_brokerUid)
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_brokerUid, money_type='money_cash_b'), 300)
        case_list[des] = result

    def test_04_idAreaNoBrokerMemberIMPay(self, des='印尼区私聊打赏非主播分成50%'):
        """
        用例描述：
        检查印尼区私聊一对一打赏礼物，非公会成员是一代宗师的用户收到打赏的50%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊一对一打赏流程
        3.校验接口和返回值数据，到账money_cash_personal
        4.检查打赏者数据，预期：700 - 600 = 100
        5.检查被打赏者余额,预期：600 * 0.5 = 300
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_testUid)  # 非主播账户余额清空
        conMysql.updateUserextendMoneyClearSql(config.pt_testUid)  # 非主播钱包附加表账户余额清空
        data = encodePtData(payType='chat-gift')
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(
            conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'), 300)
        case_list[des] = result
