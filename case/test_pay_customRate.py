from common.Config import config
from common.method import reason
from common.conMysql import conMysql
import unittest
from common.Request import post_request_session
from common.Assert import assert_body, assert_code, assert_equal
from common.basicData import encodeData
from common.Consts import case_list_b, result
from common.runFailed import Retry


@Retry(max_n=3)
class TestPayCreate(unittest.TestCase):

    customUid = 100500205
    pack_cal_uid = config.bb_user['pack_cal_uid']  # 打包结算签约主播
    ceoUid = config.live_role['pack_ceo']  # 公会长

    @classmethod
    def tearDownClass(cls) -> None:
        conMysql.checkBrokerUserRate(cls.pack_cal_uid, cls.ceoUid, rate=100)

    def test_01_roomPayCustomRate_50(self, des='商业房打赏自定义分成:50'):
        """
        用例描述：
        tdr:后台自定义分成比例为50%（所得公会魅力值部分-70%与公会长按照比例分成）
        脚本步骤：
        1.构造打赏者，被打赏者和公会长数据
        2.房间内打赏（打赏100分）
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：100 - 100 = 0
        5.检查被打赏者余额，预期为：100 * 0.62 * 0.5
        6.检查被打赏者公会长余额，预期为：100 * 0.62 *（1-0.5）
        """
        conMysql.updateMoneySql(config.payUid, money=30, money_cash=30, money_cash_b=30, money_b=10)
        conMysql.updateUserMoneyClearSql(self.customUid, self.ceoUid)
        conMysql.checkUserBroker(self.customUid, bid=self.ceoUid)  # bid=100500205 被打赏者加入工会
        conMysql.checkBrokerUserRate(self.customUid, self.ceoUid, rate=50)  # config.bbc_broker_user_rate 设置分成比
        data = encodeData(payType='package',
                          money=100,
                          uid=self.customUid,
                          giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('single_money', self.customUid,
                                                money_type='money_cash'), 100 * config.rate * 0.5)
        assert_equal(conMysql.selectUserInfoSql('single_money', self.ceoUid,
                                                money_type='money_cash'), 100 * config.rate * (1-0.5))
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
        5.检查被打赏者总余额，预期为：1000 * 0.42 * 0.8 + 1000 * 0.3 = 636
        6.检查被打赏者公会魅力值余额,预期为：1000 * 0.42 * 0.8 = 336（公会魅力值）
        7.检查被打赏者公会长余额，预期为：1000 * 0.42 *（1-0.8) = 84(公会魅力值)
        """
        conMysql.updateMoneySql(config.payUid, money=930, money_cash=30, money_cash_b=30, money_b=10)
        conMysql.updateUserMoneyClearSql(self.customUid, self.ceoUid)
        conMysql.checkUserBroker(self.customUid, bid=self.ceoUid)  # bid=105002314 被打赏者加入工会
        conMysql.checkBrokerUserRate(self.customUid, self.ceoUid, rate=80)  # config.bbc_broker_user_rate 设置分成比
        data = encodeData(payType='chat-gift', uid=self.customUid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('sum_money', self.customUid), 636)
        assert_equal(conMysql.selectUserInfoSql('single_money', self.customUid, money_type='money_cash'),
                     1000 * (config.rate - 0.2) * 0.8)
        assert_equal(conMysql.selectUserInfoSql('single_money', self.ceoUid, money_type='money_cash'),
                     1000 * (config.rate - 0.2) * 0.2)
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
        5.检查被打赏者总余额，到账预期为：52000*（0.7*0.25≈17%） - 52000*（0.08*0.25=2%）=8840-1040=7800
        6.检查被打赏者公会长余额，到账预期为：52000*（70%-17%=53%) - 52000*（0.08*0.75=6%）=27560-3120=24440
        """
        conMysql.updateMoneySql(config.payUid, money=52000)
        conMysql.updateUserMoneyClearSql(self.customUid, self.ceoUid)
        conMysql.checkUserBroker(self.customUid, bid=self.ceoUid)  # bid=105002314 被打赏者加入工会
        conMysql.checkBrokerUserRate(self.customUid, self.ceoUid, rate=25)  # config.bbc_broker_user_rate 设置分成比
        data = encodeData(payType='defend',
                          uid=self.customUid,
                          money=52000,
                          defend_id=2)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('single_money', self.customUid, money_type='money_cash'),
                     7800)
        assert_equal(conMysql.selectUserInfoSql('single_money', self.ceoUid, money_type='money_cash'),
                     24440)
        case_list_b[des] = result

    def test_04_liveRoomPayCustomRate_70(self, des='直播公会房间打赏自定义分成:70'):
        """
        用例描述：
        tdr:后台自定义分成比例为70%（所得公会魅力值部分*70%与公会长按照比例分成，公会长原分成不变）
        脚本步骤：
        1.构造打赏者，被打赏者和公会长数据
        2.房间内打赏流程
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：100 - 100 = 0
        5.检查被打赏者余额，预期为：100 * 0.6 * 0.7 =  42
        6.检查被打赏者公会长余额，预期为：100 * 0.21  + 100 * 0.6 * 0.3 = 39
        """
        conMysql.updateMoneySql(config.payUid, money=30, money_cash=30, money_cash_b=30, money_b=10)
        conMysql.updateUserMoneyClearSql(self.pack_cal_uid, self.ceoUid)
        conMysql.checkBrokerUserRate(self.pack_cal_uid, self.ceoUid, rate=70)
        data = encodeData(payType='package',
                          money=100,
                          rid=config.live_role['live_rid'],
                          uid=self.pack_cal_uid,
                          giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('single_money',
                                                self.pack_cal_uid,
                                                money_type='money_cash'), 100 * 0.6 * 0.7)
        assert_equal(conMysql.selectUserInfoSql('single_money',
                                                self.ceoUid,
                                                money_type='money_cash'), 39)
        case_list_b[des] = result

    def test_05_liveChatPayCustomRate_0(self, des='直播公会私聊打赏自定义分成:0'):
        """
        用例描述：
        tdr:后台自定义分成比例为0%（所得公会魅力值部分*0%与公会长按照比例分成，公会长原分成不变）
        脚本步骤：
        1.构造打赏者，被打赏者和公会长数据
        2.房间内打赏流程
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：1000 - 1000 = 0
        5.检查被打赏者余额，预期为：1000 * 0.6 * 0 =  0
        6.检查被打赏者公会长余额，预期为：1000 * 0.2  + 1000 * 0.6 * 1 = 800
        """
        conMysql.updateMoneySql(config.payUid, money=30, money_cash=3000, money_cash_b=70)
        conMysql.updateUserMoneyClearSql(self.pack_cal_uid, self.ceoUid)
        conMysql.checkBrokerUserRate(self.pack_cal_uid, self.ceoUid, rate=0)
        data = encodeData(payType='chat-gift',
                          uid=self.pack_cal_uid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 2100)
        assert_equal(conMysql.selectUserInfoSql('single_money',
                                                self.pack_cal_uid,
                                                money_type='money_cash'), 0)
        assert_equal(conMysql.selectUserInfoSql('sum_money',
                                                self.pack_cal_uid), 0)
        assert_equal(conMysql.selectUserInfoSql('single_money',
                                                self.ceoUid,
                                                money_type='money_cash'), 800)
        case_list_b[des] = result
