# coding=utf-8
"""
common/Logs.py、Assert.py、runFailed.py 单元测试

可在无后端环境下直接运行：
    python -m pytest tests/test_utils.py -v
"""
import functools
import logging
import unittest
from unittest.mock import patch

# ============ Logs.py 测试 ============

from common.Logs import (
    get_logger,
    _ensure_log_dir,
    _create_handlers,
    DEFAULT_WHEN,
    DEFAULT_BACK_COUNT,
    DEFAULT_LOG_LEVEL,
)
from logging.handlers import TimedRotatingFileHandler


class TestEnsureLogDir(unittest.TestCase):
    """日志目录创建"""

    def test_returns_existing_path(self):
        """返回的路径应在 BASE_PATH/log 下"""
        import os
        from common.Config import config
        path = _ensure_log_dir()
        self.assertEqual(path, os.path.join(config.BASE_PATH, 'log'))

    def test_directory_exists_after_call(self):
        """调用后目录应存在"""
        import os
        path = _ensure_log_dir()
        self.assertTrue(os.path.isdir(path))


class TestCreateHandlers(unittest.TestCase):
    """Handler 创建"""

    def test_returns_two_handlers(self):
        """应返回控制台和文件两个 handler"""
        import tempfile, os
        formatter = logging.Formatter('%(message)s')
        with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as f:
            tmp_path = f.name
        try:
            console, file_h = _create_handlers(tmp_path, logging.DEBUG, formatter)
            self.assertIsInstance(console, logging.StreamHandler)
            self.assertIsInstance(file_h, TimedRotatingFileHandler)
        finally:
            # 关闭 handler 释放文件句柄
            file_h.close()
            os.unlink(tmp_path)

    def test_custom_when_and_back_count(self):
        """自定义 when/back_count 应被正确应用"""
        import tempfile, os
        formatter = logging.Formatter('%(message)s')
        with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as f:
            tmp_path = f.name
        try:
            _, file_h = _create_handlers(tmp_path, logging.DEBUG, formatter,
                                         when='H', back_count=5)
            self.assertEqual(file_h.backupCount, 5)
            self.assertIn('H', file_h.suffix)  # 小时轮转 suffix 含 _%H
        finally:
            file_h.close()
            os.unlink(tmp_path)


class TestGetLogger(unittest.TestCase):
    """get_logger 集成"""

    def test_returns_logger_instance(self):
        """应返回 logging.Logger 实例"""
        lg = get_logger('_test_unit.log')
        self.assertIsInstance(lg, logging.Logger)
        self.assertEqual(lg.name, '_test_unit.log')

    def test_has_two_handlers(self):
        """首次调用应有 2 个 handler（console + file）"""
        lg = get_logger('_test_unit_handlers.log')
        self.assertEqual(len(lg.handlers), 2)

    def test_duplicate_call_no_new_handlers(self):
        """同名重复调用不应增加 handler"""
        lg1 = get_logger('_test_unit_dup.log')
        lg2 = get_logger('_test_unit_dup.log')
        self.assertIs(lg1, lg2)
        self.assertEqual(len(lg1.handlers), 2)

    def test_custom_params_applied(self):
        """自定义 when/back_count 应传递到文件 handler"""
        lg = get_logger('_test_unit_custom.log', when='H', back_count=7)
        file_handlers = [h for h in lg.handlers
                         if isinstance(h, TimedRotatingFileHandler)]
        self.assertEqual(len(file_handlers), 1)
        self.assertEqual(file_handlers[0].backupCount, 7)


# ============ Assert.py 测试 ============

from common import Consts
from common.Assert import (
    _assert,
    _record_failure,
    assert_code,
    assert_len,
    assert_equal,
    assert_in_text,
    assert_body,
    assert_between,
    RPC_DELAY,
)


class TestCoreAssert(unittest.TestCase):
    """核心 _assert 函数"""

    def setUp(self):
        Consts.fail_case_reason.clear()

    def test_passes_on_true(self):
        """条件为真不应抛异常"""
        _assert(True, 'should not fail')
        self.assertEqual(len(Consts.fail_case_reason), 0)

    def test_raises_on_false(self):
        """条件为假应抛 AssertionError"""
        with self.assertRaises(AssertionError) as ctx:
            _assert(False, 'test reason')
        self.assertEqual(str(ctx.exception), 'test reason')
        self.assertIn('test reason', Consts.fail_case_reason)


class TestRecordFailure(unittest.TestCase):
    """_record_failure"""

    def setUp(self):
        Consts.fail_case_reason.clear()

    def test_appends_to_global_list(self):
        """应将原因追加到 fail_case_reason"""
        _record_failure('reason A')
        _record_failure('reason B')
        self.assertEqual(Consts.fail_case_reason, ['reason A', 'reason B'])


class TestAssertCode(unittest.TestCase):
    """assert_code"""

    def setUp(self):
        Consts.fail_case_reason.clear()

    @patch('common.Assert._delay_for_rpc')
    def test_passes_on_200(self, mock_delay):
        """状态码 200 应通过"""
        result = assert_code(200)
        self.assertTrue(result)
        self.assertEqual(len(Consts.fail_case_reason), 0)

    @patch('common.Assert._delay_for_rpc')
    def test_fails_on_500(self, mock_delay):
        """状态码 500 应失败"""
        with self.assertRaises(AssertionError):
            assert_code(500)
        self.assertTrue(len(Consts.fail_case_reason) > 0)

    @patch('common.Assert._delay_for_rpc')
    def test_custom_expected(self, mock_delay):
        """自定义期望状态码"""
        self.assertTrue(assert_code(301, 301))


class TestAssertLen(unittest.TestCase):
    """assert_len"""

    def setUp(self):
        Consts.fail_case_reason.clear()

    def test_passes_when_actual_gte_expected(self):
        """actual >= expect 应通过"""
        self.assertTrue(assert_len(10, 5))
        self.assertTrue(assert_len(5, 5))

    def test_fails_when_actual_lt_expected(self):
        """actual < expect 应失败"""
        with self.assertRaises(AssertionError):
            assert_len(3, 5)
        self.assertTrue(len(Consts.fail_case_reason) > 0)


class TestAssertEqual(unittest.TestCase):
    """assert_equal"""

    def setUp(self):
        Consts.fail_case_reason.clear()

    def test_passes_on_equal(self):
        """相等值应通过"""
        self.assertTrue(assert_equal(42, 42))
        self.assertTrue(assert_equal('abc', 'abc'))

    def test_fails_on_unequal(self):
        """不等值应失败"""
        with self.assertRaises(AssertionError):
            assert_equal(1, 2)
        self.assertTrue(len(Consts.fail_case_reason) > 0)


class TestAssertInText(unittest.TestCase):
    """assert_in_text"""

    def setUp(self):
        Consts.fail_case_reason.clear()

    def test_passes_when_found(self):
        """JSON 中包含目标文本应通过"""
        body = {'msg': '操作成功', 'code': 0}
        self.assertTrue(assert_in_text(body, '操作成功'))

    def test_fails_when_not_found(self):
        """JSON 中不包含目标文本应失败"""
        body = {'msg': '操作失败'}
        with self.assertRaises(AssertionError):
            assert_in_text(body, '操作成功')


class TestAssertBody(unittest.TestCase):
    """assert_body"""

    def setUp(self):
        Consts.fail_case_reason.clear()

    def test_passes_on_match(self):
        """字段值匹配应通过"""
        body = {'status': 'ok', 'code': 200}
        self.assertTrue(assert_body(body, 'status', 'ok'))

    def test_fails_on_mismatch(self):
        """字段值不匹配应失败"""
        body = {'status': 'error'}
        with self.assertRaises(AssertionError):
            assert_body(body, 'status', 'ok')


class TestAssertBetween(unittest.TestCase):
    """assert_between"""

    def setUp(self):
        Consts.fail_case_reason.clear()

    def test_passes_in_range(self):
        """范围内的值应通过"""
        self.assertTrue(assert_between(50, 10, 100))
        self.assertTrue(assert_between(10, 10, 100))  # 下边界
        self.assertTrue(assert_between(100, 10, 100))  # 上边界

    def test_fails_out_of_range(self):
        """范围外的值应失败"""
        with self.assertRaises(AssertionError):
            assert_between(5, 10, 100)
        with self.assertRaises(AssertionError):
            assert_between(101, 10, 100)


# ============ runFailed.py 测试 ============

from common.runFailed import Retry


class TestRetryDecorator(unittest.TestCase):
    """Retry 重试装饰器"""

    def test_bare_decorator_succeeds_first_try(self):
        """@Retry 装饰的函数首次成功应直接返回"""
        @Retry(interval=0)
        def always_ok():
            return 42
        self.assertEqual(always_ok(), 42)

    def test_bare_decorator_retries_then_succeeds(self):
        """@Retry 装饰的函数首次失败、重试后成功"""
        call_count = [0]

        @Retry(max_n=2, interval=0)
        def fail_once():
            call_count[0] += 1
            if call_count[0] < 2:
                raise ValueError('not ready')
            return 'ok'

        self.assertEqual(fail_once(), 'ok')
        self.assertEqual(call_count[0], 2)

    def test_max_retries_exhausted(self):
        """超过最大重试次数应抛出异常"""
        @Retry(max_n=1, interval=0)
        def always_fail():
            raise RuntimeError('always')

        with self.assertRaises(RuntimeError):
            always_fail()

    def test_max_n_count(self):
        """max_n=3 应总共执行 4 次（1 次原始 + 3 次重试）"""
        call_count = [0]

        @Retry(max_n=3, interval=0)
        def always_fail():
            call_count[0] += 1
            raise RuntimeError('fail')

        with self.assertRaises(RuntimeError):
            always_fail()
        self.assertEqual(call_count[0], 4)

    def test_class_decorator(self):
        """类装饰器应为 test_ 开头的方法添加重试"""
        import unittest as ut

        @Retry(max_n=1, interval=0)
        class MyTest(ut.TestCase):
            def test_ok(self):
                return True

            def helper_not_test(self):
                raise RuntimeError('should not be retried')

        # test_ok 应该被装饰
        obj = MyTest()
        self.assertTrue(obj.test_ok())

    def test_functools_wraps_preserves_name(self):
        """装饰后应保留原函数名"""
        @Retry(interval=0)
        def my_function():
            """docstring"""
            pass

        self.assertEqual(my_function.__name__, 'my_function')
        self.assertEqual(my_function.__doc__, 'docstring')


if __name__ == '__main__':
    unittest.main()
