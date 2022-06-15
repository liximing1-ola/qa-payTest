from common.Config import config
from common.method import reason
from common.conPtMysql import conMysql
from common.Request import post_request_session
import unittest
from common.Assert import assert_code, assert_body, assert_equal
from common.basicData import encodePtData
from common.Consts import case_list, result
from common.runFailed import Retry
@Retry
class TestPayCreate(unittest.TestCase):

    def test_01_RoomPayNoMoney(self, des='房间打赏但余额不足的场景'):
        """
        用例描述：
        验证余额不足时，房间一对一打赏
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏流程
        3.校验接口状态和返回值数据
        4.检查预期返回msg，预期：支付失败
        5.检查被打赏者余额,预期：0
        """
        conMysql.updateUserMoneyClearSql(config.pt_payUid, config.pt_testUid)
        data = encodePtData(payType='package')
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, reason(des, res))
        assert_body(res['body'], 'msg', '餘額不足，無法支付', reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_testUid), 0)
        case_list[des] = result

    def test_02_RoomPayChangeMoney(self, des='商业房1V1打赏场景'):
        """
        用例描述：
        验证余额足够时，非直播类型房间一对一打赏,打赏分成满足师徒收益(一代宗师)的基础上为：70:30
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：600 * 0.7 = 420
        """
        conMysql.updateMoneySql(config.pt_payUid, 700)
        data = encodePtData(payType='package')
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserMoneySql('single_money', config.pt_testUid, money_type='money_cash'), 420)
        case_list[des] = result