# coding=utf-8
"""
通用工具函数模块

提供哈希计算、精度处理等通用工具。
"""
import hashlib
import math
import time


def hash_key():
    """生成连击key"""
    return hashlib.md5(str(int(time.time())).encode()).hexdigest()


def deal_num(num):
    """处理精度问题,保留2位小数后,向上取整"""
    return math.ceil(round(num, 2))

