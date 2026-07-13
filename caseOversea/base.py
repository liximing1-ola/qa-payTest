# coding=utf-8
"""
海外版区域测试公共基类

提取 caseOversea/test_app_*Area.py 中重复的 setUpClass/tearDownClass
和通用导入，减少区域测试文件的样板代码。
"""
import unittest

from common.Config import config
from common.conPtMysql import conMysql


class OverseaAreaTestBase(unittest.TestCase):
    """海外版分区域测试基类

    子类通过设置类属性指定大区：
        bigarea_id: 大区 ID（1=英语, 3=阿拉伯, 4=韩语, ...）
    """

    bigarea_id: int = 1

    @classmethod
    def setUpClass(cls) -> None:
        """测试前准备：设置用户大区"""
        conMysql.updateUserBigArea(tuple(config.oversea_user.values()), bigarea_id=cls.bigarea_id)

    @classmethod
    def tearDownClass(cls) -> None:
        """测试后清理：恢复用户大区"""
        conMysql.updateUserBigArea(tuple(config.oversea_user.values()))
