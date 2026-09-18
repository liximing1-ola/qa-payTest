# coding=utf-8
"""
歌友房支付测试

场景差异通过模块级 SCENES 表声明，由 PayTestBase.run_case 统一执行。
"""
import pytest

from case.base import PayCase, PayTestBase
from common.Config import config
from common.conMysql import conMysql as mysql
from common.runFailed import Retry

# 打包结算主播 / 直播公会公会长
PACK_CAL_UID = config.bb_user.pack_cal_uid
PACK_CEO_UID = config.live_role['pack_ceo']

SCENES = [
    PayCase(
        des='歌友房直播工会收60%公会魅力值',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'clear_user_money', 'params': {'uid1': PACK_CAL_UID, 'uid2': PACK_CEO_UID}}
        ],
        data={'payType': 'package', 'rid': lambda ctx: ctx['cls'].singer_rid, 'uid': PACK_CAL_UID},
        checks=[
            {'field': 'single_money', 'uid': PACK_CAL_UID, 'money_type': 'money_cash', 'expected': 600},
            {'field': 'sum_money', 'uid': PACK_CAL_UID, 'expected': 600},
            {'field': 'sum_money', 'uid': PACK_CEO_UID, 'expected': 0},
            {'field': 'sum_money', 'expected': 0}
        ],
        report='case_list_b'),
    PayCase(
        des='歌友房普通工会收62%公会魅力值',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': config.gsUid}}
        ],
        data={'payType': 'package', 'rid': lambda ctx: ctx['cls'].singer_rid, 'uid': config.gsUid},
        checks=[
            {'field': 'single_money', 'uid': config.gsUid, 'money_type': 'money_cash', 'expected': 1000 * config.rate},
            {'field': 'sum_money', 'uid': config.gsUid, 'expected': 1000 * config.rate},
            {'field': 'sum_money', 'expected': 0}
        ],
        report='case_list_b'),
    PayCase(
        des='歌友房打赏箱子GS收62%（mc）',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 600}},
            {'action': 'update_money', 'params': {'uid': config.gsUid}}
        ],
        data={'payType': 'package', 'money': 600, 'rid': lambda ctx: ctx['cls'].singer_rid,
              'giftId': config.giftId['46'], 'uid': config.gsUid, 'star': 1},
        checks=[
            {'field': 'sum_money', 'expected': 0},
            {'field': 'single_money', 'uid': config.gsUid, 'money_type': 'money_cash', 'min_value': 300 * config.rate},
            {'field': 'sum_money', 'uid': config.gsUid, 'min_value': 300 * config.rate}
        ],
        report='case_list_b'),
    PayCase(
        des='歌友房普通用户礼物打赏收个人魅力值',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ],
        data={'rid': lambda ctx: ctx['cls'].singer_rid},
        checks=[
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 620},
            {'field': 'sum_money', 'uid': config.rewardUid, 'expected': 620},
            {'field': 'sum_money', 'expected': 0}
        ],
        report='case_list_b'),
]


@Retry(max_n=3)
class TestPayUnionRoom(PayTestBase):
    """歌友房支付测试类"""

    @classmethod
    def setUpClass(cls):
        """查询歌友房 rid（延迟到运行期，避免 import 阶段依赖数据库）"""
        cls.singer_rid = mysql.selectUserInfoSql('union')

    @pytest.mark.run(order=1)
    def test_01_singerRoomLiveBrokerRate_60(self):
        """歌友房内，直播公会成员礼物打赏到账60%公会魅力值"""
        self.run_case(SCENES[0])

    def test_02_singerRoomNormalBrokerRate_62(self):
        """歌友房内，普通公会成员礼物打赏到账62%公会魅力值"""
        self.run_case(SCENES[1])

    def test_03_singerPayBoxNormalBrokerRate_62(self):
        """歌友房内，普通公会成员箱子打赏到账62%公会魅力值"""
        self.run_case(SCENES[2])

    def test_04_singerRoomPayNormalUser(self):
        """歌友房内，非公会成员收到礼物打赏时收62%个人魅力值（师徒）"""
        self.run_case(SCENES[3])
