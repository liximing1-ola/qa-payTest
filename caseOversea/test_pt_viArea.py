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
# @unittest.skip('vi大区有调整，待处理')
class TestPayCreate(unittest.TestCase):
    """
    越南区消费差异化验证：
    1.商业房内打赏非主播分成比例70%（普通钻石礼物打赏）进money_Cash_personal
    2.商业房内打赏非主播分成开出物品价值的比例70%（开箱子盲盒打赏）
    3.1v1私聊打赏非主播分成比例50%（普通钻石礼物打赏分成）
    4.联盟房/个人房打赏非主播分成80%
    5、商业厅打赏主播分成比例70%，进money_Cash_b
    6、私聊打赏主播分成50%
    7、个人房打赏主播分成70%
    """

    @classmethod
    def setUpClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()), bigarea_id=7)
        conMysql.updateUserRidInfoSql('business', config.pt_room['business_joy_vi'], area='vn')

    @classmethod
    def tearDownClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()))

    def test_01_viAreaVipRoomPay(self, des='越南区区商业房礼物打赏非主播70%分成场景'):
        """
        用例描述：
        验证余额足够时，越南区区商业房打赏非主播钻石礼物,打赏分成70%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏普通礼物（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.7 = 420
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_testUid)  # 账户余额清空
        conMysql.updateUserextendMoneyClearSql(config.pt_testUid)  # 非主播钱包附加表账户余额清空
        data = encodePtData(payType='package', rid=conMysql.select_user_chatroom('business',bigarea_id=7))
        res = post_request_session(config.pt_pay_url, data, token_name='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'), 420)
        case_list[des] = result

    def test_02_viAreaVipRoomGiveBox(self, des='越南区区商业房箱子打赏非主播70%分成场景'):
        """
        用例描述：
        验证余额足够时，越南区商业房1对1打赏箱子,打赏分成非主播箱子为70%
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
        2.giveBox
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：700 - 600 = 100
        5.检查收箱用户账户余额，得到箱子/盲盒开出物品价值的70%，预期money值为：不小于210。开铜箱子最小为30钻。
        """
        conMysql.updateMoneySql(config.pt_payUid, money=400, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(config.pt_testUid)
        conMysql.updateUserextendMoneyClearSql(config.pt_testUid)  # 非主播钱包附加表账户余额清空
        data = encodePtData(payType='package',
                            giftId=config.giftId['46'],
                            rid=conMysql.select_user_chatroom('business',bigarea_id=7))
        res = post_request_session(config.pt_pay_url, data, token_name='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_len(conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'), 210)
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'),
                     conMysql.selectUserInfoSql(accountType='pay_change', uid=config.pt_testUid))
        case_list[des] = result

    def test_03_viAreaChatPay(self, des='越南区私聊打赏非主播礼物打赏55分成场景'):
        """
        用例描述：
        验证余额足够时，越南区私聊打赏普通礼物,打赏非主播分成为0.5
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊内一对一打赏普通礼物（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.5 = 300
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_testUid)  # 账户余额清空
        conMysql.updateUserextendMoneyClearSql(config.pt_testUid)  # 非主播钱包附加表账户余额清空
        data = encodePtData(payType='chat-gift')
        res = post_request_session(config.pt_pay_url, data, token_name='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'), 300)
        case_list[des] = result

    def test_04_viAreaUnionRoomPay(self, des='越南区区联盟个人房礼物非主播打赏80%分成场景'):
        """
        用例描述：
        验证余额足够时，越南区联盟房间1对1打赏礼物,打赏分成满足师徒收益(一代宗师)的基础上为：80%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.8 = 480
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_testUid)
        conMysql.updateUserextendMoneyClearSql(config.pt_testUid)  # 非主播钱包附加表账户余额清空
        data = encodePtData(payType='package', rid=conMysql.select_user_chatroom('vip',bigarea_id=7))
        res = post_request_session(config.pt_pay_url, data, token_name='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.pt_testUid, money_type='money_cash_personal'), 480)
        case_list[des] = result

    def test_05_viAreaVipRoomPay(self, des='越南区区商业房礼物打赏主播70%分成场景'):
        """
        用例描述：
        验证余额足够时，越南区区商业房打赏非主播钻石礼物,打赏分成70%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏普通礼物（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.7 = 420
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_brokerUid)  # 账户余额清空
        data = encodePtData(payType='package', rid=conMysql.select_user_chatroom('business',bigarea_id=7),uid=config.pt_brokerUid)
        res = post_request_session(config.pt_pay_url, data, token_name='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_brokerUid, money_type='money_cash_b'), 420)
        case_list[des] = result

    def test_06_viAreaChatPay(self, des='越南区私聊打赏主播礼物打赏55分成场景'):
        """
        用例描述：
        验证余额足够时，越南区私聊打赏普通礼物,打赏非主播分成为0.5
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊内一对一打赏普通礼物（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.5 = 300
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_brokerUid)  # 账户余额清空
        data = encodePtData(payType='chat-gift',uid=config.pt_brokerUid)
        res = post_request_session(config.pt_pay_url, data, token_name='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_brokerUid, money_type='money_cash_b'), 300)
        case_list[des] = result

    def test_07_viAreaUnionRoomPay(self, des='越南区区联盟个人房礼物主播打赏70%分成场景'):
        """
        用例描述：
        验证余额足够时，越南区联盟房间1对1打赏礼物,打赏主播为：70%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.7 = 420
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_brokerUid)
        data = encodePtData(payType='package', rid=conMysql.select_user_chatroom('vip',bigarea_id=7),uid=config.pt_brokerUid)
        res = post_request_session(config.pt_pay_url, data, token_name='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_brokerUid, money_type='money_cash_b'), 420)
        case_list[des] = result
