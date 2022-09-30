import json

from caseStarify.need_data import *
from caseStarify.tools import hash_key


def deal_pay_data(op_type, gift_id, work_state="todo", to_uids=None, is_use_bag=False, hit_num=1, combo_key=None, gistarify_work_gift_config=None):
	"""
	处理pay的data
	:param op_type: 打赏类型 work/room
	:param gift_id: 礼物id
	:param work_state: 作品状态,done/todo
	:param to_uids: 房间打赏时,必传,被打赏人id的list
	:param is_use_bag: 房间打赏时,必传,是否时背包礼物
	:param hit_num: 房间打赏时,必传,连击数
	:return:
	"""
	gifts = starify_work_gift_config if op_type == "work" else starify_room_gift_config

	if to_uids is None:
		to_uids = []
	if combo_key is None:
		combo_key = hash_key()
	gift_id = str(gift_id)
	params_work = {
		"gift_id": gifts[gift_id]['id'],
		"gift_num": 1,
		"price": gifts[gift_id]['price'],
		"num": 1,
		"gift_type": "normal",
		"uid": starify_payUid,
		"wid": starify_work_state[work_state]
	}
	params_room = {
		"from_uid": starify_payUid,
		"to_uids": to_uids,
		"rid": starify_rid,
		"gift_id": gifts[gift_id]['id'],
		"cid": 0,  # todo
		"gift_num": 1,
		"is_use_bag": is_use_bag,
		"money": gifts[gift_id]['price'],
		"combo_key": combo_key,
		"hit_num": hit_num
	}
	if op_type == "work":
		params = params_work
		total_money = str(gifts[gift_id]['price'])
	else:
		params = params_room
		total_money = str(gifts[gift_id]['price'] * len(to_uids))

	data = {
		"op_type": op_type,
		"params": json.dumps(params),
		"money_type": "star_coin",
		"total_money": total_money,
	}
	return data
