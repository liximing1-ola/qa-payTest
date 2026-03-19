import hashlib
import math
import time

import requests


def merge_dicts(*args):
    """
	合并dict
	:param dict_old:老的字典
	:param dict_new:新的字典
	:return:
	"""
    _all_dict = {}
    for _dict in args:
        if not isinstance(_dict, dict):
            _dict = {}
        _all_dict = {**_all_dict, **_dict}
    return _all_dict


def create_sign(query, salt="!rilegoule#"):
    """
	生成sign
	:param query: 路径参数 dict
	:param salt:
	:return:
	"""
    keys = ['_abi', '_index', '_ipv', '_model', '_platform', '_timestamp', 'format', 'package']
    hashArgs = []
    for key in sorted(keys):
        value = query[key]
        hashArgs.append(f"{key}={value}")
    content = '&'.join(hashArgs) + salt
    _sign = hashlib.md5(bytes(content, encoding='utf-8')).hexdigest()
    return _sign


def hash_key():
    """生成连击key"""
    return hashlib.md5(str(int(time.time())).encode()).hexdigest()


def deal_num(num):
    """处理精度问题,保留2位小数后,向上取整"""
    return math.ceil(round(num, 2))


if __name__ == '__main__':
    pass
