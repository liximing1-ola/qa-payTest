"""
common/method.py 纯逻辑函数单元测试

仅覆盖不依赖数据库 / 网络的纯逻辑分支，可在无后端环境下直接运行：
    python -m pytest tests/test_method.py -v
"""
import unittest
from unittest.mock import Mock, patch

from common import Consts
from common.method import (
    _contains_key,
    calculate_vip_exp,
    dict_to_markdown,
    dict_to_slack_fields,
    format_reason,
    get_user_title,
    get_value,
    is_extend,
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

    def test_contains_key_found_nested(self):
        self.assertTrue(_contains_key({'a': {'b': 1}}, 'b'))

    def test_contains_key_not_found(self):
        self.assertFalse(_contains_key({'a': 1}, 'x'))

    def test_contains_key_in_list(self):
        self.assertTrue(_contains_key([{'a': 1}, {'b': 2}], 'b'))

    def test_contains_key_scalar_returns_false(self):
        self.assertFalse(_contains_key('string', 's'))

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
        reason = format_reason('slp场景', {'body': {'success': True}})
        self.assertIn('Depiction: slp场景', reason)

    def test_missing_body_defaults_to_empty(self):
        reason = format_reason('无body', {})
        self.assertIn('Depiction: 无body', reason)


class TestTitleLevel(unittest.TestCase):
    """爵位系数"""

    def test_known_levels(self):
        self.assertEqual(get_user_title(10), 1.0)    # 骑士
        self.assertEqual(get_user_title(40), 1.05)   # 伯爵
        self.assertEqual(get_user_title(90), 1.3)    # 皇帝

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


class TestGetImage(unittest.TestCase):
    """get_image 图片获取"""

    @patch('common.method.requests.get')
    def test_mode1_success(self, mock_get):
        """mode=1 成功时应返回 imageUrl"""
        from common.method import get_image
        mock_resp = Mock()
        mock_resp.json.return_value = {'code': 1, 'data': [{'imageUrl': 'http://img.test/1.jpg'}]}
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        result = get_image(mode=1)
        self.assertEqual(result, 'http://img.test/1.jpg')

    @patch('common.method.requests.get')
    def test_mode2_success(self, mock_get):
        """mode=2 成功时应返回第一个元素"""
        from common.method import get_image
        mock_resp = Mock()
        mock_resp.json.return_value = ['http://shibe.online/dog1.jpg']
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        result = get_image(mode=2)
        self.assertEqual(result, 'http://shibe.online/dog1.jpg')

    @patch('common.method.requests.get')
    def test_mode1_code_not_1(self, mock_get):
        """mode=1 但 code!=1 应返回 None"""
        from common.method import get_image
        mock_resp = Mock()
        mock_resp.json.return_value = {'code': 0, 'msg': 'error'}
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        result = get_image(mode=1)
        self.assertIsNone(result)

    def test_invalid_mode_returns_none(self):
        """无效 mode 应返回 None"""
        from common.method import get_image
        result = get_image(mode=999)
        self.assertIsNone(result)

    @patch('common.method.requests.get', side_effect=Exception('network error'))
    def test_request_exception_returns_none(self, mock_get):
        """请求异常应返回 None"""
        from common.method import get_image
        result = get_image(mode=2)
        self.assertIsNone(result)


class TestCheckPath(unittest.TestCase):
    """check_path 路径检查"""

    @patch('common.method.os.path.exists', return_value=True)
    def test_existing_path_no_error(self, mock_exists):
        """路径存在时不应抛异常"""
        from common.method import check_path
        check_path('/some/existing/path')  # 不抛异常

    @patch('Robot.robot')
    @patch('common.method.os.path.exists', return_value=False)
    def test_missing_path_raises(self, mock_exists, mock_robot):
        """路径不存在应抛 EnvironmentError"""
        from common.method import check_path
        with self.assertRaises(EnvironmentError):
            check_path('/some/missing/path')


class TestCalculateVipExpMoney(unittest.TestCase):
    """VIP 经验计算 money/coin 分支"""

    @patch('common.method.mysql')
    def test_money_with_title(self, mock_mysql):
        """money 类型且有爵位时应返回 pay_off * title"""
        mock_mysql.select_user_info_sql.return_value = 50  # 侯爵
        result = calculate_vip_exp('money', uid=111, pay_off=100)
        self.assertEqual(result, int(100 * 1.1))

    @patch('common.method.mysql')
    def test_coin_with_no_title(self, mock_mysql):
        """coin 类型但无爵位时应返回 0"""
        mock_mysql.select_user_info_sql.return_value = 999  # 不存在的等级
        result = calculate_vip_exp('coin', uid=111, pay_off=100)
        self.assertEqual(result, 0)


if __name__ == '__main__':
    unittest.main()
