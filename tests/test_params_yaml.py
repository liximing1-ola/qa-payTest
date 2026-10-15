"""
common/params_yaml.py 单元测试

全部 mock 文件系统，可在无外部依赖下直接运行：
    python -m pytest tests/test_params_yaml.py -v
"""
import unittest
from unittest.mock import mock_open, patch

from common.params_yaml import YamlReader, _yaml_cache


def _patch_yaml_read(yaml_data):
    """返回一组 patch：config + exists + builtins.open + yaml.safe_load"""
    return (
        patch('common.params_yaml.config'),
        patch('common.params_yaml.os.path.exists', return_value=True),
        patch('common.params_yaml.open', mock_open()),
        patch('common.params_yaml.yaml')
    )


class TestYamlReader(unittest.TestCase):
    """YamlReader.read"""

    def setUp(self):
        _yaml_cache.clear()

    def tearDown(self):
        _yaml_cache.clear()

    @patch('common.params_yaml.config')
    def test_get_yaml_path(self, mock_config):
        """_get_yaml_path 应拼接 BASE_PATH + common + filename"""
        mock_config.BASE_PATH = '/app'
        path = YamlReader._get_yaml_path('Basic.yml')
        self.assertTrue(path.endswith('Basic.yml'))
        self.assertIn('common', path)

    @patch('common.params_yaml.yaml')
    @patch('common.params_yaml.open', mock_open())
    @patch('common.params_yaml.os.path.exists', return_value=True)
    @patch('common.params_yaml.config')
    def test_read_returns_value(self, mock_config, mock_exists, mock_yaml):
        """正常读取应返回 key 对应的值"""
        mock_config.BASE_PATH = '/app'
        mock_yaml.safe_load.return_value = {'key1': 'value1', 'key2': 42}

        result = YamlReader.read('Basic.yml', 'key1')
        self.assertEqual(result, 'value1')

    @patch('common.params_yaml.yaml')
    @patch('common.params_yaml.open', mock_open())
    @patch('common.params_yaml.os.path.exists', return_value=True)
    @patch('common.params_yaml.config')
    def test_read_missing_key_returns_none(self, mock_config, mock_exists, mock_yaml):
        """key 不存在应返回 None"""
        mock_config.BASE_PATH = '/app'
        mock_yaml.safe_load.return_value = {'key1': 'value1'}

        result = YamlReader.read('Basic.yml', 'not_exist')
        self.assertIsNone(result)

    @patch('common.params_yaml.os.path.exists', return_value=False)
    @patch('common.params_yaml.config')
    def test_read_file_not_found_returns_none(self, mock_config, mock_exists):
        """文件不存在应返回 None"""
        mock_config.BASE_PATH = '/app'
        result = YamlReader.read('missing.yml', 'key1')
        self.assertIsNone(result)

    @patch('common.params_yaml.yaml')
    @patch('common.params_yaml.open', mock_open())
    @patch('common.params_yaml.os.path.exists', return_value=True)
    @patch('common.params_yaml.config')
    def test_read_empty_yaml_returns_none(self, mock_config, mock_exists, mock_yaml):
        """空 YAML 文件应返回 None"""
        mock_config.BASE_PATH = '/app'
        mock_yaml.safe_load.return_value = None

        result = YamlReader.read('empty.yml', 'key1')
        self.assertIsNone(result)

    @patch('common.params_yaml.yaml')
    @patch('common.params_yaml.os.path.exists', return_value=True)
    @patch('common.params_yaml.config')
    def test_read_exception_returns_none(self, mock_config, mock_exists, mock_yaml):
        """解析异常应返回 None"""
        mock_config.BASE_PATH = '/app'
        mock_yaml.safe_load.side_effect = Exception('parse error')

        result = YamlReader.read('bad.yml', 'key1')
        self.assertIsNone(result)

    @patch('common.params_yaml.yaml')
    @patch('common.params_yaml.open', mock_open())
    @patch('common.params_yaml.os.path.exists', return_value=True)
    @patch('common.params_yaml.config')
    def test_read_uses_cache(self, mock_config, mock_exists, mock_yaml):
        """第二次读取应使用缓存，不再打开文件"""
        mock_config.BASE_PATH = '/app'
        mock_yaml.safe_load.return_value = {'k': 'v'}

        YamlReader.read('cached.yml', 'k')
        YamlReader.read('cached.yml', 'k')
        # safe_load 只应被调用一次
        mock_yaml.safe_load.assert_called_once()

    @patch('common.params_yaml.yaml')
    @patch('common.params_yaml.open', mock_open())
    @patch('common.params_yaml.os.path.exists', return_value=True)
    @patch('common.params_yaml.config')
    def test_read_cache_missing_key(self, mock_config, mock_exists, mock_yaml):
        """缓存命中但 key 不存在应返回 None"""
        mock_config.BASE_PATH = '/app'
        mock_yaml.safe_load.return_value = {'k': 'v'}

        YamlReader.read('cached.yml', 'k')
        result = YamlReader.read('cached.yml', 'missing')
        self.assertIsNone(result)


class TestYamlAlias(unittest.TestCase):
    """向后兼容别名"""

    def test_yaml_alias(self):
        """Yaml 应指向 YamlReader"""
        from common.params_yaml import Yaml
        self.assertIs(Yaml, YamlReader)


if __name__ == '__main__':
    unittest.main()
