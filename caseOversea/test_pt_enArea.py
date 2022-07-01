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
    英语区消费差异化验证：
    1.英语区私聊分成比例50%（礼物打赏，箱子打赏）
    2.英语区家族房分成50%（礼物打赏，箱子打赏）
    """
    @classmethod
    def setUpClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()), bigarea_id=1)
        conMysql.updateUserInfoSql('fleet', config.pt_room['en_fleet'])

    @classmethod
    def tearDownClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()))

    def test_01_enAreaIMPayGift(self, des='英语区私聊打赏礼物55分成场景'):
        """
        用例描述：
        检查账户余额充足时，英语区私聊打赏礼物分成为1：0.5
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊一对一打赏流程
        3.校验接口和返回值数据
        4.检查打赏者数据，预期：600 - 600 = 0
        5.检查被打赏者余额,预期：600 * 0.5 = 300
        """
        conMysql.updateMoneySql(config.pt_payUid, money=600)
        conMysql.updateMoneySql(config.pt_testUid)
        data = encodePtData(payType='chat-gift')
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_testUid, money_type='money_cash'), 300)
        case_list[des] = result

    def test_02_enAreaIMPayGiveBox(self, des='英语区私聊打赏箱子55分成场景'):
        """
        用例描述：
        检查账户余额充足时，英语区私聊打赏箱子分成为1：0.5
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊一对一打赏流程
        3.校验接口和返回值数据
        4.检查打赏者数据，预期：700 - 600 = 0
        5.检查被打赏者余额,预期为：不小于150
        """
        conMysql.updateMoneySql(config.pt_payUid, money=300, money_cash=100, money_b=100, money_cash_b=100)
        conMysql.updateMoneySql(config.pt_testUid)
        data = encodePtData(payType='chat-gift', giftId=config.giftId['46'])
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 0)
        assert_len(conMysql.selectUserInfoSql('sum_money', config.pt_testUid), 150)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_testUid, money_type='money_cash_b'),
                     conMysql.selectUserInfoSql(accountType='pay_change', uid=config.pt_testUid))
        case_list[des] = result

    def test_03_enAreaFleetRoomPay(self, des='英语区家族房礼物打赏55分成场景'):
        """
        用例描述：
        验证余额足够时，英语区家族房1对1打赏礼物,打赏分成满足师徒收益(一代宗师)的基础上为1:0.5
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.5 = 300
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_testUid)
        data = encodePtData(payType='package', rid=config.pt_room['en_fleet'])
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_testUid, money_type='money_cash'), 300)
        case_list[des] = result

    def test_04_enAreaFleetRoomGiveBox(self, des='英语区家族房送箱子55分成场景'):
        """
        用例描述：
        验证余额足够时，英语区家族房1对1打赏箱子,打赏分成满足师徒收益(一代宗师)的基础上为1:0.5
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
        2.giveBox
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：700 - 600 = 100
        5.检查收箱用户账户余额，预期值为：不小于150
        """
        conMysql.updateMoneySql(config.pt_payUid, money=400, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(config.pt_testUid)
        data = encodePtData(payType='package', giftId=config.giftId['46'], rid=config.pt_room['en_fleet'])
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_len(conMysql.selectUserInfoSql('single_money', config.pt_testUid, money_type='money_cash_b'), 150)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_testUid, money_type='money_cash_b'),
                     conMysql.selectUserInfoSql(accountType='pay_change', uid=config.pt_testUid))
        case_list[des] = result