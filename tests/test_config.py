# coding=utf-8
"""
common/Config.py 契约测试（测试数据夹具锁定）

锁定各域共享实体的当前取值与结构，任何"静默改数据"都会在此显式失败；
无外部依赖，可直接运行：
    python -m pytest tests/test_config.py -v
"""
import unittest
from dataclasses import fields

from common.Config import (BBUserConfig, CommodityConfig, LiveRoleConfig,
                           OverseaRoomConfig, OverseaUserConfig, config)


class TestBBUserEntities(unittest.TestCase):
    """BB 域共享用户实体取值锁定"""

    def test_base_uids(self):
        """打赏者 / 普通被打赏者 / 打包结算 / 公会等基础实体"""
        self.assertEqual(config.bb_user.payUid, 103273407)
        self.assertEqual(config.bb_user.testUid, 105002312)
        self.assertEqual(config.bb_user.pack_cal_uid, 105002313)
        self.assertEqual(config.bb_user.gsUid, 105002325)

    def test_room_ids(self):
        """VIP 房 / 颜值房 / 舰队房房间号"""
        self.assertEqual(config.bb_user.vipRoomRid, 200089706)
        self.assertEqual(config.bb_user.prettyRid, 200089942)
        self.assertEqual(config.bb_user.fleetRid, 200091067)

    def test_converged_entities(self):
        """原散落在用例文件中的裸实体已收敛至此（一代宗师 / 商业房 / 自定义分成）"""
        self.assertEqual(config.bb_user.masterUid, 100500338)
        self.assertEqual(config.bb_user.businessUid, 105002103)
        self.assertEqual(config.bb_user.custom_rate_uid, 100500205)


class TestPropertyConsistency(unittest.TestCase):
    """Config 便捷属性与子配置逐一一致（单一数据源）"""

    def test_subconfig_types(self):
        self.assertIsInstance(config.bb_user, BBUserConfig)
        self.assertIsInstance(config.live_role, LiveRoleConfig)
        self.assertIsInstance(config.oversea_user, OverseaUserConfig)
        self.assertIsInstance(config.oversea_room, OverseaRoomConfig)
        self.assertIsInstance(config.commodity, CommodityConfig)

    def test_bb_uid_properties(self):
        """BB 便捷属性直接委托 bb_user，避免双源定义"""
        self.assertEqual(config.payUid, config.bb_user.payUid)
        self.assertEqual(config.rewardUid, config.bb_user.testUid)
        self.assertEqual(config.masterUid, config.bb_user.masterUid)
        self.assertEqual(config.businessUid, config.bb_user.businessUid)
        self.assertEqual(config.gsUid, config.bb_user.gsUid)

    def test_oversea_uid_properties(self):
        self.assertEqual(config.oversea_payUid, config.oversea_user.payUid)
        self.assertEqual(config.oversea_testUid, config.oversea_user.testUid)
        self.assertEqual(config.oversea_brokerUid, config.oversea_user.brokerUid)
        self.assertEqual(config.oversea_fleetUid, config.oversea_user.fleet_uid)

    def test_master_uid_single_source(self):
        """masterUid 必须定义在 bb_user 字段中，而非属性内硬编码"""
        names = [f.name for f in fields(BBUserConfig)]
        self.assertIn('masterUid', names)
        self.assertEqual(config.masterUid, 100500338)


class TestGiftContract(unittest.TestCase):
    """礼物 ID 映射结构与关键值锁定（用例以 config.giftId['5'] 索引，防 KeyError 回归）"""

    def test_gift_id_keys(self):
        self.assertEqual(sorted(config.giftId, key=int),
                         ['5', '7', '11', '46', '47', '54', '62', '362'])

    def test_gift_id_values(self):
        self.assertEqual(config.giftId['5'], 5)
        self.assertEqual(config.giftId['46'], 46)
        self.assertEqual(config.giftId['362'], 362)

    def test_oversea_gift_id(self):
        self.assertEqual(sorted(config.oversea_giftId, key=int),
                         ['10', '46', '47', '773', '774'])
        self.assertEqual(config.oversea_giftId['773'], 773)


class TestRoleAndCommodityContract(unittest.TestCase):
    """直播角色 / 海外用户与房间 / 商城商品取值锁定"""

    def test_live_role(self):
        self.assertEqual(config.live_role.pack_ceo, 105002314)
        self.assertEqual(config.live_role.pack_master_NoPack, 105002319)
        self.assertEqual(config.live_role.pack_cal_uid, 105002313)
        self.assertEqual(config.live_role.live_rid, 193185577)
        self.assertEqual(config.live_role.auto_rid, 193185484)
        # 下标访问与属性访问等价（用例以 config.live_role['live_rid'] 索引）
        self.assertEqual(config.live_role['live_rid'], config.live_role.live_rid)

    def test_oversea_user(self):
        self.assertEqual(config.oversea_user.payUid, 800350557)
        self.assertEqual(config.oversea_user.testUid, 800022872)
        self.assertEqual(config.oversea_user.brokerUid, 800018895)
        self.assertEqual(config.oversea_user.fleet_uid, 800041062)

    def test_oversea_room(self):
        self.assertEqual(config.oversea_room.vip_rid, 105698376)
        self.assertEqual(config.oversea_room.th_union, 105708881)
        self.assertEqual(config.oversea_room['vip_rid'], config.oversea_room.vip_rid)

    def test_commodity_cids(self):
        """优惠券商品 ID（原散落在 test_pay_coupon.py 的模块常量）"""
        self.assertEqual(config.commodity.coupon_cid, 54)
        self.assertEqual(config.commodity.radio_cid, 21980)

    def test_rate(self):
        self.assertEqual(config.rate, 0.62)


if __name__ == '__main__':
    unittest.main()
