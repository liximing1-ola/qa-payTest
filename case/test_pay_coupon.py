"""
优惠券支付测试

场景差异通过模块级 SCENES 表声明，由 PayTestBase.run_case 统一执行。
"""
from case.base import PayCase, PayTestBase

from common.con_mysql import ConMysql as mysql
from common.config import config
from common.run_failed import Retry

# 老司机券 / 电台青铜体验券
GIFT_CID_COUPON = config.commodity.coupon_cid
GIFT_CID_RADIO = config.commodity.radio_cid

SCENES = [
    PayCase(
        des='房间打赏但余额不足的场景',
        setup=[
            {'action': 'clear_user_money', 'uids': (config.pay_uid, config.reward_uid)}
        ],
        data={'money': 100, 'giftId': config.gift_id['5']},
        checks=[
            {'field': 'sum_money', 'uid': config.reward_uid, 'expected': 0}
        ],
        success=0,
        msg='余额不足，无法支付'),
    PayCase(
        des='打赏礼物使用未激活券的场景',
        setup=[
            {'action': 'delete_commodity', 'uid': config.pay_uid},
            {'action': 'insert_commodity', 'params': {'uid': config.pay_uid, 'cid': GIFT_CID_COUPON, 'num': 1}},
            {'action': 'update_money', 'params': {'uid': config.pay_uid, 'money': 3000}},
            {'action': 'update_money', 'params': {'uid': config.reward_uid}}
        ],
        queries=[('cid', lambda: mysql.select_user_info_sql('id_commodity', config.pay_uid, cid=GIFT_CID_COUPON))],
        data={'giftId': config.gift_id['11'], 'money': 3000,
              'package_cid': lambda ctx: ctx['cid'],
              'ctype': 'coupon', 'duction_money': 500},
        checks=[
            {'field': 'sum_money', 'uid': config.reward_uid, 'expected': 0},
            {'field': 'sum_money', 'uid': config.pay_uid, 'expected': 3000}
        ],
        success=0,
        msg='余额不足，无法支付'),
    PayCase(
        des='打赏礼物时有激活券的场景',
        setup=[
            {'action': 'delete_commodity', 'uid': config.pay_uid},
            {'action': 'insert_commodity', 'params': {'uid': config.pay_uid, 'cid': GIFT_CID_COUPON, 'num': 1, 'state': 1}},
            {'action': 'update_money', 'params': {'uid': config.pay_uid, 'money': 3000}},
            {'action': 'update_money', 'params': {'uid': config.reward_uid}}
        ],
        queries=[('cid', lambda: mysql.select_user_info_sql('id_commodity', config.pay_uid, cid=GIFT_CID_COUPON))],
        data={'giftId': config.gift_id['11'], 'money': 3000,
              'package_cid': lambda ctx: ctx['cid'],
              'ctype': 'coupon', 'duction_money': 500},
        checks=[
            {'field': 'sum_money', 'uid': config.reward_uid, 'expected': 1860},
            {'field': 'sum_money', 'uid': config.pay_uid, 'expected': 500}
        ]),
    PayCase(
        des='房间内打赏多人场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.pay_uid, 'money': 5000, 'money_cash': 5000,
                                                  'money_cash_b': 5000, 'money_b': 5000}},
            {'action': 'clear_user_money', 'uids': (config.master_uid, config.reward_uid, config.gs_uid)}
        ],
        data={'payType': 'package-more', 'num': 6,
              'uids': (str(config.gs_uid), str(config.reward_uid), str(config.master_uid))},
        checks=[
            {'field': 'single_money', 'uid': config.reward_uid, 'expected': 3720},
            {'field': 'single_money', 'uid': config.master_uid, 'expected': 4200},
            {'field': 'single_money', 'uid': config.gs_uid, 'expected': 6000 * config.rate,
             'kwargs': {'money_type': 'money_cash'}},
            {'field': 'single_money', 'uid': config.pay_uid, 'expected': 2000,
             'kwargs': {'money_type': 'money_cash'}}
        ]),
    PayCase(
        des='电台使用青铜体验券',
        setup=[
            {'action': 'delete_commodity', 'uid': config.pay_uid},
            {'action': 'insert_commodity', 'params': {'uid': config.pay_uid, 'cid': GIFT_CID_RADIO, 'num': 1}},
            {'action': 'clear_user_money', 'uids': (config.pay_uid, config.reward_uid)}
        ],
        queries=[('cid', lambda: mysql.select_user_info_sql('id_commodity', config.pay_uid, cid=GIFT_CID_RADIO))],
        data={'payType': 'package-radioDefend', 'rid': 200022566, 'money': 520,
              'package_cid': lambda ctx: ctx['cid']},
        checks=[
            {'field': 'sum_money', 'uid': config.reward_uid, 'expected': 0},
            {'field': 'sum_money', 'uid': config.pay_uid, 'expected': 0},
            {'field': 'num_commodity', 'uid': config.pay_uid, 'expected': 0, 'kwargs': {'cid': GIFT_CID_RADIO}}
        ]),
]


@Retry(max_n=3)
class TestPayCoupon(PayTestBase):
    """优惠券支付测试类"""

    def test_01_RoomPayNoMoney(self):
        """余额不足时房间一对一打赏，支付失败"""
        self.run_case(SCENES[0])

    def test_02_couponNoStatePayChange(self):
        """打赏礼物使用未激活券(state=0)，支付失败"""
        self.run_case(SCENES[1])

    def test_03_couponStatePayChange(self):
        """打赏礼物使用激活券(state=1)，券抵扣 500 后正常结算"""
        self.run_case(SCENES[2])

    def test_04_RoomToMorePayChange(self):
        """房间内一对多打赏 6 人，各自按分成比例到账"""
        self.run_case(SCENES[3])

    def test_05_couponNoStatePayChange(self):
        """电台房使用青铜体验券开通坑位，不分成"""
        self.run_case(SCENES[4])
