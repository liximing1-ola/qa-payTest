# coding=utf-8
"""
海外版区域测试公共基类

提取 caseOversea/test_app_*.py 中重复的 setUpClass/tearDownClass
和通用导入，减少区域测试文件的样板代码。
"""
import time
import unittest

from common.Config import config
from common.conPtMysql import conMysql


class OverseaAreaTestBase(unittest.TestCase):
    """海外版分区域测试基类

    子类通过类属性声明各自的差异：
        bigarea_id:               大区 ID（1=英语, 3=阿拉伯, 4=韩语, ...）
        room_type/room_rid/room_area:
                                  若 room_rid 非 None，setUpClass 中额外设置房间大区信息
        clear_redis_on_setup:     setUpClass 后清理大区 Redis 缓存
        clear_redis_on_teardown:  tearDownClass 时清理大区 Redis 缓存（含 0.3s 延迟）
    """

    bigarea_id: int = 1
    room_type: str = None
    room_rid = None
    room_area: str = None
    clear_redis_on_setup: bool = False
    clear_redis_on_teardown: bool = False

    @classmethod
    def _clear_area_redis(cls) -> None:
        """清理大区相关的 Redis 缓存（按需导入 conRedis，避免非 Redis 场景引入依赖）"""
        from common.conRedis import conRedis
        conRedis.delKey('User.Big.Area.Id', config.oversea_user.values())
        conRedis.delKey('User.Big.Area', config.oversea_user.values())

    @classmethod
    def setUpClass(cls) -> None:
        """测试前准备：设置用户大区（及可选的房间大区 / Redis 清理）"""
        conMysql.updateUserBigArea(tuple(config.oversea_user.values()), bigarea_id=cls.bigarea_id)
        if cls.room_rid is not None:
            conMysql.updateUserRidInfoSql(cls.room_type, cls.room_rid, area=cls.room_area)
        if cls.clear_redis_on_setup:
            cls._clear_area_redis()

    @classmethod
    def tearDownClass(cls) -> None:
        """测试后清理：恢复用户大区（及可选的 Redis 清理）"""
        conMysql.updateUserBigArea(tuple(config.oversea_user.values()))
        if cls.clear_redis_on_teardown:
            time.sleep(0.3)
            cls._clear_area_redis()
