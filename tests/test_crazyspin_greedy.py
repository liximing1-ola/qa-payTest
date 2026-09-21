# coding=utf-8
"""
common/Crazyspin.py 与 common/Greedy.py 单元测试（URL 构建 / 请求透传 / 轮询流程）

全部 mock Session 与请求/DB 依赖，可在无后端环境下直接运行：
    python -m pytest tests/test_crazyspin_greedy.py -v
"""
import unittest
from unittest.mock import Mock, patch

from common.Config import config
from common.Crazyspin import DEFAULT_PARAMS, CrazySpin
from common.Greedy import BET_COUNT, MAX_RETRY_COUNT, Greedy


class TestCrazySpinUrls(unittest.TestCase):
    """CrazySpin URL 构建"""

    def test_build_url(self):
        url = CrazySpin._build_url('pay/create', {'a': 1, 'b': 'x'})
        self.assertTrue(url.startswith(config.oversea_host + 'pay/create?'))
        self.assertIn('a=1', url)
        self.assertIn('b=x', url)

    def test_spin_buy_url(self):
        """购买 URL 应带 uid 与固定签名参数"""
        url = CrazySpin.spin_buy_url(800350557)
        self.assertIn('pay/create', url)
        self.assertIn('_blid=800350557', url)
        self.assertIn('_sign=', url)
        self.assertIn('package=' + DEFAULT_PARAMS['package'], url)

    def test_spin_play_url(self):
        """抽奖 URL 应指向 turntable/draw 端点"""
        url = CrazySpin.spin_play_url(800350557)
        self.assertIn('/go/party/turntable/draw', url)
        self.assertIn('_blid=800350557', url)


class TestCrazySpinRequests(unittest.TestCase):
    """CrazySpin GET 请求透传"""

    def test_build_headers_injects_token(self):
        """请求头应注入 user-token 并保留默认 UA/Content-Type"""
        with patch('common.Crazyspin.Session.checkUserToken',
                   return_value='tok') as m:
            headers = CrazySpin._build_headers('app')
        self.assertEqual(headers['user-token'], 'tok')
        self.assertIn('User-Agent', headers)
        m.assert_called_once_with(operate='read', app_name='app')

    def test_get_turntable_list(self):
        """list 接口应带 rid 参数与 token 头"""
        resp = Mock()
        with patch('common.Crazyspin.Session.checkUserToken',
                   return_value='tok'), \
                patch('common.Crazyspin.requests.get', return_value=resp) as m:
            res = CrazySpin.get_turntable_list(999, 800350557, token_name='app')
        self.assertIs(res, resp)
        url = m.call_args[1]['params']
        self.assertIn('/go/party/turntable/list', m.call_args[0][0])
        self.assertEqual(url['rid'], 999)
        self.assertEqual(url['_blid'], 800350557)
        self.assertEqual(m.call_args[1]['headers']['user-token'], 'tok')


class TestGreedyRequests(unittest.TestCase):
    """Greedy URL 与请求透传"""

    def test_build_url(self):
        url = Greedy._build_url('greedy/index', 5)
        self.assertEqual(url, f"{config.oversea_host}greedy/index?uid=5")

    def test_index_forwards(self):
        """index 应向正确 URL 发空 data 并用 app token"""
        with patch('common.Greedy.post_request_session') as m:
            Greedy.index(5)
        m.assert_called_once_with(
            f"{config.oversea_host}greedy/index?uid=5", None, token_name='app')

    def test_stake_forwards_params(self):
        with patch('common.Greedy.post_request_session') as m:
            Greedy.stake(5, vid=3, counter=9, round_id=7,
                         money_type='bean', notice=False)
        url, params = m.call_args[0][0], m.call_args[0][1]
        self.assertIn('greedy/stake', url)
        self.assertEqual(params, {'vid': 3, 'counter': 9, 'round_id': 7,
                                  'money_type': 'bean', 'notice': False})


class TestGreedyPolling(unittest.TestCase):
    """Greedy 轮询与下注流程"""

    def test_wait_for_state_matched(self):
        """状态命中应立即返回 (round_id, counter_range)"""
        with patch.object(Greedy, 'index', return_value={
                'body': {'data': {'state': '1', 'round_id': 5,
                                  'counter_range': 9}}}) as m:
            res = Greedy._wait_for_state(5)
        self.assertEqual(res, (5, 9))
        self.assertEqual(m.call_count, 1)

    def test_wait_for_state_timeout(self):
        """状态始终不匹配应重试满次数并返回 (None, None)"""
        with patch.object(Greedy, 'index', return_value={
                'body': {'data': {'state': '0'}}}), \
                patch('common.Greedy.time.sleep') as m_sleep:
            res = Greedy._wait_for_state(5)
        self.assertEqual(res, (None, None))
        self.assertEqual(m_sleep.call_count, MAX_RETRY_COUNT)

    def test_wait_for_prize_matched(self):
        with patch('common.Greedy.conMysql.select_greedy_prize',
                   return_value=(100, 50)) as m:
            res = Greedy._wait_for_prize(5, 7)
        self.assertEqual(res, (100, 50))
        m.assert_called_once_with(5, 7)

    def test_wait_for_prize_timeout(self):
        """无数据（返回 (0,0)）应重试满次数并返回 (0, 0)"""
        with patch('common.Greedy.conMysql.select_greedy_prize',
                   return_value=(0, 0)), \
                patch('common.Greedy.time.sleep'):
            res = Greedy._wait_for_prize(5, 7)
        self.assertEqual(res, (0, 0))

    def test_bet_no_round_returns_zero(self):
        """等不到可投注回合应返回 [0, 0]"""
        with patch.object(Greedy, '_wait_for_state',
                          return_value=(None, None)):
            self.assertEqual(Greedy.bet('bean'), [0, 0])

    def test_bet_full_flow(self):
        """正常流程应下注 BET_COUNT 次并返回开奖结果"""
        with patch.object(Greedy, '_wait_for_state',
                          return_value=(5, 9)), \
                patch.object(Greedy, '_wait_for_prize',
                             return_value=(100, 50)) as m_prize, \
                patch.object(Greedy, 'stake') as m_stake:
            res = Greedy.bet('bean')
        self.assertEqual(res, [100, 50])
        self.assertEqual(m_stake.call_count, BET_COUNT)
        m_prize.assert_called_once()


if __name__ == '__main__':
    unittest.main()
