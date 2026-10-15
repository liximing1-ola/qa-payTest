"""
商业房支付测试

场景差异通过模块级 SCENES 表声明，由 PayTestBase.run_case 统一执行。
"""
import unittest

from case.base import PayCase, PayTestBase

from common.assert_util import assert_len
from common.con_mysql import ConMysql as mysql
from common.config import config
from common.method import calculate_vip_exp
from common.run_failed import Retry

BUSINESS_UID = config.business_uid  # 商业房 auto_rid 房主（一代宗师）
CEO_UID = config.live_role['pack_ceo']  # 直播公会公会长

SCENES = [
    PayCase(
        des='商业房礼物打赏普通用户到账62%(mcb)',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.pay_uid, 'money': 30, 'money_cash': 30,
                                                  'money_cash_b': 30, 'money_b': 10}},
            {'action': 'update_money', 'params': {'uid': config.reward_uid}},
            {'action': 'update_money', 'params': {'uid': config.gs_uid}}
        ],
        queries=[('vip_level', lambda: int(mysql.select_user_info_sql('pay_room_money', config.pay_uid)))],
        data={'money': 100, 'giftId': config.gift_id['5']},
        checks=[
            {'field': 'single_money', 'uid': config.reward_uid, 'expected': 62},
            {'field': 'single_money', 'uid': config.gs_uid, 'expected': 5},
            {'field': 'sum_money', 'uid': config.gs_uid, 'expected': 5},
            {'field': 'sum_money', 'uid': config.pay_uid, 'expected': 0},
            {'field': 'pay_room_money', 'uid': config.pay_uid,
             'expected': lambda ctx: ctx['vip_level'] + calculate_vip_exp()}
        ]),
    PayCase(
        des='商业房打赏box一代用户到账70%(mcb)',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.pay_uid, 'money': 400, 'money_cash': 100,
                                                  'money_cash_b': 100, 'money_b': 100}},
            {'action': 'update_money', 'params': {'uid': config.master_uid}}
        ],
        queries=[('vip_level', lambda: int(mysql.select_user_info_sql('pay_room_money', config.pay_uid)))],
        data={'money': 600, 'uid': config.master_uid, 'giftId': config.gift_id['46'], 'star': 4},
        checks=[
            {'field': 'sum_money', 'uid': config.pay_uid, 'expected': 100},
            {'field': 'single_money', 'uid': config.master_uid,
             'expected': lambda ctx: mysql.select_user_info_sql('pay_change', uid=config.master_uid,
                                                             money_type='_in_c_b')},
            {'field': 'pay_room_money', 'uid': config.pay_uid,
             'expected': lambda ctx: ctx['vip_level'] + calculate_vip_exp(pay_off=600)}
        ]),
    PayCase(
        des='商业房礼物打赏GS到账62%(mc)',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.pay_uid, 'money': 30, 'money_cash': 30,
                                                  'money_cash_b': 30, 'money_b': 10}},
            {'action': 'update_money', 'params': {'uid': config.gs_uid}}
        ],
        data={'money': 100, 'uid': config.gs_uid, 'giftId': config.gift_id['5']},
        checks=[
            {'field': 'single_money', 'uid': config.gs_uid, 'expected': 100 * config.rate,
             'kwargs': {'money_type': 'money_cash'}},
            {'field': 'sum_money', 'uid': config.gs_uid, 'expected': 100 * config.rate},
            {'field': 'sum_money', 'uid': config.pay_uid, 'expected': 0}
        ]),
    PayCase(
        des='商业房打赏box给GS到账62%（mc）',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.pay_uid, 'money': 10000}},
            {'action': 'update_money', 'params': {'uid': config.reward_uid}}
        ],
        data={'payType': 'package-more', 'num': 2, 'star': 2, 'money': 2100,
              'giftId': config.gift_id['47'], 'uids': (str(config.reward_uid), str(config.gs_uid))},
        checks=[
            {'field': 'sum_money', 'uid': config.pay_uid, 'expected': 1600},
            {'field': 'single_money', 'uid': config.reward_uid, 'expected': 620, 'assert_func': assert_len},
            {'field': 'single_money', 'uid': config.gs_uid, 'expected': 2000 * config.rate,
             'kwargs': {'money_type': 'money_cash'}, 'assert_func': assert_len},
            {'field': 'sum_money', 'uid': config.gs_uid, 'expected': 2000 * config.rate,
             'assert_func': assert_len}
        ]),
    PayCase(
        des='礼物打赏商业房房主到账70%(mc)',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.pay_uid, 'money': 30, 'money_cash': 30,
                                                  'money_cash_b': 30, 'money_b': 10}},
            {'action': 'update_money', 'params': {'uid': BUSINESS_UID}}
        ],
        data={'money': 100, 'uid': BUSINESS_UID, 'giftId': config.gift_id['5']},
        checks=[
            {'field': 'single_money', 'uid': BUSINESS_UID, 'expected': 70,
             'kwargs': {'money_type': 'money_cash'}},
            {'field': 'sum_money', 'uid': BUSINESS_UID, 'expected': 70},
            {'field': 'sum_money', 'uid': config.pay_uid, 'expected': 0}
        ]),
    PayCase(
        des='礼物打赏公会会长到账70%(mc)',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.pay_uid, 'money': 30, 'money_cash': 30,
                                                  'money_cash_b': 30, 'money_b': 10}},
            {'action': 'update_money', 'params': {'uid': CEO_UID}}
        ],
        data={'money': 100, 'uid': CEO_UID, 'giftId': config.gift_id['5']},
        checks=[
            {'field': 'single_money', 'uid': CEO_UID, 'expected': 70,
             'kwargs': {'money_type': 'money_cash'}},
            {'field': 'sum_money', 'uid': CEO_UID, 'expected': 70},
            {'field': 'sum_money', 'uid': config.pay_uid, 'expected': 0}
        ]),
]


@Retry(max_n=3)
class TestPayBusiness(PayTestBase):
    """商业房支付测试类"""

    def test_01_businessPayGiftNormalUser(self):
        """商业房礼物打赏普通用户，师徒基础上到账 62%（mcb）"""
        self.run_case(SCENES[0])

    def test_02_businessPayBoxNormalUser(self):
        """商业房打赏 box 给一代宗师用户，到账 70%（mcb）"""
        self.run_case(SCENES[1])

    def test_03_businessPayGiftToGs(self):
        """商业房礼物打赏 GS，到账 62%（mc）"""
        self.run_case(SCENES[2])

    def test_04_businessPayBoxToGs(self):
        """商业房内送 box 给多人，GS 分成 62%（mc）"""
        self.run_case(SCENES[3])

    @unittest.skip('')
    def test_05_musicOrderPayGiftToGs(self):
        """
        用例描述：
        验证余额足够时，business-music内点歌给GS分成为：62:38，且收入在公会魅力值
        限制：房型限定为business-music
        """
        pass

    def test_06_businessPayGiftToBusinessCreator(self):
        """礼物打赏商业房房主，到账 70%（mc）"""
        self.run_case(SCENES[4])

    def test_07_businessPayGiftToBrokerCreator(self):
        """礼物打赏公会会长，到账 70%（mc）"""
        self.run_case(SCENES[5])
