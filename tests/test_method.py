# coding=utf-8
"""
common/method.py 纯逻辑函数单元测试

仅覆盖不依赖数据库 / 网络的纯逻辑分支，可在无后端环境下直接运行：
    python -m pytest tests/test_method.py -v
"""
import unittest

from common import Consts
from common.method import (
    dict_to_slack_fields,
    dict_to_markdown,
    is_extend,
    _get_all_keys,
    get_value,
    format_reason,
    get_user_title,
    calculate_vip_exp,
)


class TestDictConversion(unittest.TestCase):
    """字典格式化转换"""

    def test_dict_to_markdown(self):
        self.assertEqual(
            dict_to_markdown({'x': 'ok', 'y': 'fail'}),
            'scene-x：ok\nscene-y：fail',
        )

    def test_dict_to_markdown_empty(self):
        self.assertEqual(dict_to_markdown({}), '')

    def test_dict_to_slack_fields(self):
        self.assertEqual(
            dict_to_slack_fields({'x': 'ok'}),
            [{'title': 'Scene:x', 'value': '执行结果:ok', 'short': False}],
        )

    def test_dict_to_slack_fields_empty(self):
        self.assertEqual(dict_to_slack_fields({}), [])


class TestJsonUtils(unittest.TestCase):
    """JSON key 检查"""

    def test_get_all_keys_nested(self):
        keys = _get_all_keys({'a': {'b': 1}, 'c': [{'d': 2}]})
        self.assertEqual(set(keys), {'a', 'b', 'c', 'd'})

    def test_is_extend_found_nested(self):
        self.assertTrue(is_extend({'a': {'b': 1}}, 'b'))

    def test_is_extend_not_found(self):
        self.assertFalse(is_extend({'a': 1}, 'x'))

    def test_is_extend_non_dict_input(self):
        self.assertFalse(is_extend(['a', 'b'], 'a'))


class TestGetValue(unittest.TestCase):
    """并发结果统计（读写 Consts 全局计数）"""

    def setUp(self):
        Consts.success_num = 0
        Consts.fail_num = 0

    def test_success_increments_success_num(self):
        get_value({'body': {'success': 1}})
        self.assertEqual(Consts.success_num, 1)
        self.assertEqual(Consts.fail_num, 0)

    def test_failure_increments_fail_num(self):
        get_value({'body': {'success': 0}})
        self.assertEqual(Consts.success_num, 0)
        self.assertEqual(Consts.fail_num, 1)

    def test_missing_body_increments_fail_num(self):
        get_value({'code': 200})
        self.assertEqual(Consts.fail_num, 1)


class TestFormatReason(unittest.TestCase):
    """失败原因格式化"""

    def test_contains_description_and_body(self):
        reason = format_reason('开通场景', {'body': {'success': 0, 'msg': 'x'}})
        self.assertIn('Depiction: 开通场景', reason)
        self.assertIn('failReason', reason)

    def test_slp_mode_returns_reason_string(self):
        reason = format_reason('slp场景', {'body': {'success': True}}, slp=True)
        self.assertIn('Depiction: slp场景', reason)

    def test_missing_body_defaults_to_empty(self):
        reason = format_reason('无body', {})
        self.assertIn('Depiction: 无body', reason)


class TestTitleLevel(unittest.TestCase):
    """爵位系数"""

    def test_known_levels(self):
        self.assertEqual(get_user_title(10), 1.0)
        self.assertEqual(get_user_title(90), 2.0)

    def test_unknown_level_returns_none(self):
        self.assertIsNone(get_user_title(999))


class TestCalculateVipExp(unittest.TestCase):
    """VIP 经验计算（仅测 bean 与异常分支，money/coin 依赖数据库不在此覆盖）"""

    def test_bean_multiplier(self):
        self.assertEqual(calculate_vip_exp('bean', pay_off=100), 150)
        self.assertEqual(calculate_vip_exp('bean', pay_off=10), 15)

    def test_unsupported_money_type_raises(self):
        with self.assertRaises(ValueError):
            calculate_vip_exp('unknown')


if __name__ == '__main__':
    unittest.main()
