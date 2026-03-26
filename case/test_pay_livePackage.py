from common.Config import config
from common.method import reason
from common.conMysql import conMysql as mysql
import unittest
from common.Request import post_request_session
from common.Assert import assert_body, assert_code, assert_equal, assert_len
from common.basicData import encodeData
from common.Consts import case_list_b, result
from common.runFailed import Retry


@Retry(max_n=3)
class TestPayLivePackage(unittest.TestCase):
    """直播打包结算支付测试类"""
    
    live_role = config.live_role.copy()
    # 商业房房主 or (（工会会长 or 工会成员）&& 同意大神协议 )
    # (insert into xs_user_settings (uid, agreement_version) values(100500205, 1))

    def _prepare_broker_data(self, test_uid, ceo_uid, pay_money, extra_steps=None):
        """准备公会打包结算测试数据"""
        mysql.updateUserInfoSql('chatroom', test_uid)  # 商业房房主
        mysql.updateUserInfoSql('broker_user', test_uid, ceo_uid)  # 打包结算
        mysql.checkUserXsBroker(ceo_uid)  # 公会长
        UserMoneyOperations.update(config.payUid, money=pay_money)
        mysql.updateUserMoneyClearSql(test_uid, ceo_uid)
        if extra_steps:
            for step in extra_steps:
                step()

    def _validate_db_state(self, checks):
        """验证数据库状态"""
        for check in checks:
            field, uid, expected = check['field'], check['uid'], check['expected']
            kwargs = check.get('kwargs', {})
            assert_func = check.get('assert_func', assert_equal)
            assert_func(mysql.selectUserInfoSql(field, uid, **kwargs), expected)

    def test_01_liveRoomPayGift_602119(self):
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
        des = '直播间内礼物打赏主播-公会长分成60:21'
        test_uid, ceo_uid = self.live_role['pack_cal_uid'], self.live_role['pack_ceo']
        
        self._prepare_broker_data(test_uid, ceo_uid, pay_money=1000)
        
        data = encodeData(rid=self.live_role['live_rid'], uid=test_uid)
        res = post_request_session(config.pay_url, data)
        
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        self._validate_db_state([
            {'field': 'single_money', 'uid': test_uid, 'expected': 600, 'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': ceo_uid, 'expected': 210, 'kwargs': {'money_type': 'money_cash'}},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ])
        case_list_b[des] = result

    def test_02_liveRoomPayBox_602119(self):
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
        des = '直播间内箱子打赏主播-公会长分成60:21'
        test_uid, ceo_uid = self.live_role['pack_cal_uid'], self.live_role['pack_ceo']
        
        self._prepare_broker_data(test_uid, ceo_uid, pay_money=700)
        
        data = encodeData(money=600, rid=self.live_role['live_rid'], 
                          giftId=config.giftId['46'], uid=test_uid, star=1)
        res = post_request_session(config.pay_url, data)
        
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        self._validate_db_state([
            {'field': 'single_money', 'uid': test_uid, 'expected': 300 * 0.6, 'kwargs': {'money_type': 'money_cash'}, 'assert_func': assert_len},
            {'field': 'single_money', 'uid': ceo_uid, 'expected': 300 * 0.21, 'kwargs': {'money_type': 'money_cash'}, 'assert_func': assert_len},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 100}
        ])
        case_list_b[des] = result

    def test_03_knightDefendPayChangeMoney(self):
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
        des = '开通房间守护团给GS收60%（公会）'
        test_uid, ceo_uid = self.live_role['pack_cal_uid'], self.live_role['pack_ceo']
        
        self._prepare_broker_data(test_uid, ceo_uid, pay_money=100000)
        
        data = encodeData(payType='package-knightDefend', money=99900,
                          uid=test_uid, rid=self.live_role['live_rid'])
        res = post_request_session(config.pay_url, data)
        
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        self._validate_db_state([
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 100},
            {'field': 'single_money', 'uid': test_uid, 'expected': 59940, 'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': ceo_uid, 'expected': 20979, 'kwargs': {'money_type': 'money_cash'}}
        ])
        case_list_b[des] = result

    def test_04_chatPayGift_602020(self):
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
        des = '私聊打赏主播-公会长分成60:20'
        test_uid, ceo_uid = self.live_role['pack_cal_uid'], self.live_role['pack_ceo']
        
        self._prepare_broker_data(test_uid, ceo_uid, pay_money=1000)
        
        data = encodeData(payType='chat-gift', uid=test_uid)
        res = post_request_session(config.pay_url, data)
        
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        self._validate_db_state([
            {'field': 'single_money', 'uid': test_uid, 'expected': 600, 'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': ceo_uid, 'expected': 200, 'kwargs': {'money_type': 'money_cash'}},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ])
        case_list_b[des] = result

    def test_05_chatPayBox_602020(self):
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
        des = '私聊打赏箱子主播-公会长分成60:20'
        test_uid, ceo_uid = self.live_role['pack_cal_uid'], self.live_role['pack_ceo']
        
        self._prepare_broker_data(test_uid, ceo_uid, pay_money=1000)
        
        data = encodeData(payType='chat-gift', money=600, uid=test_uid,
                          giftId=config.giftId['46'], star=1)
        res = post_request_session(config.pay_url, data)
        
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        self._validate_db_state([
            {'field': 'single_money', 'uid': test_uid, 'expected': 300 * 0.6, 'kwargs': {'money_type': 'money_cash'}, 'assert_func': assert_len},
            {'field': 'single_money', 'uid': ceo_uid, 'expected': 300 * 0.20, 'kwargs': {'money_type': 'money_cash'}, 'assert_func': assert_len},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 400}
        ])
        case_list_b[des] = result

    def test_06_liveRoomPayGift_602119(self):
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
        des = '直播公会主播(非宗师)-公会长打赏分成60:21'
        test_uid, ceo_uid = self.live_role['pack_cal_uid'], self.live_role['pack_ceo']
        
        self._prepare_broker_data(test_uid, ceo_uid, pay_money=1000, 
                                  extra_steps=[lambda: mysql.checkUserXsMentorLevel(test_uid, level=1)])
        
        data = encodeData(rid=self.live_role['live_rid'], uid=test_uid)
        res = post_request_session(config.pay_url, data)
        
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        self._validate_db_state([
            {'field': 'single_money', 'uid': test_uid, 'expected': 600, 'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': ceo_uid, 'expected': 210, 'kwargs': {'money_type': 'money_cash'}},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ])
        case_list_b[des] = result

    def test_07_liveRoomUnderRolePay_6238(self):
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
        des = '直播间打赏麦下用户分成62:38'
        
        UserMoneyOperations.update(config.payUid, money=100)
        UserMoneyOperations.update(config.rewardUid)
        
        data = encodeData(giftId=config.giftId['5'], rid=self.live_role['live_rid'], money=100)
        res = post_request_session(config.pay_url, data)
        
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        self._validate_db_state([
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 62, 'kwargs': {'money_type': 'money_cash_b'}},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ])
        case_list_b[des] = result

    def test_08_NotLiveRoomPayAnchor(self):
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
        des = '主播在非直播间被打赏70%进个人魅力'
        test_uid = self.live_role['pack_cal_uid']
        
        UserMoneyOperations.update(config.payUid, money=1000)
        UserMoneyOperations.update(test_uid)
        
        data = encodeData(uid=test_uid)
        res = post_request_session(config.pay_url, data)
        
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        self._validate_db_state([
            {'field': 'single_money', 'uid': test_uid, 'expected': 700},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ])
        case_list_b[des] = result
