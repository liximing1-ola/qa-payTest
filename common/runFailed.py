# -*- coding: utf-8 -*-
"""
失败用例重跑装饰器

Usage:
    @Retry              # 默认重试1次
    def test_001(self): pass

    @Retry(max_n=3)     # 重试3次
    def test_002(self): pass

    @Retry(max_n=2, func_prefix="test_1")  # 只重试test_1开头的方法
    class TestClass(unittest.TestCase): pass
"""
import sys
import functools
import traceback
import inspect
import time


class Retry:
    """失败重试装饰器，支持函数和方法级别重试"""

    def __new__(cls, func_or_cls=None, max_n=1, func_prefix="test"):
        instance = object.__new__(cls)
        if func_or_cls:
            instance.__init__(func_or_cls, max_n, func_prefix)
            time.sleep(1)
            return instance(func_or_cls)
        time.sleep(1)
        return instance

    def __init__(self, func_or_cls=None, max_n=1, func_prefix="test"):
        self._prefix = func_prefix
        self._max_n = max_n

    def _format_traceback(self):
        """格式化异常堆栈"""
        exc_type, exc_value, exc_tb = sys.exc_info()
        return ''.join(traceback.format_exception(exc_type, exc_value, exc_tb, limit=3))

    def _retry_wrapper(self, func):
        """创建重试包装器"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, self._max_n + 2):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt <= self._max_n:
                        print(self._format_traceback(), e)
                        if args and hasattr(args[0], 'tearDown') and hasattr(args[0], 'setUp'):
                            args[0].tearDown()
                            args[0].setUp()
                    else:
                        raise
        return wrapper

    def __call__(self, func_or_cls=None):
        if inspect.isfunction(func_or_cls):
            return self._retry_wrapper(func_or_cls)

        elif inspect.isclass(func_or_cls):
            for name, func in list(func_or_cls.__dict__.items()):
                if inspect.isfunction(func) and name.startswith(self._prefix):
                    setattr(func_or_cls, name, self(func))
            return func_or_cls

        else:
            raise AttributeError("Retry只能用于函数或类")
