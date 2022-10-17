import hashlib
from time import time

from common.Basic_starify import query_starify


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
	:param query: 路径参数,以dict形式传递
	:param salt: 盐,可能不一样
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
	return hashlib.md5(str(int(time())).encode()).hexdigest()


if __name__ == '__main__':
	# deal_query = query_starify.copy()
	# t = str(int(time()))
	# deal_query['_timestamp'] = t
	# # deal_query['_timestamp'] = 1664435210
	# deal_query['_index'] = 250
	# deal_query['format'] = "json"
	# print(deal_query['_timestamp'])
	# print(create_sign(deal_query))
	print(int(time()+3600*24))