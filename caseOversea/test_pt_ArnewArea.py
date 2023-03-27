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
    阿语区消费差异化验证：
    1.商业房内打赏分成比例50%（普通钻石礼物打赏公会主播50%）
    2.商业房内打赏分成开出物品价值的比例50%（开箱子盲盒打赏）
    3.1v1私聊打赏分成比例50%（普通钻石礼物打赏分成）
    4.阿语区联盟房打赏分成50%
    5.主播用户身份到账xs_user_money.money_cash。
    6.房间/私聊打赏非主播用户身份到账新字段xs_user_money_extend.money_cash_personal,7:3分成
    """

    @classmethod
    def setUpClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()), bigArea_id=3)
        conMysql.updateUserRidInfoSql('business', config.pt_room['business_joy_ar'], area='ar')

    @classmethod
    def tearDownClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()))

    def test_01_arNewAreaVipRoomPay(self, des='阿语大区商业房礼物打赏主播分成55场景'):
        """
        用例描述：
        验证余额足够时，阿语大区商业房打赏普通礼物,打赏分成满足师徒收益(一代宗师)的基础上为5：5
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏主播普通礼物（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.5 = 300
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_brokerUid)  # 公会主播账户余额清空
        data = encodePtData(payType='package',uid=config.pt_brokerUid, rid=config.pt_room['business_joy_ar'])
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_brokerUid, money_type='money_cash'), 300)
        case_list[des] = result

    def test_02_arNewAreaVipRoomGiveBox(self, des='阿语大区商业房箱子打赏主播55分成场景'):
        """
        用例描述：
        验证余额足够时，阿语大区商业房1对1打赏箱子,打赏分成满足师徒收益(一代宗师)的基础上为5：5
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
        2.giveBox
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：700 - 600 = 100
        5.检查收箱用户账户余额，得到箱子/盲盒开出物品价值的50%，预期money值为：不小于150。开铜箱子最小为30钻。
        """
        conMysql.updateMoneySql(config.pt_payUid, money=400, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(config.pt_brokerUid)
        data = encodePtData(payType='package',
                            giftId=config.giftId['46'],uid=config.pt_brokerUid,
                            rid=config.pt_room['business_joy_ar'])
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_len(conMysql.selectUserInfoSql('single_money', config.pt_brokerUid, money_type='money_cash'), 150)
        assert_equal(conMysql.selectUserInfoSql('single_money',
                                                config.pt_brokerUid,
                                                money_type='money_cash'),
                     conMysql.selectUserInfoSql(accountType='pay_change', uid=config.pt_brokerUid))
        case_list[des] = result

    def test_03_arNewAreaChatPay(self, des='阿语大区私聊礼物打赏主播55分成场景'):
        """
        用例描述：
        验证余额足够时，阿语大区私聊打赏主播普通钻石礼物,打赏分成满足师徒收益(一代宗师)的基础上为5:5
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊内一对一打赏普通礼物（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.5 = 300
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_brokerUid)  # 账户余额清空
        data = encodePtData(payType='chat-gift',uid=config.pt_brokerUid,)
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_brokerUid, money_type='money_cash'), 300)
        case_list[des] = result

    def test_04_arNewAreaUnionRoomPay(self, des='阿语大区联盟房礼物打赏主播55分成场景'):
        """
        用例描述：
        验证余额足够时，阿语区联盟房间1对1打赏礼物,打赏分成满足师徒收益(一代宗师)的基础上为：50%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.5 = 300
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_brokerUid)
        data = encodePtData(payType='package', rid=config.pt_room['union_ar'],uid=config.pt_brokerUid,)
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_brokerUid, money_type='money_cash'), 300)
        case_list[des] = result

    def test_05_arNewAreaVipRoomPay(self, des='阿语大区商业房礼物打赏非主播分成73分场景'):
        """
        用例描述：
        验证余额足够时，阿语大区商业房打赏非主播钻石礼物为7:3，到账xs_user_money_extend.money_cash_personal
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏普通礼物（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.7 = 420
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_testUid)  # 非主播账户余额清空
        conMysql.updateUserExtendMoneyClearSql(config.pt_testUid)  # 非主播钱包附加表账户余额清空
        data = encodePtData(payType='package', rid=config.pt_room['business_joy_ar'])
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'), 420)
        case_list[des] = result

    def test_06_arNewAreaChatPay(self, des='阿语大区私聊礼物打赏非主播73分成场景'):
        """
        用例描述：
        验证余额足够时，阿语大区私聊打赏主播普通钻石礼物,打赏分成满足师徒收益(一代宗师)的基础上为7:3
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊内一对一打赏普通礼物（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.7 = 420
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_testUid)  # 非主播账户余额清空
        conMysql.updateUserExtendMoneyClearSql(config.pt_testUid)  # 非主播钱包附加表账户余额清空
        data = encodePtData(payType='chat-gift')
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash'), 420)
        case_list[des] = result
