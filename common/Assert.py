"""
断言验证工具模块

提供统一的断言方法，支持状态码、长度、相等性、文本包含、范围等多种验证场景。
失败时自动记录错误原因到全局状态。
"""
import json
import platform
import time
from functools import wraps
from typing import Any, Callable, Optional
from common import Consts
from common.Config import config


# RPC接口延迟配置（秒）
RPC_DELAY = 0.6


def _delay_for_rpc():
    """非阿里云环境添加延迟，防止RPC接口结果失败"""
    if platform.node() != config.linux_node['ali']:
        time.sleep(RPC_DELAY)


def _record_failure(reason: str):
    """记录失败原因到全局状态"""
    Consts.fail_case_reason.append(reason)


def _assert_wrapper(func):
    """断言包装器：统一处理异常和成功返回"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result if result is not None else True
        except AssertionError:
            raise
        except Exception as e:
            _record_failure(f'{func.__name__} 执行异常: {str(e)}')
            raise
    return wrapper


def _assert(condition: bool, reason: str):
    """核心断言函数"""
    if not condition:
        _record_failure(reason)
        raise AssertionError(reason)


@_assert_wrapper
def assert_code(actual_code: int, expected_code: int = 200) -> bool:
    """验证HTTP状态码"""
    _delay_for_rpc()
    _assert(
        actual_code == expected_code,
        f'Actual Code: {actual_code}, Expected Code: {expected_code}, 验证结果不一致，估计服务器开小差啦!'
    )
    return True


@_assert_wrapper
def assert_len(actual_len: int, expect_len: int) -> bool:
    """验证长度/数量是否满足最小要求"""
    _assert(
        actual_len >= expect_len,
        f'实际结果: {actual_len}, 预期结果: {expect_len}, 验证结果不一致，用例执行失败，望严查!'
    )
    return True


@_assert_wrapper
def assert_equal(actual_result: Any, expect_result: Any) -> bool:
    """验证两个值是否相等"""
    _assert(
        actual_result == expect_result,
        f'实际结果: {actual_result}, 预期结果: {expect_result}, 验证结果不一致，用例执行失败，望严查!'
    )
    return True


@_assert_wrapper
def assert_in_text(body: dict, expected_msg: str) -> bool:
    """验证JSON响应中是否包含指定文本"""
    text = json.dumps(body, ensure_ascii=False)
    _assert(
        expected_msg in text,
        f'响应中未找到预期文本: {expected_msg}'
    )
    return True


@_assert_wrapper
def assert_body(body: dict, body_msg: str, expected_msg: Any, reason: str) -> bool:
    """验证响应体中指定字段的值"""
    msg = body.get(body_msg)
    _assert(
        msg == expected_msg,
        f'{body_msg} 字段值不匹配: 实际 {msg}, 预期 {expected_msg}'
    )
    return True


@_assert_wrapper
def assert_between(actual_result: int, lower_limit: int, upper_limit: int) -> bool:
    """验证数值是否在指定范围内（包含边界）"""
    actual, lower, upper = int(actual_result), int(lower_limit), int(upper_limit)
    _assert(
        lower <= actual <= upper,
        f'实际结果: {actual}, 预期结果: {lower} 至 {upper}, 验证结果不一致，用例执行失败，望严查!'
    )
    return True
