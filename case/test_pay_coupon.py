from common.Config import config
from common.method import reason
from common.conMysql import conMysql as mysql
from common.Request import post_request_session
import unittest
from common.Assert import assert_code, assert_body, assert_equal
from common.basicData import encodeData
from common.Consts import case_list, result
from common.runFailed import Retry


@Retry(max_n=3)
class TestPayCoupon(unittest.TestCase):
    """优惠券支付测试类"""
    businessRid = config.live_role['auto_rid']

    def setUp(self):
        """测试前置清理"""
        pass

    def tearDown(self):
        """测试后置清理"""
        pass

    def _prepare_test_data(self, setup_steps):
        """准备测试数据"""
        for step in setup_steps:
            if step['action'] == 'clear_user_money':
                mysql.updateUserMoneyClearSql(*step['uids'])
            elif step['action'] == 'delete_commodity':
                mysql.deleteUserAccountSql('user_commodity', step['uid'])
            elif step['action'] == 'insert_commodity':
                UserCommodityOperations.insert(**step['params'])
            elif step['action'] == 'update_money':
                UserMoneyOperations.update(**step['params'])

    def _validate_db_state(self, checks):
        """验证数据库状态"""
        for check in checks:
            field = check['field']
            uid = check['uid']
            expected = check['expected']
            kwargs = check.get('kwargs', {})
            assert_equal(mysql.selectUserInfoSql(field, uid, **kwargs), expected)

    def test_01_RoomPayNoMoney(self):
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
        des = '房间打赏但余额不足的场景'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'clear_user_money', 'uids': (config.payUid, config.rewardUid)}
        ])
        
        # 发送请求
        data = encodeData(money=100, giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, format_reason(des, res))
        assert_body(res['body'], 'msg', '余额不足，无法支付', format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'uid': config.rewardUid, 'expected': 0}
        ])
        
        case_list[des] = result

    def test_02_couponNoStatePayChange(self):
        """
        用例描述：
        有未激活券(state=0)的情况下，验证打赏
        脚本步骤：
        1.构造打赏者和被打赏者数据(gift_cid=54 老司机券)
        2.房间内打赏（券可抵扣500分）
        3.校验接口状态和返回值数据
        4.预期结果： "msg": "余额不足，无法支付"
        5.检查被打赏者余额和账户，预期为：0
        6.检查打赏者余额,预期为：3000
        """
        des = '打赏礼物使用未激活券的场景'
        gift_cid = 54
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'delete_commodity', 'uid': config.payUid},
            {'action': 'insert_commodity', 'params': {'uid': config.payUid, 'cid': gift_cid, 'num': 1}},
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 3000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ])
        
        # 获取商品ID
        cid = mysql.selectUserInfoSql('id_commodity', config.payUid, cid=gift_cid)
        
        # 发送请求
        data = encodeData(
            giftId=config.giftId['11'],
            money=3000,
            package_cid=cid,
            ctype='coupon',
            duction_money=500
        )
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, format_reason(des, res))
        assert_body(res['body'], 'msg', '余额不足，无法支付', format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'uid': config.rewardUid, 'expected': 0},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 3000}
        ])
        
        case_list[des] = result

    def test_03_couponStatePayChange(self):
        """
        用例描述：
        有激活券(state=1)的情况下，验证打赏流程
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内打赏（券可抵扣500分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为：3000 * 0.62 = 1860
        5.检查打赏者余额,预期为：3000 -2500 = 500
        """
        des = '打赏礼物时有激活券的场景'
        gift_cid = 54
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'delete_commodity', 'uid': config.payUid},
            {'action': 'insert_commodity', 'params': {'uid': config.payUid, 'cid': gift_cid, 'num': 1, 'state': 1}},
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 3000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ])
        
        # 获取商品ID
        cid = mysql.selectUserInfoSql('id_commodity', config.payUid, cid=gift_cid)
        
        # 发送请求
        data = encodeData(
            giftId=config.giftId['11'],
            money=3000,
            package_cid=cid,
            ctype='coupon',
            duction_money=500
        )
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'uid': config.rewardUid, 'expected': 1860},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 500}
        ])
        
        case_list[des] = result

    def test_04_RoomToMorePayChange(self):
        """
        用例描述：
        验证非直播类型房间内一对多打赏场景
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对多打赏流程
        3.校验接口状态和返回值数据
        4.检查打赏者余额,预期为：20000-1000*6*3 = 2000
        5.检查被打赏者余额，预期为：1000*6*0.62 = 3720(非一代宗师) 1000*6*0.7=4200(一代宗师) 1000*6*0.62=3720（公会）
        """
        des = '房间内打赏多人场景'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 5000, 'money_cash': 5000, 'money_cash_b': 5000, 'money_b': 5000}},
            {'action': 'clear_user_money', 'uids': (config.masterUid, config.rewardUid, config.gsUid)}
        ])
        
        # 发送请求
        data = encodeData(
            payType='package-more',
            num=6,
            uids=('{}'.format(config.gsUid), '{}'.format(config.rewardUid), '{}'.format(config.masterUid))
        )
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'], 200)
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 3720},
            {'field': 'single_money', 'uid': config.masterUid, 'expected': 4200},
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 6000 * config.rate, 'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': config.payUid, 'expected': 2000, 'kwargs': {'money_type': 'money_cash'}}
        ])
        
        case_list[des] = result

    def test_05_couponNoStatePayChange(self):
        """
        用例描述：
        在电台房使用24小时体验青铜坑位券，不分成
        脚本步骤：
        1.构造打赏者和被打赏者数据(commodity_cid=21981 青铜物品)
        2.房间内开通坑位
        3.校验接口状态和返回值数据
        4.预期结果：开通青铜坑位成功
        5.检查被打赏者余额和账户，预期为：0
        6.检查打赏者余额,预期为：0
        """
        des = '电台使用青铜体验券'
        gift_cid = 21980
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'delete_commodity', 'uid': config.payUid},
            {'action': 'insert_commodity', 'params': {'uid': config.payUid, 'cid': gift_cid, 'num': 1}},
            {'action': 'clear_user_money', 'uids': (config.payUid, config.rewardUid)}
        ])
        
        # 获取商品ID
        cid = mysql.selectUserInfoSql('id_commodity', config.payUid, cid=gift_cid)
        
        # 发送请求
        data = encodeData(
            payType='package-radioDefend',
            rid=200022566,
            money=520,
            package_cid=cid
        )
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'uid': config.rewardUid, 'expected': 0},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0},
            {'field': 'num_commodity', 'uid': config.payUid, 'expected': 0, 'kwargs': {'cid': gift_cid}}
        ])
        
        case_list[des] = result
