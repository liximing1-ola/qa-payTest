# coding=utf-8
"""
common/Crazyspin.py、Greedy.py 单元测试

可在无后端环境下直接运行：
    python -m pytest tests/test_games.py -v
"""
import unittest
from unittest.mock import patch

from common.Crazyspin import (
    CrazySpin,
    DEFAULT_HEADERS,
    DEFAULT_PARAMS,
)
from common.Greedy import Greedy, MAX_RETRY_COUNT, RETRY_INTERVAL


class TestCrazySpinUrls(unittest.TestCase):
    """CrazySpin URL 与请求头构建"""

    def test_build_url_encodes_params(self):
        """_build_url 应拼接 host、endpoint 并 urlencode 参数"""
        url = CrazySpin._build_url('/go/party/turntable/list', {'rid': 1, '_blid': 100})
        self.assertIn('/go/party/turntable/list', url)
        self.assertIn('rid=1', url)
        self.assertIn('_blid=100', url)

    @patch('common.Crazyspin.Session.checkUserToken', return_value='tk')
    def test_build_headers_injects_token(self, mock_token):
        """_build_headers 应注入 token 且不改动 DEFAULT_HEADERS 原件"""
        headers = CrazySpin._build_headers('dev')
        self.assertEqual(headers['user-token'], 'tk')
        self.assertNotIn('user-token', DEFAULT_HEADERS)  # 原字典未被污染
        self.assertEqual(headers['Content-Type'], DEFAULT_HEADERS['Content-Type'])

    def test_spin_buy_url_contains_params(self):
        """spin_buy_url 应含 buy 端点与 uid"""
        url = CrazySpin.spin_buy_url(123)
        self.assertIn('pay/create', url)
        self.assertIn('_blid=123', url)

    def test_spin_play_url_contains_params(self):
        """spin_play_url 应含 draw 端点与 uid"""
        url = CrazySpin.spin_play_url(123)
        self.assertIn('/go/party/turntable/draw', url)
        self.assertIn('_blid=123', url)

    @patch('common.Crazyspin.Session.checkUserToken', return_value='tk')
    @patch('common.Crazyspin.requests.get')
    def test_get_turntable_list_passes_timeout(self, mock_get, _mock_token):
        """get_turntable_list 应带 timeout（防止网络挂起无限等待）"""
        CrazySpin.get_turntable_list(rid=1, uid=2)
        self.assertIn('timeout', mock_get.call_args[1])
        self.assertGreater(mock_get.call_args[1]['timeout'], 0)

    @patch('common.Crazyspin.Session.checkUserToken', return_value='tk')
    @patch('common.Crazyspin.requests.get')
    def test_get_turntable_horn_passes_timeout(self, mock_get, _mock_token):
        """get_turntable_horn 应带 timeout"""
        CrazySpin.get_turntable_horn(uid=2)
        self.assertIn('timeout', mock_get.call_args[1])
        self.assertGreater(mock_get.call_args[1]['timeout'], 0)

    def test_default_params_immutable_usage(self):
        """默认参数应被复制而非原地修改（** 展开构造新 dict）"""
        before = dict(DEFAULT_PARAMS)
        CrazySpin.spin_buy_url(1)
        self.assertEqual(DEFAULT_PARAMS, before)


class TestGreedyWait(unittest.TestCase):
    """Greedy 等待逻辑"""

    def test_retry_params_readable_from_env(self):
        """重试参数默认为 10 次 / 5 秒，可被环境变量覆盖（此处仅校验类型与默认值）"""
        self.assertIsInstance(MAX_RETRY_COUNT, int)
        self.assertIsInstance(RETRY_INTERVAL, int)
        self.assertGreaterEqual(MAX_RETRY_COUNT, 1)
        self.assertGreaterEqual(RETRY_INTERVAL, 0)

    @patch('common.Greedy.time.sleep')
    @patch('common.Greedy.Greedy.index')
    def test_wait_for_state_retries_until_match(self, mock_index, mock_sleep):
        """状态不符时应按 RETRY_INTERVAL 间隔重试，命中即返回"""
        state_body = {'data': {'state': '1', 'round_id': 99, 'counter_range': 3}}
        mismatch_body = {'data': {'state': '0', 'round_id': 1, 'counter_range': 0}}
        mock_index.side_effect = [
            {'body': mismatch_body}, {'body': mismatch_body}, {'body': state_body},
        ]
        round_id, counter = Greedy._wait_for_state(105, target_state='1')
        self.assertEqual(round_id, 99)
        self.assertEqual(counter, 3)
        self.assertEqual(mock_index.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch('common.Greedy.time.sleep')
    @patch('common.Greedy.Greedy.index')
    def test_wait_for_state_exhausted_returns_none(self, mock_index, mock_sleep):
        """始终不匹配时应重试 MAX_RETRY_COUNT 次后返回 (None, None)"""
        mock_index.return_value = {'body': {'data': {'state': '0'}}}
        round_id, counter = Greedy._wait_for_state(105, target_state='1')
        self.assertIsNone(round_id)
        self.assertIsNone(counter)
        self.assertEqual(mock_index.call_count, MAX_RETRY_COUNT)

    @patch('common.Greedy.time.sleep')
    @patch('common.Greedy.conMysql.select_greedy_prize')
    def test_wait_for_prize_returns_on_data(self, mock_prize, mock_sleep):
        """有开奖数据时应立即返回，不再 sleep"""
        mock_prize.return_value = (30, 1200)
        counter_all, prize = Greedy._wait_for_prize(105, round_id=7)
        self.assertEqual(counter_all, 30)
        self.assertEqual(prize, 1200)
        mock_sleep.assert_not_called()

    @patch('common.Greedy.time.sleep')
    @patch('common.Greedy.conMysql.select_greedy_prize')
    def test_wait_for_prize_exhausted_returns_zero(self, mock_prize, mock_sleep):
        """始终无数据时应重试 MAX_RETRY_COUNT 次后返回 (0, 0)"""
        mock_prize.return_value = (0, 0)
        counter_all, prize = Greedy._wait_for_prize(105, round_id=7)
        self.assertEqual(counter_all, 0)
        self.assertEqual(prize, 0)
        self.assertEqual(mock_prize.call_count, MAX_RETRY_COUNT)


if __name__ == '__main__':
    unittest.main()
