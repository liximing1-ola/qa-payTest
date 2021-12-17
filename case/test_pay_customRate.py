from common.Config import config
from common.method import reason
from common.conMysql import conMysql
import unittest
from common.Request import post_request_session
from common.Assert import assert_body, assert_code, assert_equal
from common import basicData
from common.Consts import case_list_b, result
from common.runFailed import Retry
@Retry
class TestPayCreate(unittest.TestCase):

    rate_role = {
        'rewardUid2': 100500205,  # 公会成员
        'pack_ceo': 105002314,  # 公会长
    }

    def test_01_RoomPayCustomRate_(self, des='商业房打赏自定义分成:50'):
        """
        用例描述：
        tdr:后台自定义分成比例为50%（所得公会魅力值部分与公会长按照比例分成）
        脚本步骤：
        1.构造打赏者，被打赏者和公会长数据
        2.房间内打赏（打赏100分）
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：100 - 100 = 0
        5.检查被打赏者余额，预期为：100 * 0.7 * 0.5 = 35
        6.检查被打赏者公会长余额，预期为：100 * 0.7 * 0.5 = 35
        """
        conMysql.updateMoneySql(config.payUid, money=30, money_cash=30, money_cash_b=30, money_b=10)
        testUid = config.rewardUid2  # 被打赏者
        ceoUid = config.live_role['pack_ceo']  # 公会长
        conMysql.updateUserMoneyClearSql(testUid, ceoUid)
        conMysql.checkUserBroker(testUid, bid=ceoUid)  # bid=105002314 被打赏者加入工会
        conMysql.checkBrokerUserRate(testUid, ceoUid, rate=50)  # config.bbc_broker_user_rate 设置分成比
        data = basicData.encodeData(payType='package', money=100, rid=config.live_role['auto_rid'], uid=testUid,
                                    giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 0)
        assert_equal(conMysql.selectUserMoneySql('single_money', testUid, money_type='money_cash'), 35)
        assert_equal(conMysql.selectUserMoneySql('single_money', ceoUid, money_type='money_cash'), 35)
        case_list_b[des] = result