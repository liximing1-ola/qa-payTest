# coding=utf-8
"""
商城支付测试

场景差异通过模块级 SCENES 表声明，由 PayTestBase.run_case 统一执行。
"""
import pytest

from case.base import PayCase, PayTestBase
from common.Config import config
from common.conMysql import conMysql as mysql
from common.runFailed import Retry

# 礼物 cid：四叶草 / 小天使
GIFT_CID_CLOVER = 329
GIFT_CID_ANGEL = 340

SCENES = [
    PayCase(
        des='商城购买单个道具场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money_cash': 100, 'money_cash_b': 100}},
            {'action': 'delete_user_account', 'params': {'table': 'user_commodity', 'uid': config.payUid}}
        ],
        data={'payType': 'shop-buy', 'money': 100, 'cid': GIFT_CID_CLOVER},
        checks=[
            {'field': 'sum_money', 'expected': 100},
            {'field': 'sum_commodity', 'expected': 1}
        ]),
    PayCase(
        des='商城购买n个道具场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000, 'money_cash': 100000,
                                                   'money_cash_b': 1000, 'money_b': 1000}}
        ],
        data={'payType': 'shop-buy', 'cid': GIFT_CID_ANGEL, 'money': 9900, 'num': 10},
        checks=[
            {'field': 'sum_money', 'expected': 4000},
            {'field': 'num_commodity', 'expected': 10, 'cid': GIFT_CID_ANGEL}
        ]),
    PayCase(
        des='打赏背包内物品场景',
        setup=[
            {'action': 'clear_user_money', 'params': {'uid1': config.payUid, 'uid2': config.rewardUid}}
        ],
        queries=[('cid', lambda: int(mysql.selectUserInfoSql('id_commodity', config.payUid, cid=GIFT_CID_ANGEL)))],
        data={'rid': config.live_role['auto_rid'], 'giftId': config.giftId['54'], 'money': 9900,
              'package_cid': lambda ctx: ctx['cid'], 'ctype': 'gift'},
        checks=[
            {'field': 'num_commodity', 'expected': 9, 'cid': GIFT_CID_ANGEL},
            {'field': 'sum_money', 'uid': config.rewardUid, 'expected': 6138}
        ]),
    PayCase(
        des='打赏背包物品但物品不足抵扣的场景',
        setup=[
            {'action': 'clear_user_money', 'params': {'uid1': config.payUid, 'uid2': config.rewardUid}}
        ],
        queries=[('cid', lambda: int(mysql.selectUserInfoSql('id_commodity', config.payUid, cid=GIFT_CID_ANGEL)))],
        data={'rid': config.live_role['auto_rid'], 'giftId': config.giftId['54'], 'money': 99000,
              'package_cid': lambda ctx: ctx['cid'], 'ctype': 'gift', 'num': 10},
        success=0,
        msg='余额不足，无法支付',
        checks=[
            {'field': 'num_commodity', 'expected': 9, 'cid': GIFT_CID_ANGEL},
            {'field': 'sum_money', 'uid': config.rewardUid, 'expected': 0}
        ]),
]


@Retry(max_n=3)
class TestPayShopBuy(PayTestBase):
    """商城支付测试类"""

    @pytest.mark.run(order=1)
    def test_01_shopPayChangeMoney(self):
        """验证商城购买道具逻辑"""
        self.run_case(SCENES[0])

    @pytest.mark.run(order=2)
    def test_02_shopPayChangeBuyMore(self):
        """验证商城购买多个道具场景"""
        self.run_case(SCENES[1])

    @pytest.mark.run(order=3)
    def test_03_shopGiftToUser(self):
        """验证商城购买的道具在房间内赠送给其他人，师徒收益分成 62:38"""
        self.run_case(SCENES[2])

    @pytest.mark.run(order=4)
    def test_04_shopGiftToUserNoEnough(self):
        """验证商城购买的道具赠送时不足的情况"""
        self.run_case(SCENES[3])
