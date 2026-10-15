"""
common/Consts.py 单元测试

可在无后端环境下直接运行：
    python -m pytest tests/test_consts.py -v
"""
import unittest

from common import Consts


class TestIncrementCounters(unittest.TestCase):
    """线程安全计数器"""

    def setUp(self):
        Consts.success_num = 0
        Consts.fail_num = 0

    def test_increment_success(self):
        """increment_success 应递增 success_num"""
        Consts.increment_success()
        Consts.increment_success()
        self.assertEqual(Consts.success_num, 2)

    def test_increment_fail(self):
        """increment_fail 应递增 fail_num"""
        Consts.increment_fail()
        self.assertEqual(Consts.fail_num, 1)


class TestReset(unittest.TestCase):
    """reset 全局重置"""

    def test_reset_clears_all(self):
        """reset 应重置所有全局可变状态"""
        Consts.case_list['a'] = 1
        Consts.case_list_b['b'] = 2
        Consts.case_list_c['c'] = 3
        Consts.fail_case_reason.append('reason')
        Consts.result = '❌'
        Consts.startTime = 100
        Consts.endTime = 200
        Consts.success_num = 5
        Consts.fail_num = 3

        Consts.reset()

        self.assertEqual(Consts.case_list, {})
        self.assertEqual(Consts.case_list_b, {})
        self.assertEqual(Consts.case_list_c, {})
        self.assertEqual(Consts.fail_case_reason, [])
        self.assertEqual(Consts.result, '✅')
        self.assertEqual(Consts.startTime, 0)
        self.assertEqual(Consts.endTime, 0)
        self.assertEqual(Consts.success_num, 0)
        self.assertEqual(Consts.fail_num, 0)


if __name__ == '__main__':
    unittest.main()
