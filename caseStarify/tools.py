import hashlib
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
	return hashlib.md5(str(int(time.time())).encode()).hexdigest()


if __name__ == '__main__':
	# deal_query = query_starify.copy()
	# t = str(int(time()))
	# deal_query['_timestamp'] = t
	# # deal_query['_timestamp'] = 1664435210
	# deal_query['_index'] = 250
	# deal_query['format'] = "json"
	# print(deal_query['_timestamp'])
	# print(create_sign(deal_query))
	# print(int(time()+3600*24))
	url = "https://hooks.slack.com/services/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"
	# data ={"text": "This is a line of text in a channel.And this is another line of text."}
	# data = {
	# 	"username": "BUG提醒机器人",
	# 	"icon_emoji": ":lady_beetle:",
	# 	# "channel": "#调试机器人bug通知",#频道 or 人
	# 	"attachments": [
	# 		{
	# 			"fallback": "v1.0.4.4: <https://github.com/orgs/olaola-chat/projects/9/views/5?v=wq1R93UMqlk|点击跳转bug列表>",
	# 			"pretext": "v1.0.4.4: <https://github.com/orgs/olaola-chat/projects/9/views/5?v=wq1R93UMqlk|点击跳转bug列表>",
	# 			"color": "#D00000",
	# 			"fields": [
	# 				{
	# 					"title": "1",
	# 					"value": "1",
	# 					"short": False
	# 				},
	# 				{
	# 					"title": "2",
	# 					"value": "2",
	# 					"short": False
	# 				},
	# 			]
	# 		}
	# 	]
	# }

	# branch = {
	# 	"commit": "8abcad6",
	# 	"author": "wzx",
	# 	"summary": "Merge branch 'master' of https://github.com/liximing-ola/qa-payTest into wzx",
	# 	"date": "2022-10-19 14:38:57"
	# }
	# data = {
	# 	"username": "starify支付回归",
	# 	"icon_emoji": ":lady_beetle:",
	# 	"text": json.dumps(branch),
	# }
	result_dict = {'星币余额充足,作品打赏,礼物类型=安可': 'P', '作品打赏,星币余额=0': 'P'}
	fields = []
	for k, v in result_dict.items():
		field = {
			"title": f"Scene:{k}",
			"value": f"执行结果:{v}",
			"short": False
		}
		fields.append(field)
	data = {
		"username": "starify支付回归",
		"icon_emoji": ":lady_beetle:",
		# "channel": "#调试机器人bug通知",#频道 or 人
		"attachments": [
			{
				"fallback":  f"运行于:{time.strftime('%m-%d %H:%M', time.localtime(time.time()))}",
				"pretext": f"运行于:{time.strftime('%m-%d %H:%M', time.localtime(time.time()))}",
				"color": "#11d000",
				"fields": fields
			}
		]
	}
	res = requests.post(url, json=data)
	print(res.content.decode())
