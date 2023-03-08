from common.Config import config
from common.method import reason
from common.conPtMysql import conMysql
import unittest
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_len, assert_equal
from common.basicData import encodePtData
from common.Consts import result, case_list
from common.runFailed import Retry
import time
from common.conRedis import conRedis


@Retry
class TestPayCreate(unittest.TestCase):
    """
    泰语区消费差异化验证：
    1.非华语区联盟房消费分成为30%(礼物打赏，箱子)
    """

    @classmethod
    def setUpClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()), bigarea_id=6)
        conMysql.updateUserRidInfoSql('union', config.pt_room['th_union'], area='th')

    @classmethod
    def tearDownClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()))
        time.sleep(0.3)
        conRedis.delKey('User.Big.Area.Id', config.pt_user.values())
        conRedis.delKey('User.Big.Area', config.pt_user.values())

    def test_01_thaiUnionRoomPay(self, des='泰区联盟房礼物打赏非主播80%分成场景'):
        """
        用例描述：
        验证余额足够时，泰语区联盟房间1对1打赏礼物,打赏非主播为：80%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏（打赏600分）
        3.校验接口状态和返回值数据,到账money_cash_personal
        4.检查被打赏者余额，预期为：600 * 0.8 = 480
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_testUid)
        conMysql.updateUserextendMoneyClearSql(config.pt_testUid)  # 非主播钱包附加表账户余额清空
        data = encodePtData(payType='package', rid=config.pt_room['th_union'])
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(
            conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'), 480)
        case_list[des] = result

    def test_02_thaiUnionRoomGiveBox(self, des='泰区联盟房送非主播箱子80%场景'):
        """
        用例描述：
        验证余额足够时，泰语区联盟房间1对1打赏箱子,打赏分成满足师徒收益(一代宗师)的基础上为：80%
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
        2.giveBox
        3.校验接口状态和返回值数据，到账money_cash_personal
        4.检查打赏者账户余额，预期值为：700 - 600 = 100
        5.检查收箱用户账户余额，预期值为：大于300*80% = 240，铜箱子最少300，再进行分成
        """
        conMysql.updateMoneySql(config.pt_payUid, money=400, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(config.pt_testUid)
        conMysql.updateUserextendMoneyClearSql(config.pt_testUid)  # 非主播钱包附加表账户余额清空
        data = encodePtData(payType='package',
                            uid=config.pt_testUid,
                            giftId=config.giftId['46'],
                            rid=config.pt_room['th_union'])
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

    def test_03_thAreaBrokerMemberIMPay(self, des='泰语大区私聊打赏主播分成70%'):
        """
        用例描述：
        检查泰语区私聊一对一打赏礼物，公会成员是一代宗师的用户收到打赏的70%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊一对一打赏流程
        3.校验接口和返回值数据，到账money_cash_b
        4.检查打赏者数据，预期：700 - 600 = 100
        5.检查被打赏者余额,预期：600 * 0.7 = 420
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_brokerUid)  # 非主播账户余额清空
        conMysql.updateUserextendMoneyClearSql(config.pt_brokerUid)  # 非主播钱包附加表账户余额清空
        data = encodePtData(payType='chat-gift', uid=config.pt_brokerUid)
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_brokerUid, money_type='money_cash_b'), 420)
        case_list[des] = result

    def test_04_thNewAreaUnionRoomPay(self, des='泰语区联盟房礼物打赏主播70%分成场景'):
        """
        用例描述：
        验证余额足够时，泰语区1对1打赏主播礼物,打赏分成上为70%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏（打赏600分）
        3.校验接口状态和返回值数据，到账money_cash_b
        4.检查被打赏者余额，预期为：600 * 0.7 = 420
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_brokerUid)
        data = encodePtData(payType='package',
                            rid=conMysql.select_user_chatroom(property='union', bigarea_id=6), uid=config.pt_brokerUid)
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_brokerUid, money_type='money_cash_b'), 420)
        case_list[des] = result

    def test_01_thAreaNoBrokerMemberIMPay(self, des='泰国区私聊打赏非主播分成80%'):
        """
        用例描述：
        检查泰语区私聊一对一打赏礼物，非公会成员是一代宗师的用户收到打赏的80%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊一对一打赏流程
        3.校验接口和返回值数据，到账money_cash_personal
        4.检查打赏者数据，预期：700 - 600 = 100
        5.检查被打赏者余额,预期：600 * 0.8 = 480
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
            conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'), 480)
        case_list[des] = result
