"""
Token生成器模块

用于生成用户认证Token
"""
import time
import random
import hashlib
import base64
from urllib.parse import quote, urlencode


# 配置常量
KEY = "^&(tre)%29^*"
EXPIRY = 2592000
CHARS = '01234567890abcdefghijklmnopqrstuvwxyz'
VERIFY_SALT = '5(d+V8cxpY%d'
KEY_C_LENGTH = 4
SALT_LENGTH = 10


class TokenGenerator:
    """Token生成器"""

    def __init__(self, uid, salt):
        self.uid = uid
        self._salt = salt

    def generate(self) -> str:
        """生成Token"""
        # 构建参数
        arg_dict = {
            "u": self.uid,
            "s": self._salt,
            "p": "app",
            "t": int(time.time()),
            "c": ""
        }
        string = urlencode(arg_dict)
        
        # 生成摘要
        digests = self._md5(string + VERIFY_SALT).lower()
        data = string + digests[:5]
        
        # 生成密钥
        key = self._md5(KEY)
        key_a = self._md5(key[:16])
        key_b = self._md5(key[16:32])
        key_c = self._md5(self._php_microtime())[-4:]
        crypt_key = key_a + self._md5(key_a + key_c)
        key_length = len(crypt_key)
        
        # 构建数据
        data = f"{int(time.time()) + EXPIRY:010d}" + self._md5(data + key_b)[:16] + data
        data_length = len(data)
        
        # RC4加密
        encrypted = self._rc4_encrypt(data, crypt_key, key_length)
        
        # 生成Token
        token = quote(
            key_c + str(base64.b64encode(bytes(encrypted, encoding='latin1')), encoding='latin1')
            .replace("=", "")
        ).replace("/", "%2F").replace("%", "__")
        
        return token

    def _rc4_encrypt(self, data: str, crypt_key: str, key_length: int) -> str:
        """RC4加密"""
        box = list(range(256))
        rndkey = [ord(crypt_key[i % key_length]) for i in range(256)]
        
        # 打乱盒子
        j = 0
        for i in range(256):
            j = (j + box[i] + rndkey[i]) % 256
            box[i], box[j] = box[j], box[i]
        
        # 加密
        a = j = 0
        result = ""
        for i in range(len(data)):
            a = (a + 1) % 256
            j = (j + box[a]) % 256
            box[a], box[j] = box[j], box[a]
            result += chr(ord(data[i]) ^ box[(box[a] + box[j]) % 256])
        
        return result

    @staticmethod
    def generate_salt() -> str:
        """生成随机盐值"""
        return ''.join(random.choice(CHARS) for _ in range(SALT_LENGTH))

    @staticmethod
    def _md5(s: str) -> str:
        """计算MD5"""
        return hashlib.md5(s.encode('utf-8')).hexdigest()

    @staticmethod
    def _php_microtime() -> str:
        """模拟PHP microtime函数"""
        t = time.time()
        s, m = str(t).split(".")
        m = str(float(m) / (10 ** len(m))).ljust(10, "0")
        return f"{m} {s}"


if __name__ == "__main__":
    token1 = TokenGenerator(100287189, TokenGenerator.generate_salt())
    token2 = TokenGenerator(100797678, TokenGenerator.generate_salt())
    print(token1.generate())
    print(token2.generate())
