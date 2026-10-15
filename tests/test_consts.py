"""
common/consts.py 单元测试

可在无后端环境下直接运行：
    python -m pytest tests/test_consts.py -v
"""
import unittest

from common import consts


class TestIncrementCounters(unittest.TestCase):
    """线程安全计数器"""

    def setUp(self):
        consts.success_num = 0
        consts.fail_num = 0

    def test_increment_success(self):
        """increment_success 应递增 success_num"""
        consts.increment_success()
        consts.increment_success()
        self.assertEqual(consts.success_num, 2)

    def test_increment_fail(self):
        """increment_fail 应递增 fail_num"""
        consts.increment_fail()
        self.assertEqual(consts.fail_num, 1)


class TestReset(unittest.TestCase):
    """reset 全局重置"""

    def test_reset_clears_all(self):
        """reset 应重置所有全局可变状态"""
        consts.case_list['a'] = 1
        consts.case_list_b['b'] = 2
        consts.case_list_c['c'] = 3
        consts.fail_case_reason.append('reason')
        consts.result = '❌'
        consts.startTime = 100
        consts.endTime = 200
        consts.success_num = 5
        consts.fail_num = 3

        consts.reset()

        self.assertEqual(consts.case_list, {})
        self.assertEqual(consts.case_list_b, {})
        self.assertEqual(consts.case_list_c, {})
        self.assertEqual(consts.fail_case_reason, [])
        self.assertEqual(consts.result, '✅')
        self.assertEqual(consts.startTime, 0)
        self.assertEqual(consts.endTime, 0)
        self.assertEqual(consts.success_num, 0)
        self.assertEqual(consts.fail_num, 0)


if __name__ == '__main__':
    unittest.main()
