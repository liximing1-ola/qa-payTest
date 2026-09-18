# coding=utf-8
"""
家族房支付测试

场景差异通过模块级 SCENES 表声明，由 PayTestBase.run_case 统一执行。
"""
from case.base import PayCase, PayTestBase
from common.Config import config
from common.Assert import assert_len
from common.conMysql import conMysql as mysql
from common.runFailed import Retry

# 本家族房 rid / 直播公会gs
FLEET_RID = config.bb_user.fleetRid
PACK_CAL_UID = config.bb_user.pack_cal_uid

SCENES = [
    PayCase(
        des='家族房打赏直播公会gs场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': PACK_CAL_UID}}
        ],
        data={'rid': FLEET_RID, 'uid': PACK_CAL_UID},
        checks=[
            {'field': 'single_money', 'uid': PACK_CAL_UID, 'expected': 800},
            {'field': 'sum_money', 'uid': PACK_CAL_UID, 'expected': 800},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ],
        report='case_list_b'),
    PayCase(
        des='非本家族房打赏直播公会GS场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': PACK_CAL_UID}}
        ],
        data={'rid': lambda ctx: ctx['cls'].other_fleet_rid, 'uid': PACK_CAL_UID},
        checks=[
            {'field': 'single_money', 'uid': PACK_CAL_UID, 'expected': 700},
            {'field': 'sum_money', 'uid': PACK_CAL_UID, 'expected': 700},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ],
        report='case_list_b'),
    PayCase(
        des='fleetRoom打赏普通公会gs场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': config.gsUid}}
        ],
        data={'rid': FLEET_RID, 'uid': config.gsUid},
        checks=[
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 800},
            {'field': 'sum_money', 'uid': config.gsUid, 'expected': 800},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ],
        report='case_list_b'),
    PayCase(
        des='非本家族房打赏公会GS场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 600}},
            {'action': 'update_money', 'params': {'uid': config.gsUid}}
        ],
        data={'money': 600, 'rid': lambda ctx: ctx['cls'].other_fleet_rid,
              'giftId': config.giftId['46'], 'uid': config.gsUid, 'star': 1},
        checks=[
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0},
            {'field': 'single_money', 'uid': config.gsUid, 'expected': 210, 'assert_func': assert_len}
        ],
        report='case_list_b'),
    PayCase(
        des='fleetRoom打赏一代用户场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 600}},
            {'action': 'update_money', 'params': {'uid': config.masterUid}}
        ],
        data={'money': 600, 'rid': FLEET_RID, 'giftId': config.giftId['46'],
              'uid': config.masterUid, 'star': 1},
        checks=[
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0},
            {'field': 'single_money', 'uid': config.masterUid, 'expected': 300 * 0.8, 'assert_func': assert_len}
        ],
        report='case_list_b'),
    PayCase(
        des='非本fleet房打赏场景',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ],
        data={'rid': lambda ctx: ctx['cls'].other_fleet_rid},
        checks=[
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 620},
            {'field': 'sum_money', 'uid': config.payUid, 'expected': 0}
        ],
        report='case_list_b'),
]


@Retry(max_n=3)
class TestPayFleetRoom(PayTestBase):
    """家族房支付测试类"""

    @classmethod
    def setUpClass(cls):
        """查询非本家族房 rid（延迟到运行期，避免 import 阶段依赖数据库）"""
        cls.other_fleet_rid = mysql.selectUserInfoSql('fleet')

    def test_01_sameFleetRoomLiveGsRate(self):
        """同家族房内直播公会成员礼物打赏到账80%个人魅力值"""
        self.run_case(SCENES[0])

    def test_02_otherFleetRoomLiveGsRate(self):
        """非家族房内直播公会成员礼物打赏到账70%个人魅力值"""
        self.run_case(SCENES[1])

    def test_03_sameFleetRoomNormalGsRate(self):
        """家族房内普通公会成员礼物打赏到账80%个人魅力值"""
        self.run_case(SCENES[2])

    def test_04_otherFleetRoomNormalGsRate(self):
        """非家族房内GS收到箱子打赏拿70%个人魅力值"""
        self.run_case(SCENES[3])

    def test_05_sameFleetRoomPayNormalUser(self):
        """家族房内一代宗师普通用户箱子打赏到账80%个人魅力值"""
        self.run_case(SCENES[4])

    def test_06_otherFleetRoomNormalGsRate(self):
        """other家族房内普通用户礼物打赏到账62%个人魅力值"""
        self.run_case(SCENES[5])
