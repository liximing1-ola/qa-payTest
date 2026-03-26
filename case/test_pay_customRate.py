from common.Config import config
from common.method import reason
from common.conMysql import conMysql as mysql
import unittest
from common.Request import post_request_session
from common.Assert import assert_body, assert_code, assert_equal
from common.basicData import encodeData
from common.Consts import case_list_b, result
from common.runFailed import Retry


@Retry(max_n=3)
class TestPayCustomRate(unittest.TestCase):
    """自定义分成测试类"""
    customUid = 100500205
    pack_cal_uid = config.bb_user['pack_cal_uid']  # 打包结算签约主播
    ceoUid = config.live_role['pack_ceo']  # 公会长

    def setUp(self):
        """测试前置清理"""
        pass

    def tearDown(self):
        """测试后置清理"""
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        mysql.checkBrokerUserRate(cls.pack_cal_uid, cls.ceoUid, rate=100)

    def _prepare_test_data(self, setup_steps):
        """准备测试数据"""
        for step in setup_steps:
            if step['action'] == 'update_money':
                UserMoneyOperations.update(**step['params'])
            elif step['action'] == 'clear_user_money':
                mysql.updateUserMoneyClearSql(*step['uids'])
            elif step['action'] == 'check_user_broker':
                mysql.checkUserBroker(**step['params'])
            elif step['action'] == 'check_broker_rate':
                mysql.checkBrokerUserRate(**step['params'])

    def _validate_db_state(self, checks):
        """验证数据库状态"""
        for check in checks:
            field = check['field']
            uid = check['uid']
            expected = check['expected']
            kwargs = check.get('kwargs', {})
            assert_equal(mysql.selectUserInfoSql(field, uid, **kwargs), expected)

    def test_01_roomPayCustomRate_50(self):
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
        des = '商业房打赏自定义分成:50'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 30, 'money_cash': 30, 'money_cash_b': 30, 'money_b': 10}},
            {'action': 'clear_user_money', 'uids': (self.customUid, self.ceoUid)},
            {'action': 'check_user_broker', 'params': {'uid': self.customUid, 'bid': self.ceoUid}},
            {'action': 'check_broker_rate', 'params': {'uid': self.customUid, 'bid': self.ceoUid, 'rate': 50}}
        ])
        
        # 发送请求
        data = encodeData(money=100, uid=self.customUid, giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0},
            {'field': 'single_money', 'uid': self.customUid, 'expected': 100 * config.rate * 0.5, 'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': self.ceoUid, 'expected': 100 * config.rate * (1-0.5), 'kwargs': {'money_type': 'money_cash'}}
        ])
        
        case_list_b[des] = result

    def test_02_chatPayCustomRate_80(self):
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
        des = '私聊打赏自定义分成:80'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 930, 'money_cash': 30, 'money_cash_b': 30, 'money_b': 10}},
            {'action': 'clear_user_money', 'uids': (self.customUid, self.ceoUid)},
            {'action': 'check_user_broker', 'params': {'uid': self.customUid, 'bid': self.ceoUid}},
            {'action': 'check_broker_rate', 'params': {'uid': self.customUid, 'bid': self.ceoUid, 'rate': 80}}
        ])
        
        # 发送请求
        data = encodeData(payType='chat-gift', uid=self.customUid)
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0},
            {'field': 'sum_money', 'uid': self.customUid, 'expected': 636},
            {'field': 'single_money', 'uid': self.customUid, 'expected': 1000 * (config.rate - 0.2) * 0.8, 'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': self.ceoUid, 'expected': 1000 * (config.rate - 0.2) * 0.2, 'kwargs': {'money_type': 'money_cash'}}
        ])
        
        case_list_b[des] = result

    def test_03_defendPayCustomRate_25(self):
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
        des = '个人守护打赏自定义分成:25'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 52000}},
            {'action': 'clear_user_money', 'uids': (self.customUid, self.ceoUid)},
            {'action': 'check_user_broker', 'params': {'uid': self.customUid, 'bid': self.ceoUid}},
            {'action': 'check_broker_rate', 'params': {'uid': self.customUid, 'bid': self.ceoUid, 'rate': 25}}
        ])
        
        # 发送请求
        data = encodeData(payType='defend', uid=self.customUid, money=52000, defend_id=2)
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0},
            {'field': 'single_money', 'uid': self.customUid, 'expected': 7800, 'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': self.ceoUid, 'expected': 24440, 'kwargs': {'money_type': 'money_cash'}}
        ])
        
        case_list_b[des] = result

    def test_04_liveRoomPayCustomRate_70(self):
        """
        用例描述：
        tdr:后台自定义分成比例为70%（所得公会魅力值部分*70%与公会长按照比例分成，公会长原分成不变）
        脚本步骤：
        1.构造打赏者，被打赏者和公会长数据
        2.房间内打赏流程
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：100 - 100 = 0
        5.检查主播余额，预期为：100 * 0.6 * 0.7 =  42
        6.检查被打赏者公会长余额，预期为：100 * 0.21  + 100 * 0.6 * 0.3 = 39
        """
        des = '直播公会房间打赏自定义分成比:70'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 30, 'money_cash': 30, 'money_cash_b': 30, 'money_b': 10}},
            {'action': 'clear_user_money', 'uids': (self.pack_cal_uid, self.ceoUid)},
            {'action': 'check_broker_rate', 'params': {'uid': self.pack_cal_uid, 'bid': self.ceoUid, 'rate': 70}}
        ])
        
        # 发送请求
        data = encodeData(money=100, rid=config.live_role['live_rid'], uid=self.pack_cal_uid, giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0},
            {'field': 'single_money', 'uid': self.pack_cal_uid, 'expected': 100 * 0.6 * 0.7, 'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': self.ceoUid, 'expected': 39, 'kwargs': {'money_type': 'money_cash'}}
        ])
        
        case_list_b[des] = result

    def test_05_liveChatPayCustomRate_0(self):
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
        des = '直播公会私聊打赏自定义分成比:0'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 30, 'money_cash': 3000, 'money_cash_b': 70}},
            {'action': 'clear_user_money', 'uids': (self.pack_cal_uid, self.ceoUid)},
            {'action': 'check_broker_rate', 'params': {'uid': self.pack_cal_uid, 'bid': self.ceoUid, 'rate': 0}}
        ])
        
        # 发送请求
        data = encodeData(payType='chat-gift', uid=self.pack_cal_uid)
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 2100},
            {'field': 'single_money', 'uid': self.pack_cal_uid, 'expected': 0, 'kwargs': {'money_type': 'money_cash'}},
            {'field': 'sum_money', 'uid': self.pack_cal_uid, 'expected': 0},
            {'field': 'single_money', 'uid': self.ceoUid, 'expected': 800, 'kwargs': {'money_type': 'money_cash'}}
        ])
        
        case_list_b[des] = result
