"""
common/Request.py 单元测试

可在无后端环境下直接运行：
    python -m pytest tests/test_request.py -v
"""
import unittest
from unittest.mock import Mock, patch

import requests

from common.request_util import (
    DEFAULT_TIMEOUT,
    VERIFY_SSL,
    _build_headers,
    _ensure_https,
    _parse_response,
    post_request_session,
    post_request_session_starify,
    post_starify,
)


def _make_response(ok=True, status_code=200, json_data=None, json_raises=False,
                   text='<html>gateway error</html>', elapsed_seconds=0.25):
    """构造 mock Response 对象"""
    elapsed = Mock()
    elapsed.total_seconds.return_value = elapsed_seconds
    resp = Mock()
    resp.ok = ok
    resp.status_code = status_code
    resp.elapsed = elapsed
    resp.text = text
    if json_raises:
        resp.json.side_effect = ValueError('No JSON object could be decoded')
    else:
        resp.json.return_value = json_data
    return resp


class TestParseResponse(unittest.TestCase):
    """_parse_response"""

    def test_json_success(self):
        """200 + JSON：body 应为解析结果，无 error 键"""
        resp = _make_response(ok=True, status_code=200, json_data={'success': 1})
        result = _parse_response(resp)
        self.assertEqual(result['code'], 200)
        self.assertEqual(result['body'], {'success': 1})
        self.assertEqual(result['time_consuming'], 250.0)
        self.assertEqual(result['time_total'], 0.25)
        self.assertNotIn('error', result)

    def test_non_json_success(self):
        """200 但非 JSON：body 应为 None 并附 error 标记"""
        resp = _make_response(ok=True, status_code=200, json_raises=True)
        result = _parse_response(resp)
        self.assertEqual(result['code'], 200)
        self.assertIsNone(result['body'])
        self.assertEqual(result['error'], 'non-json response')
        self.assertEqual(result['time_consuming'], 250.0)

    def test_http_error_status(self):
        """非 2xx：body 为 None、无 error 键（请求本身送达了）"""
        resp = _make_response(ok=False, status_code=502, text='<html>Bad Gateway</html>')
        result = _parse_response(resp)
        self.assertEqual(result['code'], 502)
        self.assertIsNone(result['body'])
        self.assertNotIn('error', result)


class TestBuildHeaders(unittest.TestCase):
    """_build_headers"""

    @patch('common.request_util.Session.check_user_token', return_value='token-abc')
    def test_token_injected(self, mock_token):
        """token 应写入 user-token 头"""
        headers = _build_headers('app')
        self.assertEqual(headers['user-token'], 'token-abc')
        mock_token.assert_called_once_with(operate='read', app_name='app', uid=None)

    @patch('common.request_util.Session.check_user_token', return_value='token-uid')
    def test_uid_forwarded(self, mock_token):
        """uid 应透传到 checkUserToken"""
        _build_headers('starify', uid=124458)
        mock_token.assert_called_once_with(operate='read', app_name='starify', uid=124458)

    @patch('common.request_util.Session.check_user_token', return_value='t')
    def test_default_headers_preserved(self, _mock_token):
        """默认 UA / Content-Type 应保留"""
        headers = _build_headers()
        self.assertIn('User-Agent', headers)
        self.assertEqual(headers['Content-Type'], 'application/x-www-form-urlencoded')


class TestEnsureHttps(unittest.TestCase):
    """_ensure_https"""

    def test_https_unchanged(self):
        """https URL 应保持不变"""
        self.assertEqual(_ensure_https('https://a.b/c'), 'https://a.b/c')

    def test_http_upgraded(self):
        """http URL 应升级为 https"""
        self.assertEqual(_ensure_https('http://a.b/c'), 'https://a.b/c')

    def test_bare_host_prefixed(self):
        """裸主机名应补 https:// 前缀"""
        self.assertEqual(_ensure_https('a.b/c'), 'https://a.b/c')


class TestPostRequestSession(unittest.TestCase):
    """post_request_session"""

    @patch('common.request_util.Session.check_user_token', return_value='t')
    @patch('common.request_util.requests.post')
    def test_normal_flow(self, mock_post, _mock_token):
        """正常请求：返回解析结果，URL 升级 https、带 timeout 与 verify 开关"""
        mock_post.return_value = _make_response(json_data={'success': 1})
        result = post_request_session('http://x.y/z', 'a=b', token_name='dev')
        self.assertEqual(result['body'], {'success': 1})
        self.assertEqual(result['code'], 200)

        kwargs = mock_post.call_args[1]
        self.assertEqual(kwargs['url'], 'https://x.y/z')
        self.assertEqual(kwargs['data'], 'a=b')
        self.assertEqual(kwargs['timeout'], DEFAULT_TIMEOUT)
        self.assertEqual(kwargs['verify'], VERIFY_SSL)
        self.assertEqual(kwargs['headers']['user-token'], 't')

    @patch('common.request_util.Session.check_user_token', return_value='t')
    @patch('common.request_util.requests.post', side_effect=requests.Timeout('boom'))
    def test_timeout_returns_error_code(self, _mock_post, _mock_token):
        """请求超时应返回 code=-1 与 error 说明"""
        result = post_request_session('http://x.y/z', None)
        self.assertEqual(result['code'], -1)
        self.assertIn('error', result)
        self.assertEqual(result['body'], '')

    @patch('common.request_util.Session.check_user_token', return_value='t')
    @patch('common.request_util.requests.post', side_effect=RuntimeError('boom'))
    def test_unexpected_error_returns_error_code(self, _mock_post, _mock_token):
        """非 requests 异常也应返回 code=-1 而非向上抛出"""
        result = post_request_session('http://x.y/z', None)
        self.assertEqual(result['code'], -1)
        self.assertIn('error', result)

    @patch('common.request_util.Session.check_user_token', return_value='t')
    @patch('common.request_util.requests.post')
    def test_custom_timeout_forwarded(self, mock_post, _mock_token):
        """自定义 timeout 应传递到 requests.post"""
        mock_post.return_value = _make_response(json_data={})
        post_request_session('http://x.y/z', None, timeout=5.0)
        self.assertEqual(mock_post.call_args[1]['timeout'], 5.0)


class TestPostRequestSessionStarify(unittest.TestCase):
    """post_request_session_starify"""

    @patch('common.request_util.post_request_session', return_value={'code': 200, 'body': {}})
    @patch('common.request_util.Session.check_user_token')
    def test_with_uid(self, mock_token, mock_post):
        """指定 uid 时应先检查 token 文件"""
        result = post_request_session_starify('http://x.y/z', 'data', uid=123)
        mock_token.assert_called_once_with(operate='read', app_name='starify', uid=123)
        self.assertEqual(result['code'], 200)

    @patch('common.request_util.post_request_session', return_value={'code': 200, 'body': {}})
    def test_without_uid(self, mock_post):
        """不指定 uid 时应直接转发"""
        result = post_request_session_starify('http://x.y/z', 'data')
        self.assertEqual(result['code'], 200)


class TestPostStarify(unittest.TestCase):
    """post_starify"""

    @patch('common.request_util.post_request_session_starify', return_value={'code': 200, 'body': {}})
    def test_delegates_to_starify_session(self, mock_starify):
        """应使用 config.starify_pay_url 和 starify token"""
        from common.Config import config
        result = post_starify('data', uid=123, timeout=10)
        mock_starify.assert_called_once_with(
            config.starify_pay_url, 'data',
            token_name='starify', uid=123, timeout=10
        )
        self.assertEqual(result['code'], 200)


if __name__ == '__main__':
    unittest.main()
