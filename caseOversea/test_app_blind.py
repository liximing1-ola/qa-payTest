# coding=utf-8
"""
APP 海外版支付测试 - 盲盒打赏验证

验证房间内送盲盒的逻辑。
"""
from caseOversea.base import OverseaBizCase, OverseaBizTestBase
from common.Assert import assert_equal
from common.Config import config
from common.conPtMysql import conMysql
from common.runFailed import Retry


def _assert_blind_reconcile():
    """校验收礼人到账金额与 pay_change 流水一致"""
    assert_equal(conMysql.selectUserInfoSql('money_cash_personal', config.oversea_testUid,
                                            money_type='money_cash_personal'),
                 conMysql.selectUserInfoSql('pay_change', config.oversea_testUid))


# 场景表：房间盲盒打赏（单人次/多人次多个）
BLIND_SCENES = [
    OverseaBizCase(
        des='房间送盲盒场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.oversea_payUid, 'money': 100,
                                                  'money_cash': 100, 'money_cash_b': 100, 'money_b': 100}},
            {'action': 'update_money', 'params': {'uid': config.oversea_testUid}},
            {'action': 'clear_extend_money', 'params': {'uid': config.oversea_testUid}},
        ],
        # 沿用原用例的礼物引用：'773' 在 config.giftId 中未定义，行为与原实现一致
        data={'payType': 'package', 'money': 300,
              'rid': config.oversea_room['th_union'], 'giftId': lambda ctx: config.giftId['773']},
        checks=[
            {'field': 'sum_money', 'expected': 100},
            {'field': 'money_cash_personal', 'uid': config.oversea_testUid, 'min': 30},
            {'assert_func': _assert_blind_reconcile},
        ],
    ),
    OverseaBizCase(
        des='房间送多人多个盲盒场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.oversea_payUid, 'money': 10000}},
            {'action': 'update_money', 'params': {'uid': config.oversea_testUid}},
            {'action': 'clear_extend_money', 'params': {'uid': config.oversea_testUid}},
        ],
        # 沿用原用例的礼物引用：'774' 在 config.giftId 中未定义，行为与原实现一致
        data={'payType': 'package-more', 'num': 2, 'money': 1200,
              'rid': config.oversea_room['th_union'], 'giftId': lambda ctx: config.giftId['774']},
        checks=[
            {'field': 'sum_money', 'expected': 5200},
            {'field': 'money_cash_personal', 'uid': config.oversea_testUid, 'min': 60},
        ],
    ),
]


@Retry
class TestPayCreate(OverseaBizTestBase):
    """房间盲盒打赏测试类"""

    bigarea_id = 6
    room_type = 'union'
    room_rid = config.oversea_room['th_union']
    room_area = 'th'
    clear_redis_on_teardown = True

    def test_01_giveBlindPayChange(self, des: str = '房间送盲盒场景'):
        """房间送盲盒验证：打赏者余额 400-300=100，收礼人到账不小于 30 且与流水一致"""
        self.run_case(BLIND_SCENES[0])

    def test_02_giveBlindMorePeople(self, des: str = '房间送多人多个盲盒场景'):
        """房间送多人盲盒验证：打赏者余额 10000-1200*2*2=5200，收礼人到账不小于 60"""
        self.run_case(BLIND_SCENES[1])
