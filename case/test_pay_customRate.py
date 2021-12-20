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

    def test_01_roomPayCustomRate_50(self, des='商业房打赏自定义分成:50'):
        """
        用例描述：
        tdr:后台自定义分成比例为50%（所得公会魅力值部分-70%与公会长按照比例分成）
        脚本步骤：
        1.构造打赏者，被打赏者和公会长数据
        2.房间内打赏（打赏100分）
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：100 - 100 = 0
        5.检查被打赏者余额，预期为：100 * 0.7 * 0.5 = 35
        6.检查被打赏者公会长余额，预期为：100 * 0.7 *（1-0.5） = 35
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

    def test_02_chatPayCustomRate_80(self, des='私聊打赏自定义分成:80'):
        """
        用例描述：
        tdr:后台自定义分成比例为80%（所得公会魅力值部分-50%与公会长按照比例分成）
        脚本步骤：
        1.构造打赏者，被打赏者和公会长数据
        2.私聊打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：1000 - 1000 = 0
        5.检查被打赏者总余额，预期为：1000 * 0.5 * 0.8 + 1000 * 0.3 = 700
        6.检查被打赏者公会魅力值余额,预期为：1000 * 0.5 * 0.8 = 400（公会魅力值）
        7.检查被打赏者公会长余额，预期为：1000 * 0.5 *（1-0.8) = 100(公会魅力值)
        """
        conMysql.updateMoneySql(config.payUid, money=930, money_cash=30, money_cash_b=30, money_b=10)
        testUid = config.rewardUid2  # 被打赏者
        ceoUid = config.live_role['pack_ceo']  # 关联公会长
        conMysql.updateUserMoneyClearSql(testUid, ceoUid)
        conMysql.checkUserBroker(testUid, bid=ceoUid)  # bid=105002314 被打赏者加入工会
        conMysql.checkBrokerUserRate(testUid, ceoUid, rate=80)  # config.bbc_broker_user_rate 设置分成比
        data = basicData.encodeData(payType='chat-gift', uid=testUid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 0)
        assert_equal(conMysql.selectUserMoneySql('sum_money', testUid), 700)
        assert_equal(conMysql.selectUserMoneySql('single_money', testUid, money_type='money_cash'), 400)
        assert_equal(conMysql.selectUserMoneySql('single_money', ceoUid, money_type='money_cash'), 100)
        case_list_b[des] = result

    def test_03_defendPayCustomRate_25(self, des='个人守护打赏自定义分成:25'):
        """
        用例描述：
        tdr:后台自定义分成比例为25%（所得公会魅力值部分-70%与公会长按照比例分成）
        脚本步骤：
        1.构造打赏者，被打赏者和公会长数据
        2.开通守护
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：52000 - 52000 = 0
        5.检查被打赏者总余额，预期为：52000 * 0.7 * 0.25 = 9100
        6.检查被打赏者公会长余额，预期为：52000 * 0.7 *（1-0.25) = 27300
        """
        conMysql.updateMoneySql(config.payUid, money=52000)
        testUid = config.rewardUid2  # 被打赏者
        ceoUid = config.live_role['pack_ceo']  # 关联公会长
        conMysql.updateUserMoneyClearSql(testUid, ceoUid)
        conMysql.checkUserBroker(testUid, bid=ceoUid)  # bid=105002314 被打赏者加入工会
        conMysql.checkBrokerUserRate(testUid, ceoUid, rate=25)  # config.bbc_broker_user_rate 设置分成比
        data = basicData.encodeData(payType='defend', uid=testUid, money=52000)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 0)
        assert_equal(conMysql.selectUserMoneySql('single_money', testUid, money_type='money_cash'), 9100)
        assert_equal(conMysql.selectUserMoneySql('single_money', ceoUid, money_type='money_cash'), 27300)
        case_list_b[des] = result

    @unittest.skip('未完成')
    def test_04_fleetRoomPayCustomRate_100(self, des='本家族房打赏自定义分成:100'):
        """
        用例描述：
        tdr:后台自定义分成比例为25%（所得公会魅力值部分-70%与公会长按照比例分成）
        脚本步骤：
        1.构造打赏者，被打赏者和公会长数据
        2.开通守护
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：52000 - 52000 = 0
        5.检查被打赏者总余额，预期为：52000 * 0.7 * 0.25 = 9100
        6.检查被打赏者公会长余额，预期为：52000 * 0.7 *（1-0.25) = 27300
        """
        conMysql.updateMoneySql(config.payUid, money=52000)
        testUid = config.rewardUid2  # 被打赏者
        ceoUid = config.live_role['pack_ceo']  # 关联公会长
        conMysql.updateUserMoneyClearSql(testUid, ceoUid)
        conMysql.checkUserBroker(testUid, bid=ceoUid)  # bid=105002314 被打赏者加入工会
        conMysql.checkBrokerUserRate(testUid, ceoUid, rate=25)  # config.bbc_broker_user_rate 设置分成比
        data = basicData.encodeData(payType='defend', uid=testUid, money=52000)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 0)
        assert_equal(conMysql.selectUserMoneySql('single_money', testUid, money_type='money_cash'), 9100)
        assert_equal(conMysql.selectUserMoneySql('single_money', ceoUid, money_type='money_cash'), 27300)
        case_list_b[des] = result

    @unittest.skip('未完成')
    def test_05_unFleetRomePayCustomRate_0(self, des='非本家族房打赏自定义分成:0'):
        """
        用例描述：
        tdr:后台自定义分成比例为25%（所得公会魅力值部分-70%与公会长按照比例分成）
        脚本步骤：
        1.构造打赏者，被打赏者和公会长数据
        2.开通守护
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：52000 - 52000 = 0
        5.检查被打赏者总余额，预期为：52000 * 0.7 * 0.25 = 9100
        6.检查被打赏者公会长余额，预期为：52000 * 0.7 *（1-0.25) = 27300
        """
        conMysql.updateMoneySql(config.payUid, money=52000)
        testUid = config.rewardUid2  # 被打赏者
        ceoUid = config.live_role['pack_ceo']  # 关联公会长
        conMysql.updateUserMoneyClearSql(testUid, ceoUid)
        conMysql.checkUserBroker(testUid, bid=ceoUid)  # bid=105002314 被打赏者加入工会
        conMysql.checkBrokerUserRate(testUid, ceoUid, rate=25)  # config.bbc_broker_user_rate 设置分成比
        data = basicData.encodeData(payType='defend', uid=testUid, money=52000)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 0)
        assert_equal(conMysql.selectUserMoneySql('single_money', testUid, money_type='money_cash'), 9100)
        assert_equal(conMysql.selectUserMoneySql('single_money', ceoUid, money_type='money_cash'), 27300)
        case_list_b[des] = result