from common.Config import config
from common.conMysql import conMysql as mysql
import unittest
from common.Request import post_request_session
from common.method import reason, calculate_vip_exp
from common.Assert import assert_code, assert_equal, assert_body
from common.basicData import encodeData
from common.Consts import result, case_list
from common.runFailed import Retry


@Retry(max_n=3)
class TestPayBean(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        mysql.checkXsGiftConfig()

    def setUp(self) -> None:
        """测试前置清理"""
        mysql.deleteUserBeanSql(config.payUid, config.rewardUid)

    def tearDown(self) -> None:
        """测试后置清理"""
        mysql.deleteUserBeanSql(config.payUid, config.rewardUid)

    def _prepare_test_data(self, setup_steps):
        """准备测试数据"""
        for step in setup_steps:
            if step['action'] == 'delete_beans':
                mysql.deleteUserBeanSql(config.payUid, config.rewardUid)
            elif step['action'] == 'update_money':
                UserMoneyOperations.update(**step['params'])
            elif step['action'] == 'insert_beans':
                mysql.insertBeanSql(**step['params'])

    def _validate_db_state(self, checks):
        """验证数据库状态"""
        for check in checks:
            field = check['field']
            uid = check['uid']
            expected = check['expected']
            kwargs = check.get('kwargs', {})
            assert_equal(mysql.selectUserInfoSql(field, uid, **kwargs), expected)

    def test_01_NoBeanPayBeanGift(self):
        """
        用例描述：
        验证账户内金豆不足时打赏金豆礼物的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内打赏金豆礼物流程(道具：啵啵奶茶，数量：1)
        3.校验接口状态和返回值数据
        4.检查Toast，预期提示'金豆不足'
        5.检查被打赏者金豆余额,预期：0
        """
        des = '打赏金豆礼物但金豆不足的场景'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'delete_beans'},
            {'action': 'update_money', 'params': {'money': 10000}}
        ])
        
        # 发送请求
        data = encodeData(giftId=config.giftId['362'], giftType='bean')
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, format_reason(des, res))
        assert_body(res['body'], 'msg', '金豆不足', format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'bean', 'uid': config.rewardUid, 'expected': 0}
        ])
        
        case_list[des] = result

    def test_02_beanPayChangeGoldGift(self):
        """
        用例描述：
        验证金豆足够时打赏金豆礼物的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内打赏金豆礼物的流程（金豆足够）
        3.校验接口状态和返回值数据
        4.检查打赏者金豆余额，预期为：0
        5.检查被打赏者金豆余额，预期为：6000 * 0.5 = 3000
        """
        des = '打赏金豆礼物的场景'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'insert_beans', 'params': {'money_coupon': 6000}}
        ])
        
        # 发送请求
        data = encodeData(
            payType='package-more',
            giftId=config.giftId['362'],
            giftType='bean',
            num=6,
            uids=(str(config.rewardUid),)
        )
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'bean', 'uid': config.payUid, 'expected': 0},
            {'field': 'bean', 'uid': config.rewardUid, 'expected': 3000}
        ])
        
        case_list[des] = result

    def test_03_MoneyConvertGoldPayGift(self):
        """
        用例描述：
        验证打赏金豆礼物时金豆不足用钻转换的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内打赏金豆礼物流程
        3.校验接口状态和返回值数据
        4.检查打赏者金豆余额，预期为：500（不足抵扣）
        5.检查打赏者钻石余额，预期为：10000 - 1000（转换） = 9000
        6.检查被打赏者金豆余额，预期为：1000 * 0.5 = 500
        """
        des = '打赏金豆礼物不足用钻转换的场景'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 10000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}},
            {'action': 'insert_beans', 'params': {'uid': config.payUid, 'money_coupon': 500}}
        ])
        
        # 记录初始VIP等级
        vip_level = int(mysql.selectUserInfoSql('pay_room_money', config.payUid))
        
        # 发送请求
        data = encodeData(
            payType='package-exchange',
            giftId=config.giftId['362'],
            giftType='bean'
        )
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'bean', 'uid': config.payUid, 'expected': 500},
            {'field': 'bean', 'uid': config.rewardUid, 'expected': 500},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 9000}
        ])
        
        # 验证VIP经验值增长
        assert_equal(
            mysql.selectUserInfoSql('pay_room_money', config.payUid),
            vip_level + calculate_vip_exp(money_type='bean', pay_off=1000)
        )
        
        case_list[des] = result

    def test_04_ImMoneyPayChangeBeanDeduct(self):
        """
        用例描述：
        验证私聊场景打赏钻石礼物时金豆抵扣平台手续费的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊页打赏钻石礼物的流程
        3.校验接口状态和返回值数据
        4.检查打赏者金豆余额，预期为：200 - 0 = 200（2022.2.24 金豆不再抵扣20%）
        5.检查打赏者钻石余额，预期为：1000 - 1000 = 0
        6.检查被打赏者钻石余额，预期为：1000 * 0.72 = 720
        """
        des = '私聊打赏钻石礼物时金豆不再抵扣平台手续费'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}},
            {'action': 'insert_beans', 'params': {'uid': config.payUid, 'money_coupon': 200}}
        ])
        
        # 发送请求
        data = encodeData(payType='chat-gift')
        res = post_request_session(config.pay_url, data=data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'bean', 'uid': config.payUid, 'expected': 200},
            {'field': 'single_money', 'uid': config.payUid, 'expected': 0, 'kwargs': {'money_type': 'money'}},
            {'field': 'sum_money', 'uid': config.rewardUid, 'expected': 720}
        ])
        
        case_list[des] = result

    def test_05_RoomMoneyConvertGoldPayGift(self):
        """
        用例描述：
        验证房间内打赏钻石礼物时金豆抵扣平台手续费的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内打赏金豆礼物的流程
        3.校验接口状态和返回值数据
        4.检查打赏者金豆余额，预期为：400 - 0 = 400
        5.检查打赏者钻石余额，预期为：1000 - 1000 = 0
        6.检查被打赏者账户余额，预期为：1000 * 0.62 = 620
        """
        des = '房间打赏钻石礼物时金豆不再抵扣平台手续费'
        
        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}},
            {'action': 'insert_beans', 'params': {'uid': config.payUid, 'money_coupon': 400}}
        ])
        
        # 发送请求
        data = encodeData()
        res = post_request_session(config.pay_url, data)
        
        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 验证数据库
        self._validate_db_state([
            {'field': 'bean', 'uid': config.payUid, 'expected': 400},
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 620},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ])
        
        case_list[des] = result

    @unittest.skip('2022/5/12 金豆不再抵扣手续费')
    def test_06_MoneyConvertGoldPayGift(self):
        """
        用例描述：
        验证房间内打赏钻石礼物时金豆抵扣平台手续费的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内打赏金豆礼物的流程
        3.校验接口状态和返回值数据
        4.检查预期：支付失败（钻石小于当前礼物价格时，打赏失败），提示Toast：'余额不足，无法支付'
        5.检查打赏者钻石余额,预期：700
        6.检查打赏者金豆余额,预期：400
        """
        pass

    @unittest.skip('玩法已下线')
    def test_07_BeanPayChangeCombo(self):
        """
        用例描述：
        验证卡座内购买套餐的场景（钻补）
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.卡座内购买酒桌套餐的流程
        3.校验接口状态和返回值数据
        4.检查购买者金豆余额，预期为：400
        5.检查购买者钻石余额，预期为：80000 - 79900 = 100
        """
        pass
