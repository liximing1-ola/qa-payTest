# coding=utf-8
"""
金豆支付测试

场景差异通过模块级 SCENES 表声明，由 PayTestBase.run_case 统一执行；
金豆账户（xs_user_money_extend）读写由自定义 _prepare_test_data 扩展。
"""
from case.base import PayCase, PayTestBase
from common.Config import config
from common.conMysql import conMysql as mysql
from common.method import calculate_vip_exp
from common.runFailed import Retry

SCENES = [
    PayCase(
        des='打赏金豆礼物但金豆不足的场景',
        setup=[
            {'action': 'delete_beans'},
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 10000}}
        ],
        data={'giftId': config.giftId['362'], 'giftType': 'bean'},
        checks=[
            {'field': 'bean', 'uid': config.rewardUid, 'expected': 0}
        ],
        success=0,
        msg='金豆不足'),
    PayCase(
        des='打赏金豆礼物的场景',
        setup=[
            {'action': 'insert_beans', 'params': {'uid': config.payUid, 'money_coupon': 6000}}
        ],
        data={'payType': 'package-more', 'giftId': config.giftId['362'], 'giftType': 'bean',
              'num': 6, 'uids': (str(config.rewardUid),)},
        checks=[
            {'field': 'bean', 'uid': config.payUid, 'expected': 0},
            {'field': 'bean', 'uid': config.rewardUid, 'expected': 3000}
        ]),
    PayCase(
        des='打赏金豆礼物不足用钻转换的场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 10000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}},
            {'action': 'insert_beans', 'params': {'uid': config.payUid, 'money_coupon': 500}}
        ],
        queries=[('vip_level', lambda: int(mysql.selectUserInfoSql('pay_room_money', config.payUid)))],
        data={'payType': 'package-exchange', 'giftId': config.giftId['362'], 'giftType': 'bean'},
        checks=[
            {'field': 'bean', 'uid': config.payUid, 'expected': 500},
            {'field': 'bean', 'uid': config.rewardUid, 'expected': 500},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 9000},
            {'field': 'pay_room_money', 'uid': config.payUid,
             'expected': lambda ctx: ctx['vip_level'] + calculate_vip_exp(money_type='bean', pay_off=1000)}
        ]),
    PayCase(
        des='私聊打赏钻石礼物时金豆不再抵扣平台手续费',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}},
            {'action': 'insert_beans', 'params': {'uid': config.payUid, 'money_coupon': 200}}
        ],
        data={'payType': 'chat-gift'},
        checks=[
            {'field': 'bean', 'uid': config.payUid, 'expected': 200},
            {'field': 'single_money', 'uid': config.payUid, 'expected': 0, 'kwargs': {'money_type': 'money'}},
            {'field': 'sum_money', 'uid': config.rewardUid, 'expected': 720}
        ]),
    PayCase(
        des='房间打赏钻石礼物时金豆不再抵扣平台手续费',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}},
            {'action': 'insert_beans', 'params': {'uid': config.payUid, 'money_coupon': 400}}
        ],
        checks=[
            {'field': 'bean', 'uid': config.payUid, 'expected': 400},
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 620},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ]),
]


@Retry(max_n=3)
class TestPayBean(PayTestBase):
    """金豆支付测试类"""

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
        """金豆账户准备步骤（delete_beans / insert_beans），其余步骤转发基类"""
        for step in setup_steps:
            action = step['action']
            if action == 'delete_beans':
                mysql.deleteUserBeanSql(config.payUid, config.rewardUid)
            elif action == 'insert_beans':
                mysql.insertBeanSql(**step['params'])
            else:
                super()._prepare_test_data([step])

    def test_01_NoBeanPayBeanGift(self):
        """金豆不足时打赏金豆礼物，提示金豆不足"""
        self.run_case(SCENES[0])

    def test_02_beanPayChangeGoldGift(self):
        """金豆足够时打赏金豆礼物，按 50% 到账"""
        self.run_case(SCENES[1])

    def test_03_MoneyConvertGoldPayGift(self):
        """金豆不足用钻转换，同时校验 VIP 经验增长"""
        self.run_case(SCENES[2])

    def test_04_ImMoneyPayChangeBeanDeduct(self):
        """私聊打赏钻石礼物，金豆不再抵扣平台手续费"""
        self.run_case(SCENES[3])

    def test_05_RoomMoneyConvertGoldPayGift(self):
        """房间打赏钻石礼物，金豆不再抵扣平台手续费"""
        self.run_case(SCENES[4])
