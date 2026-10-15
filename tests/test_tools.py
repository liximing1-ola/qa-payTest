"""
common/tools.py 单元测试

可在无后端环境下直接运行：
    python -m pytest tests/test_tools.py -v
"""
import unittest
from unittest.mock import patch

from common.tools import deal_num, hash_key


class TestHashKey(unittest.TestCase):
    """hash_key"""

    @patch('common.tools.time')
    def test_returns_md5_hex_string(self, mock_time):
        """应返回 32 位 MD5 hex 字符串"""
        mock_time.time.return_value = 1700000000.0
        result = hash_key()
        self.assertEqual(len(result), 32)
        self.assertTrue(all(c in '0123456789abcdef' for c in result))

    @patch('common.tools.time')
    def test_same_timestamp_same_result(self, mock_time):
        """相同时间戳应产生相同结果"""
        mock_time.time.return_value = 1700000000.0
        self.assertEqual(hash_key(), hash_key())

    @patch('common.tools.time')
    def test_different_timestamp_different_result(self, mock_time):
        """不同时间戳应产生不同结果"""
        mock_time.time.return_value = 1700000000.0
        r1 = hash_key()
        mock_time.time.return_value = 1700000001.0
        r2 = hash_key()
        self.assertNotEqual(r1, r2)


class TestDealNum(unittest.TestCase):
    """deal_num"""

    def test_integer_unchanged(self):
        """整数应保持不变"""
        self.assertEqual(deal_num(5), 5)
        self.assertEqual(deal_num(0), 0)

    def test_decimal_rounds_up(self):
        """有小数部分时应向上取整（保留2位小数后）"""
        self.assertEqual(deal_num(1.5), 2)
        self.assertEqual(deal_num(0.01), 1)
        self.assertEqual(deal_num(2.1), 3)

    def test_exact_integer_after_rounding(self):
        """保留2位小数后为整数的应不变"""
        self.assertEqual(deal_num(3.00), 3)
        self.assertEqual(deal_num(3.004), 3)  # round(3.004, 2) = 3.0

    def test_negative_number(self):
        """负数向上取整趋向零"""
        self.assertEqual(deal_num(-1.5), -1)
        self.assertEqual(deal_num(-2.01), -2)


if __name__ == '__main__':
    unittest.main()
