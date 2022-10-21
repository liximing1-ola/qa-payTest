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
	# data = {
	# 	"username": "BUG提醒机器人",
	# 	"icon_emoji": ":lady_beetle:",
	# 	# "channel": "#调试机器人bug通知",#频道 or 人
	# 	"attachments": [
	# 		{
	# 			"fallback": "Plain-text summary of the attachment.",
	# 			"color": "#2eb886",
	# 			"pretext": "Optional text that appears above the attachment block",
	# 			"author_name": "Bobby Tables",
	# 			"author_link": "http://flickr.com/bobby/",
	# 			"author_icon": "http://flickr.com/icons/bobby.jpg",
	# 			"title": "Slack API Documentation",
	# 			"title_link": "https://api.slack.com/",
	# 			"text": "Optional text that appears within the attachment",
	# 			"fields": [
	# 				{
	# 					"title": "Priority",
	# 					"value": "High",
	# 					"short": False
	# 				}
	# 			],
	# 			"image_url": "http://my-website.com/path/to/image.jpg",
	# 			"thumb_url": "http://example.com/path/to/thumb.png",
	# 			"footer": "Slack API",
	# 			"footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
	# 			"ts": 123456789
	# 		}
	# 	]
	# }
	data = {
		# 	"username": "BUG提醒机器人",
		# 	"icon_emoji": ":lady_beetle:",
		"attachments": [
			{
				# "mrkdwn_in": ["text"],
				"color": "#36a64f",
				# "pretext": "",
				# "author_name": "author_name",
				# "author_link": "http://flickr.com/bobby/",
				# "author_icon": "https://placeimg.com/16/16/people",
				"title": "starify蒲公英下载",
				"title_link": "https://api.slack.com/",
				"text": "更新日志:\n1.111\n2.222",
				# "fields": [
				# 	{
				# 		"title": "A field's title",
				# 		"value": "This field's value",
				# 		"short": False
				# 	},
				# 	{
				# 		"title": "A short field's title",
				# 		"value": "A short field's value",
				# 		"short": True
				# 	},
				# 	{
				# 		"title": "A second short field's title",
				# 		"value": "A second short field's value",
				# 		"short": True
				# 	}
				# ],
				"image_url": "http://placekitten.com/g/200/200",
				# "footer": "footer",
				# "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
				"ts": 123456789
			}
		]
	}
	res = requests.post(url, json=data)
	print(res.content.decode())
