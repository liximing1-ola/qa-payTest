import unittest
import pytest


@unittest.skip('爵位购买')
class TestPayCreate(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_01_TitlePayChangeMoney(self, des='开通爵位场景'):
        """
        用例描述：
        验证爵位开通及返钱到余额（money）
        脚本步骤：
        1.清空背包内物品，模拟开通者数据
        2.开通子爵
        3.校验接口和返回值数据
        4.检查剩余钱值,预期值：（200000 - 100000 + 60000 = 160000）
        """
        pass

    @pytest.mark.run(order=2)
    def test_02_TitlePayChangeRenew(self, des='爵位续费场景'):
        """
        用例描述：
        续01，验证爵位续费及返钱到余额（money）
        脚本步骤：
        1.清空背包内物品，模拟开通者数据
        2.续费子爵
        3.校验接口状态和返回值数据
        4.检查剩余钱值,预期值：（200000 - 60000 + 36000 = 176000）
        """
        pass
