from common.Config import config
from common.method import reason
from common.conMysql import conMysql
import unittest
from common.Request import post_request_session
from common.Assert import assert_body, assert_code, assert_equal, assert_len
from common.basicData import encodeData
from common.Consts import case_list_b, result
from common.runFailed import Retry


@Retry
class TestPayCreate(unittest.TestCase):

    live_role = {
        'pack_ceo': 105002314,  # 直播公会公会长
        'pack_cal_uid': 105002313,  # 公会签约主播（打包结算），宗师等级可设置为一代和非一代
        'live_rid': 193185577,  # 直播间，房主:105002313
    }

    # 商业房房主 or (（工会会长 or 工会成员）&& 同意大神协议 )
    # (insert into xs_user_settings (uid, agreement_version) values(100500205, 1))

    def test_01_liveRoomPayGift_602119(self, des='直播间内礼物打赏主播-公会长分成60:21'):
        """
        用例描述：
        tdr:直播间内工会一代宗师主播-公会长-平台分成比为：60:21:19（打包结算频道是直播）
        验证直播间打赏一代宗师主播（打包结算主播pack_cal=1），打赏分成满足：60:21:19，且收入在money_cash账户
        脚本步骤：
        1.构造打赏者和主播数据
        2.房间内一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为：1000 * 0.6 = 600(money_cash)
        5.检查公会长余额，预期为：1000 * 0.21 = 210
        6.检查打赏者余额.预期为：1000 - 1000 = 0
        """
        test_uid = self.live_role['pack_cal_uid']
        ceo_uid = self.live_role['pack_ceo']
        conMysql.updateUserInfoSql('chatroom', test_uid)  # 商业房房主
        conMysql.updateUserInfoSql('broker_user', test_uid, ceo_uid)  # 打包结算
        conMysql.checkUserXsBroker(ceo_uid)  # 公会长
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateUserMoneyClearSql(test_uid, ceo_uid)
        data = encodeData(payType='package',
                          rid=self.live_role['live_rid'],
                          uid=test_uid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', test_uid, money_type='money_cash'), 600)
        assert_equal(conMysql.selectUserInfoSql('single_money', ceo_uid, money_type='money_cash'), 210)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    def test_02_liveRoomPayBox_602119(self, des='直播间内箱子打赏主播-公会长分成60:21'):
        """
        用例描述：
        tdr:直播间内工会一代宗师主播-公会长-平台分成比为：60:21:19（打包结算频道是直播）
        验证直播间打赏一代宗师主播（打包结算主播pack_cal=1），打赏分成满足：60:21:19，且收入在money_cash账户
        脚本步骤：
        1.构造打赏者和主播数据
        2.房间内一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为不小于：300 * 0.6 = 180(money_cash)
        5.检查公会长余额，预期为不小于： 300 * 0.21 = 62
        6.检查打赏者余额.预期为：700 - 600 = 100
        """
        test_uid = self.live_role['pack_cal_uid']
        ceo_uid = self.live_role['pack_ceo']
        conMysql.updateUserInfoSql('chatroom', test_uid)
        conMysql.updateUserInfoSql('broker_user', test_uid, ceo_uid)
        conMysql.checkUserXsBroker(ceo_uid)
        conMysql.updateMoneySql(config.payUid, money=700)
        conMysql.updateUserMoneyClearSql(test_uid, ceo_uid)
        data = encodeData(payType='package',
                          money=600,
                          rid=self.live_role['live_rid'],
                          giftId=config.giftId['46'],
                          uid=test_uid,
                          star=4)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_len(conMysql.selectUserInfoSql('single_money', test_uid, money_type='money_cash'), 300 * 0.6)
        assert_len(conMysql.selectUserInfoSql('single_money', ceo_uid, money_type='money_cash'), 300 * 0.21)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 100)
        case_list_b[des] = result

    def test_03_knightDefendPayChangeMoney(self, des='开通房间守护团给GS收60%（公会）'):
        """
         用例描述：
         开通直播间守护团，收益分成主播-公会长-平台分成比为：60:21:19（打包结算频道是直播）
         脚本步骤：
         1.构造开通者和被守护者数据
         2.开通真爱守护
         3.校验接口状态和返回值数据
         4.检查打赏者余额，预期：100000 - 99900 = 100
         5.检查公会长余额，预期为： 99900 * 0.21 = 20979
         6.检查被打赏者余额.预期为：99900 * 0.6 = 59940
         """
        test_uid = self.live_role['pack_cal_uid']
        ceo_uid = self.live_role['pack_ceo']
        conMysql.updateUserInfoSql('chatroom', test_uid)  # 商业房房主
        conMysql.updateUserInfoSql('broker_user', test_uid, ceo_uid)  # 打包结算
        conMysql.checkUserXsBroker(ceo_uid)  # 公会长
        conMysql.updateMoneySql(config.payUid, money=100000)
        conMysql.updateUserMoneyClearSql(test_uid, ceo_uid)
        data = encodeData(payType='package-knightDefend',
                          money=99900,
                          uid=test_uid,
                          rid=self.live_role['live_rid'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('single_money', test_uid, money_type='money_cash'), 59940)
        assert_equal(conMysql.selectUserInfoSql('single_money', ceo_uid, money_type='money_cash'), 20979)
        case_list_b[des] = result

    def test_04_chatPayGift_602020(self, des='私聊打赏主播-公会长分成60:20'):
        """
        用例描述：
        tdr:私聊打赏公会一代宗师主播-公会长-官方抽成：60:20:20
        脚本步骤：
        1.构造打赏者和主播数据
        2.私聊打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为：1000 * 0.6 = 600(money_cash)
        5.检查公会长余额，预期为：1000 * 0.2 = 200
        6.检查打赏者余额.预期为：1000 - 1000 = 0
        """
        test_uid = self.live_role['pack_cal_uid']
        ceo_uid = self.live_role['pack_ceo']
        conMysql.updateUserInfoSql('chatroom', test_uid)  # 商业房房主
        conMysql.updateUserInfoSql('broker_user', test_uid, ceo_uid)  # 打包结算
        conMysql.checkUserXsBroker(ceo_uid)  # 工会公会长
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateUserMoneyClearSql(test_uid, ceo_uid)
        data = encodeData(payType='chat-gift', uid=test_uid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', test_uid, money_type='money_cash'), 600)
        assert_equal(conMysql.selectUserInfoSql('single_money', ceo_uid, money_type='money_cash'), 200)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    def test_05_chatPayBox_602020(self, des='私聊打赏箱子主播-公会长分成60:20'):
        """
        用例描述：
        tdr:私聊打赏箱子公会主播-公会长-官方抽成：60:20:20
        脚本步骤：
        1.构造打赏者和主播数据
        2.私聊打赏铜箱子（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为不小于：300 * 0.6 = 180(money_cash)
        5.检查公会长余额，预期为不小于：300 * 0.2 = 60
        6.检查打赏者余额.预期为不小于：1000 - 600 = 400
        """
        test_uid = self.live_role['pack_cal_uid']
        ceo_uid = self.live_role['pack_ceo']
        conMysql.updateUserInfoSql('chatroom', test_uid)  # 商业房房主
        conMysql.updateUserInfoSql('broker_user', test_uid, ceo_uid)  # 打包结算
        conMysql.checkUserXsBroker(ceo_uid)  # 工会公会长
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateUserMoneyClearSql(test_uid, ceo_uid)
        data = encodeData(payType='chat-gift',
                          money=600,
                          uid=test_uid,
                          giftId=config.giftId['46'],
                          star=4)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_len(conMysql.selectUserInfoSql('single_money', test_uid, money_type='money_cash'), 300 * 0.6)
        assert_len(conMysql.selectUserInfoSql('single_money', ceo_uid, money_type='money_cash'), 300 * 0.20)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 400)
        case_list_b[des] = result

    def test_06_liveRoomPayGift_602119(self, des='直播公会主播(非宗师)-公会长打赏分成60:21'):
        """
        用例描述：
        tdr:直播间内工会非一代宗师主播-公会长-官方：60:21:19
        脚本步骤：
        1.构造打赏者和主播数据
        2.房间内一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为：1000 * 0.6 = 600（money_cash）
        5.检查公会长余额，预期为：1000 * 0.21 = 210
        6.检查打赏者余额.预期为：1000 - 1000 = 0
        """
        test_uid = self.live_role['pack_cal_uid']
        ceo_uid = self.live_role['pack_ceo']
        conMysql.updateUserInfoSql('chatroom', test_uid)  # 商业房房主
        conMysql.updateUserInfoSql('broker_user', test_uid, ceo_uid)  # 打包结算
        conMysql.checkUserXsBroker(ceo_uid)  # 工会公会长
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateUserMoneyClearSql(test_uid, ceo_uid)
        conMysql.checkUserXsMentorLevel(test_uid, level=1)  # 师父等级改为非一代宗师
        data = encodeData(payType='package',
                          rid=self.live_role['live_rid'],
                          uid=test_uid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', test_uid, money_type='money_cash'), 600)
        assert_equal(conMysql.selectUserInfoSql('single_money', ceo_uid, money_type='money_cash'), 210)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    def test_07_liveRoomUnderRolePay_6238(self, des='直播间打赏麦下用户分成62:38'):
        """
        用例描述：
        验证直播间内打赏麦下用户，在师徒收益基础上，分成比例应为62:38
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为：100 * 0.62 = 62
        5.检查打赏者余额,预期为：100 - 100 = 0
        """
        conMysql.updateMoneySql(config.payUid, money=100)
        conMysql.updateMoneySql(config.rewardUid)
        data = encodeData(payType='package',
                          giftId=config.giftId['5'],
                          rid=self.live_role['live_rid'],
                          money=100)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.rewardUid, money_type='money_cash_b'), 62)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    def test_08_NotLiveRoomPayAnchor(self, des='主播在非直播间被打赏70%进个人魅力'):
        """
        用例描述：
        tdr:非直播频道主播被打赏金额70进个人魅力值（money_cash_b）
        脚本步骤：
        1.构造打赏者和主播数据
        2.非直播房间内一对一打赏（打赏1000分）
        3.校验接口状态和返回值数值
        4.检查被打赏者余额和账户，预期为：1000 * 0.7 = 700(money_cash_b)
        6.检查打赏者余额.预期为：1000 - 1000 = 0
        """
        test_uid = self.live_role['pack_cal_uid']
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateMoneySql(test_uid)
        data = encodeData(payType='package', uid=test_uid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', test_uid), 700)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result
