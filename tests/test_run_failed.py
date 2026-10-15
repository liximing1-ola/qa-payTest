# coding=utf-8
"""
common/run_failed.py 单元测试（重试装饰器）

全部 mock 外部依赖，可在无后端环境下直接运行：
    python -m pytest tests/test_run_failed.py -v
"""
import unittest
from unittest.mock import patch


class TestRetryFunctionLevel(unittest.TestCase):
    """函数级重试行为"""

    def test_retry_on_failure_then_success(self):
        """失败后重试，最终成功应不抛出异常"""
        from common.run_failed import Retry

        call_count = 0

        @Retry(max_n=2, interval=0)
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError('transient error')
            return 'success'

        result = flaky_func()
        self.assertEqual(result, 'success')
        self.assertEqual(call_count, 3)  # 1次初始 + 2次重试

    def test_retry_exhausted_raises(self):
        """重试次数耗尽后应抛出最后一次异常"""
        from common.run_failed import Retry

        call_count = 0

        @Retry(max_n=2, interval=0)
        def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError('permanent error')

        with self.assertRaises(ValueError):
            always_fail()
        self.assertEqual(call_count, 3)  # 1次初始 + 2次重试

    def test_no_retry_on_success(self):
        """首次成功应不再重试"""
        from common.run_failed import Retry

        call_count = 0

        @Retry(max_n=3, interval=0)
        def success_func():
            nonlocal call_count
            call_count += 1
            return 'ok'

        result = success_func()
        self.assertEqual(result, 'ok')
        self.assertEqual(call_count, 1)


class TestRetryClassLevel(unittest.TestCase):
    """类级重试：仅重试 test_ 前缀方法"""

    def test_only_test_methods_retried(self):
        """只有 test_ 前缀的方法应被包装"""
        from common.run_failed import Retry

        @Retry(max_n=1, func_prefix="test", interval=0)
        class MyTestCase:
            def test_something(self):
                return 'test_result'

            def helper_method(self):
                return 'helper_result'

        obj = MyTestCase()
        # test_ 方法应被包装
        self.assertEqual(obj.test_something(), 'test_result')
        # 非 test_ 方法不应被包装
        self.assertEqual(obj.helper_method(), 'helper_result')

    def test_class_retry_on_failure(self):
        """类级重试应在 test 方法失败时重试"""
        from common.run_failed import Retry

        call_count = 0

        @Retry(max_n=2, func_prefix="test", interval=0)
        class MyTestCase:
            def test_flaky(self):
                nonlocal call_count
                call_count += 1
                if call_count < 2:
                    raise RuntimeError('fail')
                return 'recovered'

        obj = MyTestCase()
        result = obj.test_flaky()
        self.assertEqual(result, 'recovered')
        self.assertEqual(call_count, 2)


class TestRetryInterval(unittest.TestCase):
    """重试间隔行为"""

    @patch('common.run_failed.time.sleep')
    def test_sleep_called_between_retries(self, mock_sleep):
        """重试间隔应调用 time.sleep"""
        from common.run_failed import Retry

        call_count = 0

        @Retry(max_n=2, interval=3)
        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise RuntimeError('fail')
            return 'ok'

        result = flaky()
        self.assertEqual(result, 'ok')
        # sleep 应被调用 max_n 次（在每次重试前）
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_called_with(3)

    @patch('common.run_failed.time.sleep')
    def test_zero_interval_no_sleep(self, mock_sleep):
        """interval=0 时不应调用 sleep"""
        from common.run_failed import Retry

        call_count = 0

        @Retry(max_n=2, interval=0)
        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise RuntimeError('fail')
            return 'ok'

        flaky()
        mock_sleep.assert_not_called()


class TestRetryDecoratorNoArgs(unittest.TestCase):
    """Retry 装饰器不带参数使用 @Retry"""

    def test_bare_decorator(self):
        """@Retry 不带参数应使用默认值（max_n=1）"""
        from common.run_failed import Retry

        call_count = 0

        @Retry
        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RuntimeError('fail')
            return 'ok'

        result = flaky()
        self.assertEqual(result, 'ok')
        self.assertEqual(call_count, 2)


class TestRetryInvalidUsage(unittest.TestCase):
    """Retry 非法使用"""

    def test_non_function_or_class_raises(self):
        """用于非函数/非类时应抛出 AttributeError"""
        from common.run_failed import Retry

        retry = Retry(max_n=1)
        with self.assertRaises(AttributeError):
            retry(42)


if __name__ == '__main__':
    unittest.main()
