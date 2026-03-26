from common.Config import config
from common.conMysql import conMysql as mysql
from common.method import reason
import unittest
from common.Request import post_request_session
from common.Assert import assert_body, assert_code, assert_equal, assert_len
from common.basicData import encodeData
from common.runFailed import Retry
from common.Consts import case_list_b, result


@Retry(max_n=3)
class TestPayFleetRoom(unittest.TestCase):
    """家族房支付测试类"""
    other_fleet_rid = mysql.selectUserInfoSql('fleet')  # 非本家族房
    fleet_rid = config.bb_user['fleetRid']  # 本家族房
    pack_cal_uid = config.bb_user['pack_cal_uid']  # 直播公会gs

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
                UserMoneyOperations.update(**step['params'])

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

    def test_01_sameFleetRoomLiveGsRate(self):
        """
        用例描述：
        tdr：同家族房内直播公会成员礼物打赏到账80%个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.8 = 800(money_cash_b)
        5.检查打赏者余额，预期为：1000 - 1000 = 0
        """
        des = '家族房打赏直播公会gs场景'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': self.pack_cal_uid}}
        ])
        
        # 发送请求
        data = encodeData(rid=self.fleet_rid, uid=self.pack_cal_uid)
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': self.pack_cal_uid, 'expected': 800},
            {'field': 'sum_money', 'uid': self.pack_cal_uid, 'expected': 800},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ])
        
        case_list_b[des] = result

    def test_02_otherFleetRoomLiveGsRate(self):
        """
        用例描述：
        tdr：other家族房内直播公会成员礼物打赏到账70%个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.7 = 700(money_cash_b)
        5.检查打赏者余额，预期为：1000 - 1000 = 0
        """
        des = '非本家族房打赏直播公会GS场景'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': self.pack_cal_uid}}
        ])
        
        # 发送请求
        data = encodeData(rid=self.other_fleet_rid, uid=self.pack_cal_uid)
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': self.pack_cal_uid, 'expected': 700},
            {'field': 'sum_money', 'uid': self.pack_cal_uid, 'expected': 700},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ])
        
        case_list_b[des] = result

    def test_03_sameFleetRoomNormalGsRate(self):
        """
        用例描述：
        tdr：家族房内普通公会成员礼物打赏到账80%个人魅力值
         脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.8 = 800(money_cash_b)
        5.检查打赏者余额，预期为：1000 - 1000 = 0
        """
        des = 'fleetRoom打赏普通公会gs场景'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': config.gsUid}}
        ])
        
        # 发送请求
        data = encodeData(rid=self.fleet_rid, uid=config.gsUid)
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 800},
            {'field': 'sum_money', 'uid': config.gsUid, 'expected': 800},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ])
        
        case_list_b[des] = result

    def test_04_otherFleetRoomNormalGsRate(self):
        """
        用例描述：
        tdr：非家族房内GS收到箱子打赏拿70%个人魅力值
       脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏（打赏铜箱子）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为不小于：300 * 0.7 = 210(money_cash_b)
        5.检查打赏者余额，预期为：600 - 600 = 0
        """
        des = '非本家族房打赏公会GS场景'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 600}},
            {'action': 'update_money', 'params': {'uid': config.gsUid}}
        ])
        
        # 发送请求
        data = encodeData(
            money=600,
            rid=self.other_fleet_rid,
            giftId=config.giftId['46'],
            uid=config.gsUid,
            star=1
        )
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0},
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 210, 'assert_func': assert_len}
        ])
        
        case_list_b[des] = result

    def test_05_sameFleetRoomPayNormalUser(self):
        """
        用例描述：
        tdr：家族房内一代宗师普通用户箱子打赏到账80%个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏（打赏铜箱子）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为不小于：300 * 0.8 = 240(money_cash_b)
        5.检查打赏者余额，预期为：600 - 600 = 0
        """
        des = 'fleetRoom打赏一代用户场景'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 600}},
            {'action': 'update_money', 'params': {'uid': config.masterUid}}
        ])
        
        # 发送请求
        data = encodeData(
            money=600,
            rid=self.fleet_rid,
            giftId=config.giftId['46'],
            uid=config.masterUid,
            star=1
        )
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0},
            {'field': 'single_money', 'uid': config.masterUid, 'expected': 300 * 0.8, 'assert_func': assert_len}
        ])
        
        case_list_b[des] = result

    def test_06_otherFleetRoomNormalGsRate(self):
        """
       用例描述：
        tdr：other家族房内普通用户礼物打赏到账62%个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.62 = 620(money_cash_b)
        5.检查打赏者余额，预期为：1000 - 1000 = 0
        """
        des = '非本fleet房打赏场景'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ])
        
        # 发送请求
        data = encodeData(rid=self.other_fleet_rid)
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 620},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ])
        
        case_list_b[des] = result
