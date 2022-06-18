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
        conMysql.updateUserInfoSql('union', config.pt_room['th_union'])

    @classmethod
    def tearDownClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()))
        time.sleep(0.6)
        conRedis.delKey('User.Big.Area.Id', config.pt_user.values())
        conRedis.delKey('User.Big.Area', config.pt_user.values())

    def test_01_thaiUnionRoomPay(self, des='泰区联盟房礼物打赏场景'):
        """
        用例描述：
        验证余额足够时，泰语区联盟房间1对1打赏礼物,打赏分成满足师徒收益(一代宗师)的基础上为：30:70
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.3 = 180
        5.检查打赏者余额，预期为： 700 - 600 = 100
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        conMysql.updateMoneySql(config.pt_testUid)
        data = encodePtData(payType='package', rid=config.pt_room['th_union'])
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_testUid, money_type='money_cash'), 180)
        case_list[des] = result

    def test_02_thaiUnionRoomGiveBox(self, des='泰区联盟房送箱子场景'):
        """
        用例描述：
        验证余额足够时，泰语区联盟房间1对1打赏箱子,打赏分成满足师徒收益(一代宗师)的基础上为：30:70
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
        2.giveBox
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：700 - 600 = 100
        5.检查收箱用户账户余额，预期值为：大于90
        """
        conMysql.updateMoneySql(config.pt_payUid, money=400, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(config.pt_testUid)
        data = encodePtData(payType='package', uid=config.pt_testUid, giftId=config.giftId['46'],
                            rid=config.pt_room['th_union'])
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_len(conMysql.selectUserInfoSql('single_money', config.pt_testUid, money_type='money_cash_b'), 90)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_testUid, money_type='money_cash_b'),
                     conMysql.selectUserInfoSql(accountType='pay_change', uid=config.pt_testUid))
        case_list[des] = result