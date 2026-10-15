"""
common/Session.py 单元测试（会话管理）

全部 mock 外部依赖（requests、文件操作、数据库），可在无后端环境下直接运行：
    python -m pytest tests/test_session.py -v
"""
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch


class TestGetSession(unittest.TestCase):
    """getSession 的环境路由"""

    def test_release_returns_none(self):
        """release 环境应直接返回 None"""
        from common.session import Session
        result = Session.get_session('release')
        self.assertIsNone(result)

    def test_unknown_env_returns_none(self):
        """未知环境应返回 None"""
        from common.session import Session
        result = Session.get_session('nonexistent_env_xyz')
        self.assertIsNone(result)

    @patch.object(__import__('common.session', fromlist=['Session']).Session, '_login')
    @patch.object(__import__('common.session', fromlist=['Session']).Session, '_handle_response')
    def test_dev_env_routes_correctly(self, mock_handle, mock_login):
        """dev 环境应走 _login -> _handle_response 流程"""
        from common.session import Session
        mock_login.return_value = {'success': True, 'data': {'token': 'abc', 'uid': 1}}
        mock_handle.return_value = {'token': 'abc', 'uid': 1}

        result = Session.get_session('dev')
        self.assertIsNotNone(result)
        mock_login.assert_called_once()
        mock_handle.assert_called_once()

    @patch.object(__import__('common.session', fromlist=['Session']).Session, '_login',
                  side_effect=Exception('network error'))
    def test_dev_backup_plan_on_failure(self, mock_login):
        """dev 环境登录失败时应触发备选方案（use_backup=True）"""
        from common.session import Session
        with patch.object(Session, '_use_backup_plan', return_value={'token': 'backup'}) as mock_backup:
            result = Session.get_session('dev')
        self.assertEqual(result, {'token': 'backup'})
        mock_backup.assert_called_once()

    @patch.object(__import__('common.session', fromlist=['Session']).Session, '_login',
                  side_effect=Exception('network error'))
    def test_rush_no_backup_on_failure(self, mock_login):
        """rush 环境失败时不应触发备选方案（use_backup=False）"""
        from common.session import Session
        with patch.object(Session, '_use_backup_plan') as mock_backup:
            result = Session.get_session('rush')
        self.assertIsNone(result)
        mock_backup.assert_not_called()


class TestLogin(unittest.TestCase):
    """_login 的请求构建"""

    @patch('common.session.requests.session')
    @patch('common.session.Yaml.read')
    def test_login_builds_request(self, mock_yaml, mock_session_factory):
        """_login 应正确构建 URL 和请求参数"""
        from common.session import Session

        mock_yaml.side_effect = [
            {'Content-Type': 'application/json'},  # headers
            'param1=value1',                        # params
            {'username': 'test', 'password': '123'}  # body
        ]
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {'success': True, 'data': {'token': 't', 'uid': 1}}
        mock_session.post.return_value = mock_response
        mock_session_factory.return_value = mock_session

        env_config = {
            'headers_key': 'header_dev',
            'params_key': 'params_dev_qq',
            'body_key': 'data_dev_qq',
            'package': 'com.test.pkg',
            'login_url': 'https://example.com/login',
        }
        result = Session._login(env_config, 'dev')

        self.assertEqual(result['success'], True)
        # 验证 URL 拼接了 params 和 package
        call_url = mock_session.post.call_args[0][0]
        self.assertIn('param1=value1', call_url)
        self.assertIn('package=com.test.pkg', call_url)


class TestHandleResponse(unittest.TestCase):
    """_handle_response 的成功/失败分支"""

    @patch('common.session.Session.check_user_token')
    def test_success_response(self, mock_check):
        """成功响应应返回 token 和 uid"""
        from common.session import Session
        res = {'success': True, 'data': {'token': 'abc', 'uid': 42}}
        result = Session._handle_response(res, 'dev')
        self.assertEqual(result, {'token': 'abc', 'uid': 42})
        mock_check.assert_called_once_with('write', app_name='dev', token='abc')

    def test_failed_response_no_success(self):
        """success=False 时应返回 None"""
        from common.session import Session
        res = {'success': False, 'msg': 'login failed'}
        result = Session._handle_response(res, 'dev')
        self.assertIsNone(result)

    def test_failed_response_no_token(self):
        """data 中无 token 时应返回 None"""
        from common.session import Session
        res = {'success': True, 'data': {'uid': 42}}
        result = Session._handle_response(res, 'dev')
        self.assertIsNone(result)

    def test_failed_response_no_data(self):
        """无 data 字段时应返回 None"""
        from common.session import Session
        res = {'success': True}
        result = Session._handle_response(res, 'dev')
        self.assertIsNone(result)


class TestUseBackupPlan(unittest.TestCase):
    """_use_backup_plan 的备选方案触发"""

    @patch('common.session.Session.check_user_token')
    def test_backup_plan_flow(self, mock_check):
        """备选方案应从数据库获取 salt 并生成 token"""
        import os
        from unittest.mock import patch as _patch
        # get_token.py 模块级需要环境变量
        with _patch.dict(os.environ, {'TOKEN_KEY': 'test', 'TOKEN_VERIFY_SALT': 'test'}):
            import importlib

            import common.get_token as gt
            importlib.reload(gt)
            with _patch('common.con_mysql.ConMysql.select_user_info_sql', return_value='salt_value'), \
                 _patch.object(gt.TokenGenerator, 'generate', return_value='backup_token'):
                from common.session import Session
                result = Session._use_backup_plan('dev', 'main plan failed')

        self.assertEqual(result, {'token': 'backup_token'})
        mock_check.assert_called_once_with('write', app_name='dev', token='backup_token')


class TestCheckUserToken(unittest.TestCase):
    """checkUserToken 的读写操作"""

    def setUp(self):
        """创建临时目录用于文件操作"""
        self._temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理临时文件"""
        import shutil
        shutil.rmtree(self._temp_dir, ignore_errors=True)

    @patch('common.session.os.path.realpath')
    @patch('common.session.os.path.split')
    def test_write_and_read_token(self, mock_split, mock_realpath):
        """写入后读取应返回相同 token"""
        from common.session import Session
        mock_realpath.return_value = os.path.join(self._temp_dir, 'Session.py')
        mock_split.return_value = (self._temp_dir, 'Session.py')

        # 写入
        Session.check_user_token('write', app_name='test_env', token='my_token_123')
        # 读取
        result = Session.check_user_token('read', app_name='test_env')
        self.assertEqual(result, 'my_token_123')

    @patch('common.session.os.path.realpath')
    @patch('common.session.os.path.split')
    def test_read_empty_file_raises(self, mock_split, mock_realpath):
        """读取空文件应抛异常"""
        from common.session import Session
        mock_realpath.return_value = os.path.join(self._temp_dir, 'Session.py')
        mock_split.return_value = (self._temp_dir, 'Session.py')

        # 先创建空文件
        Session.check_user_token('write', app_name='empty_env', token='')
        # 读取空文件应抛异常
        with self.assertRaises(Exception) as ctx:
            Session.check_user_token('read', app_name='empty_env')
        self.assertIn('为空', str(ctx.exception))

    @patch('common.session.os.path.realpath')
    @patch('common.session.os.path.split')
    def test_write_with_uid(self, mock_split, mock_realpath):
        """带 uid 的文件名应包含 uid"""
        from common.session import Session
        mock_realpath.return_value = os.path.join(self._temp_dir, 'Session.py')
        mock_split.return_value = (self._temp_dir, 'Session.py')

        Session.check_user_token('write', app_name='dev', token='tok', uid=123)
        result = Session.check_user_token('read', app_name='dev', uid=123)
        self.assertEqual(result, 'tok')

    @patch('common.session.os.path.realpath')
    @patch('common.session.os.path.split')
    def test_creates_file_if_not_exists(self, mock_split, mock_realpath):
        """文件不存在时应自动创建"""
        from common.session import Session
        mock_realpath.return_value = os.path.join(self._temp_dir, 'Session.py')
        mock_split.return_value = (self._temp_dir, 'Session.py')

        # 确保文件不存在
        txt_path = os.path.join(self._temp_dir, 'new_envUserToken.txt')
        self.assertFalse(os.path.exists(txt_path))

        Session.check_user_token('write', app_name='new_env', token='hello')
        self.assertTrue(os.path.exists(txt_path))


if __name__ == '__main__':
    unittest.main()
