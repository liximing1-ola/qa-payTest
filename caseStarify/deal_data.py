import json

from caseStarify.need_data import *
from caseStarify.tools import hash_key


def deal_pay_data(op_type, commodity, work_state="todo", to_uids=None, is_use_bag=False, hit_offset=1, combo_key=None,sale_level=1):
	"""
	处理pay的data
	:param op_type: 打赏类型 work/room
	:param commodity: 物品
	:param work_state: 作品状态,done/todo
	:param to_uids: 房间打赏时,必传,被打赏人id的list
	:param is_use_bag: 房间打赏时,必传,是否时背包礼物
	:param hit_offset: 合并请求的连击数
	:param combo_key: 连击key
	:param sale_level: 物品购买档位 1,2,3
	:return:
	"""

	if to_uids is None:
		to_uids = []
	params_work = {
		"gift_id": commodity['gift_id'],
		"gift_num": 1,
		"price": commodity['price'],
		"num": 1,  # 只能打赏一次固定为1
		"gift_type": "normal",
		"uid": starify_payUid,
		"wid": starify_work_state[work_state]
	}
	params_room = {
		"from_uid": starify_payUid,
		"to_uids": to_uids,
		"rid": starify_rid,
		"gift_id": commodity['gift_id'],
		"cid": 0,  # todo 从礼物面板发起=0,从背包发起=cid
		"gift_num": 1,  # 无用参数
		"is_use_bag": is_use_bag,
		"money": commodity['price'],
		"combo_key": combo_key if combo_key is not None else hash_key(),
		"hit_offset": hit_offset
	}
	params_shop = {
		"cid": commodity['cid'],
		"sale_level": sale_level,  # 档位 1=3天/2=7天/3=15天
		"count": 1  # 目前,默认为1
	}

	if op_type == "work":  # 作品
		params = params_work
		total_money = str(commodity['price'])
	elif op_type == "room":  # 歌房
		params = params_room
		total_money = str(commodity['price'] * len(to_uids) * int(hit_offset))  # 单价*人数*连击数
	elif op_type == "shop_buy":  # 商城
		params = params_shop
		total_money = "0"  # 无用参数
	else:
		raise Exception("不支持的参数!")

	data = {
		"op_type": op_type,
		"params": json.dumps(params),
		"money_type": "star_coin",
		"total_money": total_money,
	}
	return data


def deal_pay_contract_data(op_type, from_uid, worth, sign_type, singer_uid=c_uid, rid=0):
	"""
	处理 竞拍玩法 参数
	:param op_type: 类型
	:param singer_uid: # 被买的人
	:param rid: 房间id
	:param from_uid: # 购买者
	:param worth:  # 价格
	:param sign_type: # 类型 1=直接购买，0=竞价
	:return:
	"""
	params_contract = {
		"singer_uid": singer_uid,
		"rid": rid,
		"from_uid": from_uid,
		"worth": worth,
		"sign_type": sign_type
	}

	if op_type == "audition_contract":  # 竞拍
		params = params_contract
		total_money = str(worth)
	else:
		raise Exception("不支持的参数!")
	data = {
		"op_type": op_type,
		"params": json.dumps(params),
		"money_type": "star_coin",
		"total_money": total_money,
		"hideErrorToast": "1"
	}
	print(data)
	return data
