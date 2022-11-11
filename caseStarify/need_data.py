# 房间号
starify_rid = 10002496
# 打赏人
starify_payPhone = "15008520001"
starify_payUid = 124585
# 被打赏人 01
starify_rewardUid01 = 124586  # 手机 15008520002
# 被打赏人 02
starify_rewardUid02 = 124587  # 手机 15008520003


# 作品id
starify_work_state = {
	"todo": 9926,  # 未打赏
	"done": 9927,  # 已打赏
}

# 礼物配置
commodity_config = {
	# 作品礼物
	"1": {
		"gift_id": 1,  # 礼物id
		"name": "星幣",
		"price": 1,
		"cid": 28,
	},
	"2": {
		"gift_id": 2,
		"name": "安可",
		"price": 2,
		"cid": 29,
	},
	# 房间礼物-非特权
	"3": {
		"gift_id": 3,
		"name": "為你打call",
		"price": 5,
		"cid": 30,
	},
	"4": {
		"gift_id": 4,
		"name": "螢光棒",
		"price": 40,
		"cid": 31,
	},
	"5": {
		"gift_id": 5,
		"name": "氣泡槍",
		"price": 150,
		"cid": 32,
	},
	"6": {
		"gift_id": 6,
		"name": "光音魔瓶",
		"price": 520,
		"cid": 33,
	},
	"7": {
		"gift_id": 7,
		"name": "節奏大師",
		"price": 1200,
		"cid": 34,
	},
	"8": {
		"gift_id": 8,
		"name": "麥克風",
		"price": 2000,
		"cid": 35,
	},
	"9": {
		"gift_id": 9,
		"name": "聲霸天下",
		"price": 5200,
		"cid": 36,
		"reward_lower": 0.05,  # 返奖下限
		"reward_upper": 0.10  # 返奖上限
	},
	"10": {
		"gift_id": 10,
		"name": "摩登派對",
		"price": 19999,
		"cid": 37,
		"reward_lower": 0.15,
		"reward_upper": 0.20
	},
	# 物品-头像框
	"header": {
		"gift_id": 0,
		"name": "header-2",
		"price": 444,
		"cid": 46,
		"level_1":
			{
				"day": 3,
				"rate": 1,  # 折扣
				"duration": 3 * 86400,
			},
		"level_2":
			{
				"day": 7,
				"rate": 0.8,  # 折扣
				"duration": 7 * 86400,
			},
		"level_3":
			{
				"day": 15,
				"rate": 0.7,  # 折扣
				"duration": 15 * 86400,
			},
	},
	# 物品-麦上光圈
	"ring": {
		"gift_id": 0,
		"name": "ring-1",
		"price": 2222,
		"cid": 44,
		"level_1":
			{
				"day": 3,
				"rate":1,  # 折扣
				"duration": 3 * 86400,
			},
		"level_2":
			{
				"day": 7,
				"rate": 0.85,  # 折扣
				"duration": 7 * 86400,
			},
		"level_3":
			{
				"day": 15,
				"rate": 0.65,  # 折扣
				"duration": 15 * 86400,
			},
	},
	# 物品-入场横幅
	"effect": {
		"gift_id": 0,
		"name": "effect-3",
		"price": 333,
		"cid": 42,
		"level_1":
			{
				"day": 3,
				"rate": 1,  # 折扣
				"duration": 3 * 86400,
			},
		"level_2":
			{
				"day": 7,
				"rate": 0.7,  # 折扣
				"duration": 7 * 86400,
			},
		"level_3":
			{
				"day": 15,
				"rate": 0.5,  # 折扣
				"duration": 15 * 86400,
			},
	},
}

