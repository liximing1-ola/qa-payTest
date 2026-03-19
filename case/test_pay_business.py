from common.Config import config
from common.conMysql import conMysql as mysql
from common.Request import post_request_session
from common.method import checkUserVipExp
import unittest
from common.Assert import assert_code, assert_equal, assert_body, assert_len
from common.method import reason
from common.basicData import encodeData
from common.Consts import case_list, result
from common.runFailed import Retry


@Retry(max_n=3)
class TestPayBusiness(unittest.TestCase):
    """商业房支付测试类"""
    business_uid = 105002103  # 商业房auto_rid房主（一代宗师）
    ceo_uid = config.live_role['pack_ceo']  # 直播公会公会长

    def setUp(self):
        """测试前置清理"""
        pass

    def tearDown(self):
        """测试后置清理"""
        pass

    def _prepare_test_data(self, setup_steps):
        """准备测试数据"""
        for step in setup_steps:
            if step['action'] == 'update_money':
                mysql.updateMoneySql(**step['params'])

    def _validate_db_state(self, checks):
        """验证数据库状态"""
        for check in checks:
            field = check['field']
            uid = check['uid']
            expected = check['expected']
            kwargs = check.get('kwargs', {})
            if 'assert_func' in check:
                check['assert_func'](mysql.selectUserInfoSql(field, uid, **kwargs), expected)
            else:
                assert_equal(mysql.selectUserInfoSql(field, uid, **kwargs), expected)

    def test_01_businessPayGiftNormalUser(self):
        """
        用例描述：
        验证余额足够时，商业房打赏礼物给普通用户分成满足师徒收益(非一代宗师)的基础上为：62:38，且收入在个人魅力值
        师父为公会成员，收到的师徒分成进个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏礼物（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.62 =62 (money_cash_b)
        5.检查被打赏者师徒账户，预期为：100 * 0.05 = 5（money_cash_b）
        6.检查打赏者VIP经验值变动
        """
        des = '商业房礼物打赏普通用户到账62%(mcb)'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 30, 'money_cash': 30, 'money_cash_b': 30, 'money_b': 10}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}},
            {'action': 'update_money', 'params': {'uid': config.gsUid}}
        ])
        
        # 记录初始VIP等级
        vip_level = int(mysql.selectUserInfoSql('pay_room_money', config.payUid))
        
        # 发送请求
        data = encodeData(money=100, giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 62},
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 5},
            {'field': 'sum_money', 'uid': config.gsUid, 'expected': 5},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0},
            {'field': 'pay_room_money', 'uid': config.payUid, 'expected': vip_level + checkUserVipExp()}
        ])
        
        case_list[des] = result

    def test_02_businessPayBoxNormalUser(self):
        """
        用例描述：
        验证余额足够时，商业房打赏分成满足师徒收益(一代宗师)的基础上为：70:30，且收入在个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏礼盒（打赏box）
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：700 - 600 = 100
        5.检查收礼用户账户余额，预期值为不小于：210
        """
        des = '商业房打赏box一代用户到账70%(mcb)'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 400, 'money_cash': 100, 'money_cash_b': 100, 'money_b': 100}},
            {'action': 'update_money', 'params': {'uid': config.masterUid}}
        ])
        
        # 记录初始VIP等级
        vip_level = int(mysql.selectUserInfoSql('pay_room_money', config.payUid))
        
        # 发送请求
        data = encodeData(money=600, uid=config.masterUid, giftId=config.giftId['46'], star=4)
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        
        # 验证数据库
        income = mysql.selectUserInfoSql('pay_change', uid=config.masterUid, money_type='_in_c_b')
        self._validate_db_state([
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 100},
            {'field': 'single_money', 'uid': config.masterUid, 'expected': income},
            {'field': 'pay_room_money', 'uid': config.payUid, 'expected': vip_level + checkUserVipExp(pay_off=600)}
        ])
        
        case_list[des] = result

    def test_03_businessPayGiftToGs(self):
        """
        用例描述：
        验证余额足够时，商业房打赏礼物给GS分成为：62:38，且收入在公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏礼物（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.62 =62 (money_cash)
        """
        des = '商业房礼物打赏GS到账62%(mc)'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 30, 'money_cash': 30, 'money_cash_b': 30, 'money_b': 10}},
            {'action': 'update_money', 'params': {'uid': config.gsUid}}
        ])
        
        # 发送请求
        data = encodeData(money=100, uid=config.gsUid, giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        
        # 验证数据库
        expected_amount = 100 * config.rate
        self._validate_db_state([
            {'field': 'single_money', 'uid': config.gsUid, 'expected': expected_amount, 'kwargs': {'money_type': 'money_cash'}},
            {'field': 'sum_money', 'uid': config.gsUid, 'expected': expected_amount},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ])
        
        case_list[des] = result

    def test_04_businessPayBoxToGs(self):
        """
        用例描述：
        验证商业房内送box给多个人时逻辑正常且GS分成为：62:38，且收入在公会魅力值
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
        2.giveBox
        3.校验接口状态和返回值数据
        4.检查账户余额，预期值为：10000 - 2100*2*2 = 1600
        5.检查收箱用户账户余额，预期值为不小于：2000 * 0.62 = 1240（money_cash）
        """
        des = '商业房打赏box给GS到账62%（mc）'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 10000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ])
        
        # 发送请求
        data = encodeData(
            payType='package-more',
            num=2,
            star=2,
            money=2100,
            giftId=config.giftId['47'],
            uids=('{}'.format(config.rewardUid), '{}'.format(config.gsUid))
        )
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 1600},
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 620, 'assert_func': assert_len},
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 2000 * config.rate, 'kwargs': {'money_type': 'money_cash'}, 'assert_func': assert_len},
            {'field': 'sum_money', 'uid': config.gsUid, 'expected': 2000 * config.rate, 'assert_func': assert_len}
        ])
        
        case_list[des] = result

    @unittest.skip('')
    def test_05_musicOrderPayGiftToGs(self):
        """
        用例描述：
        验证余额足够时，business-music内点歌给GS分成为：62:38，且收入在公会魅力值
        限制：房型限定为business-music
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间选中GS点歌（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：3000 * 0.62 = 1860 (money_cash)
        """
        pass

    def test_06_businessPayGiftToBusinessCreator(self):
        """
        用例描述：
        验证余额足够时，打赏礼物给商业房房主分成为：70:30，且收入在公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏礼物（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.7 =70 (money_cash)
        """
        des = '礼物打赏商业房房主到账70%(mc)'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 30, 'money_cash': 30, 'money_cash_b': 30, 'money_b': 10}},
            {'action': 'update_money', 'params': {'uid': self.business_uid}}
        ])
        
        # 发送请求
        data = encodeData(money=100, uid=self.business_uid, giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': self.business_uid, 'expected': 70, 'kwargs': {'money_type': 'money_cash'}},
            {'field': 'sum_money', 'uid': self.business_uid, 'expected': 70},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ])
        
        case_list[des] = result

    def test_07_businessPayGiftToBrokerCreator(self):
        """
        用例描述：
        验证余额足够时，打赏礼物给公会会长分成为：70:30，且收入在公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏礼物（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.7 =70 (money_cash)
        """
        des = '礼物打赏公会会长到账70%(mc)'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 30, 'money_cash': 30, 'money_cash_b': 30, 'money_b': 10}},
            {'action': 'update_money', 'params': {'uid': self.ceo_uid}}
        ])
        
        # 发送请求
        data = encodeData(money=100, uid=self.ceo_uid, giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': self.ceo_uid, 'expected': 70, 'kwargs': {'money_type': 'money_cash'}},
            {'field': 'sum_money', 'uid': self.ceo_uid, 'expected': 70},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ])
        
        case_list[des] = result
