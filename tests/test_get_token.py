# coding=utf-8
"""
common/getToken.py 单元测试（Token 生成器）

由于 getToken.py 在模块级读取环境变量，测试需要：
1. 在 import 前设置环境变量 TOKEN_KEY 和 TOKEN_VERIFY_SALT
2. 使用 importlib.reload 重新加载模块

可在无后端环境下直接运行：
    python -m pytest tests/test_get_token.py -v
"""
import hashlib
import importlib
import os
import unittest
from unittest.mock import patch


class TestTokenGenerator(unittest.TestCase):
    """TokenGenerator 功能测试"""

    @classmethod
    def setUpClass(cls):
        """确保环境变量已设置后 reload 模块"""
        cls.env_patch = patch.dict(os.environ, {
            'TOKEN_KEY': 'test_key_12345678901234567890',
            'TOKEN_VERIFY_SALT': 'test_salt_abcdef'
        })
        cls.env_patch.start()

        # 确保模块已加载
        import common.get_token as gt
        importlib.reload(gt)
        cls.gt = gt

    @classmethod
    def tearDownClass(cls):
        cls.env_patch.stop()

    def test_token_generation_not_empty(self):
        """生成的 token 应非空且为字符串"""
        salt = self.gt.TokenGenerator.generate_salt()
        gen = self.gt.TokenGenerator(uid=100287189, salt=salt)
        token = gen.generate()
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)

    def test_token_generation_unique(self):
        """不同 uid 应生成不同 token"""
        salt1 = self.gt.TokenGenerator.generate_salt()
        salt2 = self.gt.TokenGenerator.generate_salt()
        gen1 = self.gt.TokenGenerator(uid=100287189, salt=salt1)
        gen2 = self.gt.TokenGenerator(uid=10079678, salt=salt2)
        token1 = gen1.generate()
        token2 = gen2.generate()
        # 由于 salt 和时间戳不同，token 应不同
        self.assertNotEqual(token1, token2)


class TestGenerateSalt(unittest.TestCase):
    """generate_salt 长度和字符集"""

    @classmethod
    def setUpClass(cls):
        cls.env_patch = patch.dict(os.environ, {
            'TOKEN_KEY': 'test_key_for_salt',
            'TOKEN_VERIFY_SALT': 'test_salt_for_salt'
        })
        cls.env_patch.start()
        import common.get_token as gt
        importlib.reload(gt)
        cls.gt = gt

    @classmethod
    def tearDownClass(cls):
        cls.env_patch.stop()

    def test_salt_length(self):
        """盐值长度应为 10"""
        salt = self.gt.TokenGenerator.generate_salt()
        self.assertEqual(len(salt), 10)

    def test_salt_characters(self):
        """盐值应仅包含 CHARS 字符集（数字+小写字母）"""
        salt = self.gt.TokenGenerator.generate_salt()
        allowed = set(self.gt.CHARS)
        for ch in salt:
            self.assertIn(ch, allowed)

    def test_salt_randomness(self):
        """多次生成的盐值应不同"""
        salts = {self.gt.TokenGenerator.generate_salt() for _ in range(10)}
        # 10次生成应至少有2个不同值（概率极高）
        self.assertGreater(len(salts), 1)


class TestMd5(unittest.TestCase):
    """_md5 摘要正确性"""

    @classmethod
    def setUpClass(cls):
        cls.env_patch = patch.dict(os.environ, {
            'TOKEN_KEY': 'test_key_md5',
            'TOKEN_VERIFY_SALT': 'test_salt_md5'
        })
        cls.env_patch.start()
        import common.get_token as gt
        importlib.reload(gt)
        cls.gt = gt

    @classmethod
    def tearDownClass(cls):
        cls.env_patch.stop()

    def test_md5_correctness(self):
        """_md5 结果应与 hashlib.md5 直接计算一致"""
        test_string = 'hello_world'
        expected = hashlib.md5(test_string.encode('utf-8')).hexdigest()
        result = self.gt.TokenGenerator._md5(test_string)
        self.assertEqual(result, expected)

    def test_md5_empty_string(self):
        """空字符串的 MD5 应正确"""
        expected = hashlib.md5(b'').hexdigest()
        result = self.gt.TokenGenerator._md5('')
        self.assertEqual(result, expected)

    def test_md5_chinese(self):
        """中文字符串的 MD5 应正确"""
        test_string = '测试中文'
        expected = hashlib.md5(test_string.encode('utf-8')).hexdigest()
        result = self.gt.TokenGenerator._md5(test_string)
        self.assertEqual(result, expected)


class TestPhpMicrotime(unittest.TestCase):
    """_php_microtime 格式正确性"""

    @classmethod
    def setUpClass(cls):
        cls.env_patch = patch.dict(os.environ, {
            'TOKEN_KEY': 'test_key_mtime',
            'TOKEN_VERIFY_SALT': 'test_salt_mtime'
        })
        cls.env_patch.start()
        import common.get_token as gt
        importlib.reload(gt)
        cls.gt = gt

    @classmethod
    def tearDownClass(cls):
        cls.env_patch.stop()

    def test_microtime_format(self):
        """microtime 格式应为 '0.xxxxxxxxx xxxxxxxxxx'"""
        result = self.gt.TokenGenerator._php_microtime()
        self.assertIsInstance(result, str)
        parts = result.split(' ')
        self.assertEqual(len(parts), 2)
        # 第一部分应为 0.xxxx 格式
        self.assertTrue(parts[0].startswith('0.'))
        self.assertEqual(len(parts[0]), 10)  # '0.' + 8位小数
        # 第二部分应为秒数
        self.assertTrue(parts[1].isdigit())


class TestRc4Encrypt(unittest.TestCase):
    """_rc4_encrypt 输出非空字符串"""

    @classmethod
    def setUpClass(cls):
        cls.env_patch = patch.dict(os.environ, {
            'TOKEN_KEY': 'test_key_rc4',
            'TOKEN_VERIFY_SALT': 'test_salt_rc4'
        })
        cls.env_patch.start()
        import common.get_token as gt
        importlib.reload(gt)
        cls.gt = gt

    @classmethod
    def tearDownClass(cls):
        cls.env_patch.stop()

    def test_rc4_output_not_empty(self):
        """RC4 加密输出应非空"""
        result = self.gt.TokenGenerator._rc4_encrypt('hello', 'secret_key')
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_rc4_output_length(self):
        """RC4 加密输出长度应与输入相同"""
        data = 'test_data_12345'
        key = 'my_key'
        result = self.gt.TokenGenerator._rc4_encrypt(data, key)
        self.assertEqual(len(result), len(data))

    def test_rc4_different_keys(self):
        """不同密钥应产生不同加密结果"""
        data = 'same_data'
        result1 = self.gt.TokenGenerator._rc4_encrypt(data, 'key1')
        result2 = self.gt.TokenGenerator._rc4_encrypt(data, 'key2')
        self.assertNotEqual(result1, result2)


class TestEnvironmentVariables(unittest.TestCase):
    """环境变量缺失时应抛出 EnvironmentError"""

    def test_missing_token_key_raises(self):
        """TOKEN_KEY 缺失时应抛出 EnvironmentError"""
        with patch.dict(os.environ, {}, clear=True):
            # 确保 TOKEN_VERIFY_SALT 存在但 TOKEN_KEY 不存在
            os.environ['TOKEN_VERIFY_SALT'] = 'some_salt'
            os.environ.pop('TOKEN_KEY', None)
            with self.assertRaises(EnvironmentError):
                import common.get_token as gt
                importlib.reload(gt)

    def test_missing_verify_salt_raises(self):
        """TOKEN_VERIFY_SALT 缺失时应抛出 EnvironmentError"""
        with patch.dict(os.environ, {}, clear=True):
            os.environ['TOKEN_KEY'] = 'some_key'
            os.environ.pop('TOKEN_VERIFY_SALT', None)
            with self.assertRaises(EnvironmentError):
                import common.get_token as gt
                importlib.reload(gt)


if __name__ == '__main__':
    unittest.main()
