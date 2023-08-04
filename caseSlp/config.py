# 打赏人
from common.Config import config

pay_url = config.slp_pay_url
# 打赏人
payPhone = "15008520001"
payUid = 200000118

# 被打赏人 01
rewardPhoneUid = "15008520002"
rewardUid = 200000120  # 手机 15008520002

# 礼物配置 todo
giftId = {
	"5": 5,  # 棒棒糖*100钻
	# "7": 7,  # 大宝剑*1000钻
	# "11": 11,  # 老司机*3000钻(券-500钻石)
	# "46": 46,  # 幸运星*600钻
	# "47": 47,  # 五色星*2100钻
	# "54": 54,  # 小天使*9900钻（商城购买）
	# "62": 62,  # 人气券*20（金币）
	# "362": 362,  # 啵啵奶茶*1000（金豆）
}
# # 房间号
# slp_rid = 10002496
# # 打赏人
# slp_payPhone = "15008520001"
# slp_payUid = a_uid = 200000118
# # 被打赏人 01
# slp_rewardPhoneUid01 = "15008520002"
# slp_rewardUid01 = b_uid = 124586  # 手机 15008520002
# # 被打赏人 02
# slp_rewardPhoneUid02 = "15008520003"
# slp_rewardUid02 = c_uid = 124587  # 手机 15008520003
#
#
# # 作品id
# slp_work_state = {
# 	"todo": 9926,  # 未打赏
# 	"done": 9927,  # 已打赏
# }
#
# # 礼物配置
# commodity_config = {
# 	# 作品礼物
# 	"1": {
# 		"gift_id": 1,  # 礼物id
# 		"name": "星币",
# 		"price": 1,
# 		"cid": 28,
# 		"wealth": 1,
# 		"charm": 0,
# 	},
# 	"2": {
# 		"gift_id": 2,
# 		"name": "安可",
# 		"price": 2,
# 		"cid": 29,
# 		"wealth": 2,
# 		"charm": 0,
# 	},
# 	# 房间礼物-非特权
# 	"3": {
# 		"gift_id": 3,
# 		"name": "为你打call",
# 		"price": 5,
# 		"cid": 1,
# 		"wealth": 5,
# 		"charm": 1,
# 	},
# 	"4": {
# 		"gift_id": 4,
# 		"name": "荧光棒",
# 		"price": 40,
# 		"cid": 2,
# 		"wealth": 40,
# 		"charm": 8,
# 	},
# 	"5": {
# 		"gift_id": 5,
# 		"name": "气泡枪",
# 		"price": 150,
# 		"cid": 3,
# 		"wealth": 150,
# 		"charm": 30,
# 	},
# 	"6": {
# 		"gift_id": 6,
# 		"name": "光音魔瓶",
# 		"price": 520,
# 		"cid": 4,
# 		"wealth": 520,
# 		"charm": 104,
# 	},
# 	"7": {
# 		"gift_id": 7,
# 		"name": "节奏大师",
# 		"price": 1200,
# 		"cid": 5,
# 		"wealth": 1200,
# 		"charm": 240,
# 	},
# 	"8": {
# 		"gift_id": 8,
# 		"name": "麦克风",
# 		"price": 2000,
# 		"cid": 6,
# 		"wealth": 2000,
# 		"charm": 400,
# 	},
# 	"9": {
# 		"gift_id": 9,
# 		"name": "聲霸天下",
# 		"price": 5200,
# 		"cid": 7,
# 		"wealth": 5200,
# 		"charm": 1040,
# 		"reward_lower": 0.05,  # 返奖下限
# 		"reward_upper": 0.10,  # 返奖上限
# 	},
# 	"10": {
# 		"gift_id": 10,
# 		"name": "摩登派对",
# 		"price": 19999,
# 		"cid": 8,
# 		"wealth": 19999,
# 		"charm": 3999,
# 		"reward_lower": 0.15,
# 		"reward_upper": 0.20,
# 	},
# 	#特权礼物
# 	"lv1": {
# 		"gift_id": 28,
# 		"name": "pick me",
# 		"price": 100,
# 		"cid": 70,
# 		"wealth": 100,
# 		"charm": 20,
# 	},
# 	"lv2": {
# 		"gift_id": 27,
# 		"name": "加热度",
# 		"price": 300,
# 		"cid": 69,
# 		"wealth": 300,
# 		"charm": 60,
# 	},
# 	"lv3": {
# 		"gift_id": 15,
# 		"name": "藤野仙車",
# 		"price": 520,
# 		"cid": 30,
# 		"wealth": 520,
# 		"charm": 104,
# 	},
# 	"lv4": {
# 		"gift_id": 16,
# 		"name": "蝴蝶仙女",
# 		"price": 2000,
# 		"cid": 31,
# 		"wealth": 2000,
# 		"charm": 400,
# 	},
# 	"lv5": {
# 		"gift_id": 17,
# 		"name": "愛心轟炸機",
# 		"price": 5200,
# 		"cid": 32,
# 		"wealth": 5200,
# 		"charm": 1040,
# 		"reward_lower": 0.1,
# 		"reward_upper": 0.15,
# 	},
# 	"lv6": {
# 		"gift_id": 18,
# 		"name": "林深見鹿",
# 		"price": 18888,
# 		"cid": 33,
# 		"wealth": 18888,
# 		"charm": 3777,
# 		"reward_lower": 0.15,
# 		"reward_upper": 0.20,
# 	},
# 	# 宝箱免费礼物
# 	"51": {
# 		"gift_id": 51,  # 礼物id
# 		"name": "音符",  # 日常宝箱-免费礼物
# 		"price": 1,
# 		"cid": 113,
# 		"wealth": 1,
# 		"charm": 0,
# 	},
#
#
# 	# 物品-头像框
# 	"header": {
# 		"gift_id": 0,
# 		"name": "Dreamy Planet",
# 		"price": 10000,
# 		"cid": 13,
# 		"level_1":
# 			{
# 				"day": 3,
# 				"rate": 0.9,  # 折扣
# 				"duration": 3 * 86400,
# 			},
# 		"level_2":
# 			{
# 				"day": 7,
# 				"rate": 0.9,  # 折扣
# 				"duration": 7 * 86400,
# 			},
# 		"level_3":
# 			{
# 				"day": 15,
# 				"rate": 0.85,  # 折扣
# 				"duration": 15 * 86400,
# 			},
# 		"wealth": 10000,
# 		"charm": 0,
# 	},
# 	# 物品-麦上光圈
# 	"ring": {
# 		"gift_id": 0,
# 		"name": "Love at First Sight",
# 		"price": 9000,
# 		"cid": 14,
# 		"level_1":
# 			{
# 				"day": 3,
# 				"rate":1,  # 折扣
# 				"duration": 3 * 86400,
# 			},
# 		"level_2":
# 			{
# 				"day": 7,
# 				"rate": 0.9,  # 折扣
# 				"duration": 7 * 86400,
# 			},
# 		"level_3":
# 			{
# 				"day": 15,
# 				"rate": 0.9,  # 折扣
# 				"duration": 15 * 86400,
# 			},
# 		"wealth": 9000,
# 		"charm": 0,
# 	},
# 	# 物品-入场横幅
# 	"effect": {
# 		"gift_id": 0,
# 		"name": "Electric Guitar",
# 		"price": 4000,
# 		"cid": 15,
# 		"level_1":
# 			{
# 				"day": 3,
# 				"rate": 1,  # 折扣
# 				"duration": 3 * 86400,
# 			},
# 		"level_2":
# 			{
# 				"day": 7,
# 				"rate": 0.9,  # 折扣
# 				"duration": 7 * 86400,
# 			},
# 		"level_3":
# 			{
# 				"day": 15,
# 				"rate": 0.85,  # 折扣
# 				"duration": 15 * 86400,
# 			},
# 		"wealth": 4000,
# 		"charm": 0,
# 	},
# }
#
# # 分成比例
# contract_ratio = {
# 	'singer': 0.1,  # 歌手
# 	'producer': 0.7,  # 制作人
# }
#
# # 财富等级
# wealth_lv = {
# 	"lv0": {
# 		"min": 0,
# 		"max": 5000-1,
# 	},
# 	"lv1": {
# 		"min": 5000,
# 		"max": 50000-1,
# 	},
# 	"lv2": {
# 		"min": 50000,
# 		"max": 100000-1,
# 	},
# 	"lv3": {
# 		"min": 100000,
# 		"max": 380000-1,
# 	},
# 	"lv4": {
# 		"min": 380000,
# 		"max": 660000-1,
# 	},
# 	"lv5": {
# 		"min": 660000,
# 		"max": 1500000-1,
# 	},
# 	"lv6": {
# 		"min": 1500000,
# 		"max": 99999999,
# 	},
# }
