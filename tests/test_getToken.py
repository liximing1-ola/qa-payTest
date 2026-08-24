# coding=utf-8
"""
common/getToken.py 单元测试

覆盖纯逻辑函数：generate_salt / _md5 / _php_microtime / _rc4_encrypt / generate
可在无后端环境下直接运行：
    python -m pytest tests/test_getToken.py -v
"""
import re
import unittest

from common.getToken import (
    TokenGenerator,
    CHARS,
    KEY_C_LENGTH,
    SALT_LENGTH,
)


class TestConstants(unittest.TestCase):
    """常量一致性"""

    def test_chars_no_duplicates(self):
        """CHARS 不应有重复字符"""
        self.assertEqual(len(CHARS), len(set(CHARS)))

    def test_chars_is_lowercase_alnum(self):
        """CHARS 应为小写字母+数字"""
        self.assertTrue(all(c.isdigit() or c.islower() for c in CHARS))

    def test_key_c_length_positive(self):
        """KEY_C_LENGTH 应为正整数"""
        self.assertGreater(KEY_C_LENGTH, 0)

    def test_salt_length_positive(self):
        """SALT_LENGTH 应为正整数"""
        self.assertGreater(SALT_LENGTH, 0)


class TestGenerateSalt(unittest.TestCase):
    """盐值生成"""

    def test_returns_correct_length(self):
        """盐值长度应为 SALT_LENGTH"""
        salt = TokenGenerator.generate_salt()
        self.assertEqual(len(salt), SALT_LENGTH)

    def test_all_chars_from_charset(self):
        """盐值字符应全部来自 CHARS"""
        salt = TokenGenerator.generate_salt()
        self.assertTrue(all(c in CHARS for c in salt))

    def test_different_calls_produce_different_salts(self):
        """两次调用应产生不同盐值（随机性）"""
        salt1 = TokenGenerator.generate_salt()
        salt2 = TokenGenerator.generate_salt()
        self.assertNotEqual(salt1, salt2)


class TestMd5(unittest.TestCase):
    """MD5 计算"""

    def test_known_value(self):
        """已知输入的 MD5 应匹配"""
        self.assertEqual(
            TokenGenerator._md5('test'),
            '098f6bcd4621d373cade4e832627b4f6',
        )

    def test_returns_lowercase_hex(self):
        """返回应为 32 字符小写十六进制"""
        result = TokenGenerator._md5('anything')
        self.assertEqual(len(result), 32)
        self.assertTrue(re.match(r'^[0-9a-f]{32}$', result))

    def test_empty_string(self):
        """空字符串的 MD5 应为已知值"""
        self.assertEqual(
            TokenGenerator._md5(''),
            'd41d8cd98f00b204e9800998ecf8427e',
        )


class TestPhpMicrotime(unittest.TestCase):
    """PHP microtime 模拟"""

    def test_format(self):
        """返回格式应为 'msec sec'"""
        result = TokenGenerator._php_microtime()
        parts = result.split(' ')
        self.assertEqual(len(parts), 2)
        msec, sec = parts

        # msec 应以 "0." 开头
        self.assertTrue(msec.startswith('0.'))
        # msec 至少 10 字符（0.xxxxxxxx）
        self.assertGreaterEqual(len(msec), 10)
        # sec 应为纯数字
        self.assertTrue(sec.isdigit())

    def test_sec_matches_current_time(self):
        """sec 部分应接近当前时间戳"""
        import time
        before = int(time.time())
        result = TokenGenerator._php_microtime()
        after = int(time.time())
        sec = int(result.split(' ')[1])
        self.assertGreaterEqual(sec, before)
        self.assertLessEqual(sec, after)


class TestRc4Encrypt(unittest.TestCase):
    """RC4 加密"""

    def test_deterministic_same_input_key(self):
        """相同输入+密钥应产生相同输出"""
        data = 'hello world'
        key = 'testkey123'
        result1 = TokenGenerator._rc4_encrypt(data, key)
        result2 = TokenGenerator._rc4_encrypt(data, key)
        self.assertEqual(result1, result2)

    def test_different_key_different_output(self):
        """不同密钥应产生不同输出"""
        data = 'hello world'
        result1 = TokenGenerator._rc4_encrypt(data, 'key1')
        result2 = TokenGenerator._rc4_encrypt(data, 'key2')
        self.assertNotEqual(result1, result2)

    def test_output_same_length_as_input(self):
        """输出长度应等于输入长度（流密码特性）"""
        data = 'abcdefghij'
        result = TokenGenerator._rc4_encrypt(data, 'key')
        self.assertEqual(len(result), len(data))

    def test_empty_input(self):
        """空输入应返回空字符串"""
        self.assertEqual(TokenGenerator._rc4_encrypt('', 'key'), '')

    def test_decrypt_roundtrip(self):
        """RC4 解密=再加密一次（XOR 对称性）"""
        plaintext = 'secret message 12345'
        key = 'mykey'
        encrypted = TokenGenerator._rc4_encrypt(plaintext, key)
        # 对密文再加密一次应恢复原文
        decrypted = TokenGenerator._rc4_encrypt(encrypted, key)
        self.assertEqual(decrypted, plaintext)


class TestGenerate(unittest.TestCase):
    """Token 生成集成测试"""

    def setUp(self):
        self.gen = TokenGenerator(100287189, 'testsalt00')

    def test_returns_non_empty_string(self):
        """Token 应为非空字符串"""
        token = self.gen.generate()
        self.assertTrue(token)
        self.assertIsInstance(token, str)

    def test_token_url_safe(self):
        """Token 不应包含原始 / 或 % 字符（已被编码）"""
        token = self.gen.generate()
        self.assertNotIn('/', token)
        self.assertNotIn('%', token)

    def test_different_uids_different_tokens(self):
        """不同 UID 应产生不同 Token"""
        gen1 = TokenGenerator(100287189, 'salt0001')
        gen2 = TokenGenerator(100797678, 'salt0001')
        # 多次取（因为 microtime 不同），只需验证大概率不同
        tokens = {gen1.generate() for _ in range(5)}
        tokens2 = {gen2.generate() for _ in range(5)}
        # 两个集合不应完全相同
        self.assertTrue(tokens != tokens2)

    def test_token_contains_key_c_prefix(self):
        """Token 前缀应为 key_c（4 字符 MD5 尾部）"""
        token = self.gen.generate()
        # key_c 是 _md5(php_microtime())[-4:]
        # token 格式: key_c + base64(encrypted)
        # key_c 是 4 个十六进制字符
        self.assertGreaterEqual(len(token), 4)
        prefix = token[:4]
        self.assertTrue(re.match(r'^[0-9a-f]{4}$', prefix))


if __name__ == '__main__':
    unittest.main()
