"""
common/Assert.py 单元测试（断言工具）

全部 mock 外部依赖，可在无后端环境下直接运行：
    python -m pytest tests/test_assert.py -v
"""
import unittest
from unittest.mock import patch

from common import consts


class TestAssertCode(unittest.TestCase):
    """assert_code 成功/失败"""

    def setUp(self):
        """清理全局状态"""
        consts.fail_case_reason.clear()

    @patch('common.assert_util._delay_for_rpc')
    def test_success(self, _mock_delay):
        """状态码匹配时应返回 True"""
        from common.assert_util import assert_code
        result = assert_code(200, 200)
        self.assertTrue(result)
        self.assertEqual(len(consts.fail_case_reason), 0)

    @patch('common.assert_util._delay_for_rpc')
    def test_failure(self, _mock_delay):
        """状态码不匹配时应记录失败并抛出 AssertionError"""
        from common.assert_util import assert_code
        with self.assertRaises(AssertionError):
            assert_code(500, 200)
        self.assertEqual(len(consts.fail_case_reason), 1)
        self.assertIn('500', consts.fail_case_reason[0])


class TestAssertEqual(unittest.TestCase):
    """assert_equal 成功/失败"""

    def setUp(self):
        consts.fail_case_reason.clear()

    def test_success(self):
        """值相等时应返回 True"""
        from common.assert_util import assert_equal
        result = assert_equal(42, 42)
        self.assertTrue(result)

    def test_failure(self):
        """值不等时应记录失败并抛出"""
        from common.assert_util import assert_equal
        with self.assertRaises(AssertionError):
            assert_equal(1, 2)
        self.assertEqual(len(consts.fail_case_reason), 1)


class TestAssertLen(unittest.TestCase):
    """assert_len 成功/失败"""

    def setUp(self):
        consts.fail_case_reason.clear()

    def test_success(self):
        """实际长度 >= 预期时应返回 True"""
        from common.assert_util import assert_len
        result = assert_len(5, 3)
        self.assertTrue(result)

    def test_success_equal(self):
        """实际长度 == 预期时也应返回 True"""
        from common.assert_util import assert_len
        result = assert_len(3, 3)
        self.assertTrue(result)

    def test_failure(self):
        """实际长度 < 预期时应抛出"""
        from common.assert_util import assert_len
        with self.assertRaises(AssertionError):
            assert_len(1, 5)
        self.assertEqual(len(consts.fail_case_reason), 1)


class TestAssertInText(unittest.TestCase):
    """assert_in_text 成功/失败"""

    def setUp(self):
        consts.fail_case_reason.clear()

    def test_success(self):
        """body 中包含预期文本时应返回 True"""
        from common.assert_util import assert_in_text
        result = assert_in_text({'msg': '操作成功', 'code': 0}, '操作成功')
        self.assertTrue(result)

    def test_failure(self):
        """body 中不包含预期文本时应抛出"""
        from common.assert_util import assert_in_text
        with self.assertRaises(AssertionError):
            assert_in_text({'msg': '操作失败'}, '操作成功')
        self.assertEqual(len(consts.fail_case_reason), 1)


class TestAssertBody(unittest.TestCase):
    """assert_body 成功/失败"""

    def setUp(self):
        consts.fail_case_reason.clear()

    def test_success(self):
        """字段值匹配时应返回 True"""
        from common.assert_util import assert_body
        result = assert_body({'code': 200, 'msg': 'ok'}, 'code', 200)
        self.assertTrue(result)

    def test_failure(self):
        """字段值不匹配时应抛出"""
        from common.assert_util import assert_body
        with self.assertRaises(AssertionError):
            assert_body({'code': 500}, 'code', 200)
        self.assertEqual(len(consts.fail_case_reason), 1)


class TestAssertBetween(unittest.TestCase):
    """assert_between 成功/失败"""

    def setUp(self):
        consts.fail_case_reason.clear()

    def test_success_within_range(self):
        """数值在范围内应返回 True"""
        from common.assert_util import assert_between
        result = assert_between(5, 1, 10)
        self.assertTrue(result)

    def test_success_at_boundary(self):
        """数值在边界上应返回 True"""
        from common.assert_util import assert_between
        result = assert_between(1, 1, 10)
        self.assertTrue(result)
        result = assert_between(10, 1, 10)
        self.assertTrue(result)

    def test_failure_below_range(self):
        """数值低于范围应抛出"""
        from common.assert_util import assert_between
        with self.assertRaises(AssertionError):
            assert_between(0, 1, 10)

    def test_failure_above_range(self):
        """数值高于范围应抛出"""
        from common.assert_util import assert_between
        with self.assertRaises(AssertionError):
            assert_between(11, 1, 10)


class TestRecordFailure(unittest.TestCase):
    """_record_failure 记录到 consts.fail_case_reason"""

    def setUp(self):
        consts.fail_case_reason.clear()

    def test_records_reason(self):
        """应将原因追加到 fail_case_reason"""
        from common.assert_util import _record_failure
        _record_failure('test failure reason')
        self.assertEqual(consts.fail_case_reason, ['test failure reason'])

    def test_multiple_failures(self):
        """多次失败应累积记录"""
        from common.assert_util import _record_failure
        _record_failure('reason 1')
        _record_failure('reason 2')
        self.assertEqual(len(consts.fail_case_reason), 2)


class TestAssertWrapper(unittest.TestCase):
    """_assert_wrapper 异常透传"""

    def setUp(self):
        consts.fail_case_reason.clear()

    def test_assertion_error_propagates(self):
        """AssertionError 应直接透传不被包装"""
        from common.assert_util import _assert_wrapper

        @_assert_wrapper
        def failing_func():
            raise AssertionError('direct assertion')

        with self.assertRaises(AssertionError) as ctx:
            failing_func()
        self.assertIn('direct assertion', str(ctx.exception))

    def test_other_exception_records_and_raises(self):
        """非 AssertionError 异常应记录并重新抛出"""
        from common.assert_util import _assert_wrapper

        @_assert_wrapper
        def error_func():
            raise RuntimeError('unexpected error')

        with self.assertRaises(RuntimeError):
            error_func()
        self.assertEqual(len(consts.fail_case_reason), 1)
        self.assertIn('执行异常', consts.fail_case_reason[0])

    def test_none_return_becomes_true(self):
        """函数返回 None 时应转为 True"""
        from common.assert_util import _assert_wrapper

        @_assert_wrapper
        def none_func():
            return None

        result = none_func()
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
