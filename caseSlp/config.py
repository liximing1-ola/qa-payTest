# 打赏人
from common.Config import config as old_config

pay_url = old_config.slp_pay_url
default_num = 1  # 礼物个数
default_money = 100000  # 打赏者默认金额
payUid = 200000128  # 15008520000	支付测试0000	打赏者/Basic.yml 登录session

gs_A_ceo_uid = 200000118  # 15008520001	支付测试0001	A公会长
gs_B_ceo_uid = 200000120  # 15008520002	支付测试0002	B公会长
gs_A_uid = gsUid = 200000124  # 15008520003	支付测试0003	A工会-成员
gs_B_uid = 200000125  # 15008520004	支付测试0004	B工会-成员
normal_uid = rewardUid = 200000126  # 15008520005	支付测试0005	普通用户

gs_A_ceo_rid = gs_soundchat_rid = 100000388  # A工会-工会长 rid  商业-直播厅/business-soundchat
gs_B_ceo_rid = gs_friend_rid = 100000390  # B工会-工会长 rid  商业-标准9麦/business-friend
gs_A_rid = 100000410  # A工会-成员 rid  商业-直播厅/business-soundchat
gs_B_rid = 100000373  # B工会-成员 rid  商业-标准9麦/business-friend
normal_rid = 100000366  # 普通用户 rid  商业-标准9麦/business-friend

# 麦位index
microphone_num = {  # todo
	"接待": 0,
	"普通": 1,
	"老板": 8,
}
# 礼物配置
giftId = {
	"69": {  # 椰子水*100钻
		"gid": 69,
		"cid": 329,
		"price": 100
	},
	"70": {  # 羽毛*300钻
		"gid": 70,
		"cid": 330,
		"price": 300
	},
}

room_defend = {  # 房间守护
	'chunai': {  # 纯爱
		'week': {
			'knight_level': 1,
			'duration_level': 1,
			'price': 9900,
		},
		'month': {
			'knight_level': 1,
			'duration_level': 2,
			'price': 29900,
		},
		'year': {
			'knight_level': 1,
			'duration_level': 3,
			'price': 299000,
		}
	},
	'zhenai': {  # 真爱
		'week': {
			'knight_level': 2,
			'duration_level': 1,
			'price': 28800,
		},
		'month': {
			'knight_level': 2,
			'duration_level': 2,
			'price': 99900,
		},
		'year': {
			'knight_level': 2,
			'duration_level': 3,
			'price': 999000,
		},
	},
	'zhiai': {  # 挚爱
		'week': {
			'knight_level': 3,
			'duration_level': 1,
			'price': 88800,
		},
		'month': {
			'knight_level': 3,
			'duration_level': 2,
			'price': 299900,
		},
		'year': {
			'knight_level': 3,
			'duration_level': 3,
			'price': 29999000,
		},
	},
}
defend = {  # 个人守护
	"CP": {
		"id": 1,
		"price": 520000,
		"upgrade_price": 520000,
		"break_price": 99900,

	},
	"小宝贝": {
		"id": 2,
		"price": 52000,
		"upgrade_price": 99900,
		"break_price": 28800,
	},
	"知己": {
		"id": 3,
		"price": 52000,
		"upgrade_price": 99900,
		"break_price": 28800,
	},
	"守卫": {
		"id": 4,
		"price": 36000,
		"upgrade_price": 66600,
		"break_price": 28800,
	},
	"队友": {
		"id": 5,
		"price": 6600,
		"upgrade_price": 66600,
		"break_price": 28800,
	},
	"跟班": {
		"id": 6,
		"price": 36000,
		"upgrade_price": 9900,
		"break_price": 28800,
	},
	"闺蜜": {
		"id": 7,
		"price": 52000,
		"upgrade_price": 520000,
		"break_price": 28800,
	},
	"兄弟": {
		"id": 8,
		"price": 36000,
		"upgrade_price": 66600,
		"break_price": 28800,
	},
}
# 分成比例
rates = {
	# 主播,mc
	'gs': {
		"default": 0.6,  # 默认
		# "other_room": 0,  # 跨档
		# "room": 0,  # 房间
		# "chat": 0,  # 私聊
		# "defend": 0,  # 个人守护
		# "room_defend": 0,  # 直播房间守护
	},
	# 普通用户,mcb
	'normal': {
		"default": 0.6,  # 默认
		# "room": 0,  # 房间
		# "chat": 0,  # 私聊
		# "defend": 0,  # 个人守护
	},
}
# 爵位
juewei_level = {
	'骑士': {
		'level': 10,
		'update': 100,
	},
	'男爵': {
		'level': 20,
		'update': 100,
	},
	'子爵': {
		'level': 30,
		'update': 100,
	},
	'伯爵': {
		'level': 40,
		'update': 105,
	},
	'侯爵': {
		'level': 50,
		'update': 110,
	},
	'公爵': {
		'level': 60,
		'update': 115,
	},
	'亲王': {
		'level': 70,
		'update': 120,
	},
	'国王': {
		'level': 80,
		'update': 125,
	},
	'皇帝': {
		'level': 90,
		'update': 130,
	},
}
# # # 角色配置 todo
# live_role = {
# 	'pack_ceo': 105002314,  # 直播公会公会长
# 	'pack_master_NoPack': 105002319,  # 非公会一代宗师主播
# 	'pack_cal_uid': 105002313,  # 公会签约主播（打包结算），宗师等级可设置为一代和非一代
# 	'live_rid': 193185577,  # 直播间(types=live)，房主:105002313
# 	'auto_rid': 193185484,  # business | types: auto | room_factory_type: business-content | settlement_channel: cp-women
# }
# # 被打赏者（一代宗师） todo
# masterUid = 100500338
