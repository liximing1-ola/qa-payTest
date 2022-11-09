import json

from caseStarify.need_data import *
from caseStarify.tools import hash_key


def deal_pay_data(op_type, commodity, work_state="todo", to_uids=None, is_use_bag=False, hit_offset=1, combo_key=None):
	"""
	处理pay的data
	:param op_type: 打赏类型 work/room
	:param commodity: 物品
	:param work_state: 作品状态,done/todo
	:param to_uids: 房间打赏时,必传,被打赏人id的list
	:param is_use_bag: 房间打赏时,必传,是否时背包礼物
	:param hit_offset: 合并请求的连击数
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
		"sale_level": 1,  # 档位 1=3天/2=7天/3=15天
		"count": 1
	}
	if op_type == "work":
		params = params_work
		total_money = str(commodity['price'])
	elif op_type == "room":
		params = params_room
		total_money = str(commodity['price'] * len(to_uids) * int(hit_offset))  # 单价*人数*连击数
	elif op_type == "shop_buy":
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
