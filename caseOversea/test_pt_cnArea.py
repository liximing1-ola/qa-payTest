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
# @unittest.skip('cn大区有调整，待处理')
class TestPayCreate(unittest.TestCase):
    """
    中文区消费差异化验证：
    1.个人房内打赏主播分成比例70%（普通钻石礼物打赏）到账money_cash_b
    2.个人房内打赏非主播分成比例80%（普通钻石礼物打赏）到账money_cash_personal
    3.个人房内打赏非主播分成开出物品价值的比例80%（开箱子盲盒打赏）到账money_cash_personal
    4.1v1私聊打赏非主播分成比例80%（普通钻石礼物打赏分成）到账money_cash_personal
    5.私聊打赏主播分成比例70%（普通钻石礼物打赏分成）到账money_cash_b
    6.商业厅打赏主播分成比例70%（普通钻石礼物打赏）到账money_cash_b
    7.商业厅内打赏非主播分成比例70%（普通钻石礼物打赏）到账money_cash_personal
    """

    @classmethod
    def setUpClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()), bigArea_id=2)
        conMysql.updateUserRidInfoSql('vip', config.pt_room['vip_rid'], area='cn')

    @classmethod
    def tearDownClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()))

    def test_01_cnAreaVipRoomPay(self, des='中文大区个人房内打赏主播分成比例70%场景'):
        """
        用例描述：
        验证余额足够时，中文大区个人房打赏主播钻石礼物,打赏分成70%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏普通礼物（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.7 = 420
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_brokerUid)  # 账户余额清空
        data = encodePtData(payType='package', rid=config.pt_room['vip_rid'],uid=config.pt_brokerUid)
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_brokerUid, money_type='money_cash_b'), 420)
        case_list[des] = result

    def test_02_cnAreaVipRoomPay(self, des='中文大区个人房内打赏非主播分成比例80%场景'):
        """
        用例描述：
        验证余额足够时，中文大区个人房打赏非主播钻石礼物,打赏分成80%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏普通礼物（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.8 = 480
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_testUid)  # 账户余额清空
        conMysql.updateUserExtendMoneyClearSql(config.pt_testUid)  # 非主播钱包附加表账户余额清空
        data = encodePtData(payType='package', rid=config.pt_room['vip_rid'])
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'), 480)
        case_list[des] = result

    def test_03_CnAreaVipRoomGiveBox(self, des='中文大区个人房内打赏非主播分成比例80%（开箱子盲盒打赏）'):
        """
        用例描述：
        验证余额足够时，中文大区个人房1对1打赏非主播箱子,打赏分成开出物品的基础上为80%
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
        2.giveBox
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：700 - 600 = 100
        5.检查收箱用户账户余额，得到箱子/盲盒开出物品价值的80%，预期money值为：不小于240。开铜箱子最小为30钻。
        """
        conMysql.updateMoneySql(config.pt_payUid, money=400, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(config.pt_testUid)
        conMysql.updateUserExtendMoneyClearSql(config.pt_testUid)  # 非主播钱包附加表账户余额清空
        data = encodePtData(payType='package',
                            giftId=config.giftId['46'],
                            rid=config.pt_room['vip_rid'])
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_len(conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'), 240)
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'),
                     conMysql.selectUserInfoSql(accountType='pay_change', uid=config.pt_testUid))
        case_list[des] = result

    def test_04_cnAreaChatPay(self, des='中文大区1v1私聊打赏非主播分成比例80%'):
        """
        用例描述：
        验证余额足够时，中文大区私聊打赏非主播普通礼物,80%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊内一对一打赏普通礼物（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.8 = 480
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_testUid)  # 账户余额清空
        conMysql.updateUserExtendMoneyClearSql(config.pt_testUid)  # 非主播钱包附加表账户余额清空
        data = encodePtData(payType='chat-gift')
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'), 480)
        case_list[des] = result

    def test_05_cnAreaChatPay(self, des='中文大区1v1私聊打赏主播分成比例70%'):
        """
        用例描述：
        验证余额足够时，中文大区私聊打赏非主播普通礼物,70%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊内一对一打赏普通礼物（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.7 = 420
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_brokerUid)  # 账户余额清空
        data = encodePtData(payType='chat-gift',uid=config.pt_brokerUid)
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_brokerUid, money_type='money_cash_b'), 420)
        case_list[des] = result

    def test_06_cnNewAreaBusinessRoomPay(self, des='中文大区商业房礼物打赏主播70%分成场景'):
        """
        用例描述：
        验证余额足够时，中文商业厅房1对1打赏礼物,打赏主播分成70%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏（打赏600分）
        3.校验接口状态和返回值数据，主播到账money_cash_b
        4.检查被打赏者余额，预期为：600 * 0.7 = 420
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_brokerUid)
        data = encodePtData(payType='package',
                            rid=conMysql.select_user_chatroom('business', bigArea_id=2), uid=config.pt_brokerUid)
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_brokerUid, money_type='money_cash_b'), 420)
        case_list[des] = result

    def test_07_cnNewAreaBusinessRoomPay(self, des='中文大区商业房礼物打赏非主播70%分成场景'):
        """
        用例描述：
        验证余额足够时，中文商业厅房1对1打赏礼物,打赏非主播分成70%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏（打赏600分）
        3.校验接口状态和返回值数据，主播到账money_cash_b
        4.检查被打赏者余额，预期为：600 * 0.7 = 420
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_testUid)
        conMysql.updateUserExtendMoneyClearSql(config.pt_testUid)  # 非主播钱包附加表账户余额清空
        data = encodePtData(payType='package',
                            rid=conMysql.select_user_chatroom('business', bigArea_id=2))
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'), 420)
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'),
                     conMysql.selectUserInfoSql(accountType='pay_change', uid=config.pt_testUid))
        case_list[des] = result

