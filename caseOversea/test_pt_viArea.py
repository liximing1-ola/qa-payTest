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
    越南区消费差异化验证：
    1.商业房内打赏分成比例70%（普通礼物打赏）
    2.商业房内打赏分成开出物品价值的比例70%（开箱子盲盒打赏）
    3.1v1私聊打赏分成比例80%（普通礼物打赏分成）
    4.越南区联盟房打赏分成30%
    """

    @classmethod
    def setUpClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()), bigarea_id=7)
        conMysql.updateUserRidInfoSql('business', config.pt_room['business_joy_vi'], area='vn')

    @classmethod
    def tearDownClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()))

    def test_01_viAreaVipRoomPay(self, des='越南区区商业房礼物打赏37分成场景'):
        """
        用例描述：
        验证余额足够时，越南区区商业房打赏普通礼物,打赏分成满足师徒收益(一代宗师)的基础上为3:7
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏普通礼物（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.7 = 420
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_testUid)  # 账户余额清空
        data = encodePtData(payType='package', rid=config.pt_room['business_joy_vi'])
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_testUid, money_type='money_cash'), 420)
        case_list[des] = result

    def test_02_viAreaVipRoomGiveBox(self, des='越南区区商业房箱子打赏37分成场景'):
        """
        用例描述：
        验证余额足够时，越南区商业房1对1打赏箱子,打赏分成满足师徒收益(一代宗师)的基础上为3:7
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
        2.giveBox
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：700 - 600 = 100
        5.检查收箱用户账户余额，得到箱子/盲盒开出物品价值的70%，预期money值为：不小于210。开铜箱子最小为30钻。
        """
        conMysql.updateMoneySql(config.pt_payUid, money=400, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(config.pt_testUid)
        data = encodePtData(payType='package',
                            giftId=config.giftId['46'],
                            rid=config.pt_room['business_joy_vi'])
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_len(conMysql.selectUserInfoSql('single_money', config.pt_testUid, money_type='money_cash_b'), 210)
        assert_equal(conMysql.selectUserInfoSql('single_money',
                                                config.pt_testUid,
                                                money_type='money_cash_b'),
                     conMysql.selectUserInfoSql(accountType='pay_change', uid=config.pt_testUid))
        case_list[des] = result

    # 白名单打赏0.8分成，非白名单0.5分成
    def test_03_viAreaChatPay(self, des='越南区非白名单私聊礼物打赏55分成场景'):
        """
        用例描述：
        验证余额足够时，越南区私聊打赏普通礼物,打赏分成满足师徒收益(一代宗师)的基础上为0.5
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊内一对一打赏普通礼物（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.5 = 300
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_testUid)  # 账户余额清空
        data = encodePtData(payType='chat-gift')
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_testUid, money_type='money_cash'), 300)
        case_list[des] = result

    def test_04_viAreaUnionRoomPay(self, des='越南区区联盟房礼物打赏30%分成场景'):
        """
        用例描述：
        验证余额足够时，越南区联盟房间1对1打赏礼物,打赏分成满足师徒收益(一代宗师)的基础上为：30%
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.3 = 180
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_testUid)
        data = encodePtData(payType='package', rid=config.pt_room['union_vi'])
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_testUid, money_type='money_cash'), 180)
        case_list[des] = result
