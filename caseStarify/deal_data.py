import json

from caseStarify.need_data import *
from caseStarify.tools import hash_key


def deal_pay_data(op_type, gift, work_state="todo", to_uids=None, is_use_bag=False, hit_offset=1, combo_key=None):
	"""
	处理pay的data
	:param op_type: 打赏类型 work/room
	:param gift: 礼物id
	:param work_state: 作品状态,done/todo
	:param to_uids: 房间打赏时,必传,被打赏人id的list
	:param is_use_bag: 房间打赏时,必传,是否时背包礼物
	:param hit_offset: 合并请求的连击数
	:return:
	"""
	gifts = gift_config if op_type == "work" else gift_config

	if to_uids is None:
		to_uids = []
	gift = str(gift)
	params_work = {
		"gift_id": gifts[gift]['gift_id'],
		"gift_num": 1,
		"price": gifts[gift]['price'],
		"num": 1,  # 只能打赏一次固定为1
		"gift_type": "normal",
		"uid": starify_payUid,
		"wid": starify_work_state[work_state]
	}
	params_room = {
		"from_uid": starify_payUid,
		"to_uids": to_uids,
		"rid": starify_rid,
		"gift_id": gifts[gift]['gift_id'],
		"cid": 0,  # todo
		"gift_num": 1,
		"is_use_bag": is_use_bag,
		"money": gifts[gift]['price'],
		"combo_key": combo_key if combo_key is not None else hash_key(),
		"hit_offset": hit_offset  # todo
	}
	if op_type == "work":
		params = params_work
		total_money = str(gifts[gift]['price'])
	else:
		params = params_room
		total_money = str(gifts[gift]['price'] * len(to_uids) * int(hit_offset))  # 单价*人数*连击数

	data = {
		"op_type": op_type,
		"params": json.dumps(params),
		"money_type": "star_coin",
		"total_money": total_money,
	}
	return data
