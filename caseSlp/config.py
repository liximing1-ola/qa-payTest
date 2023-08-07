# 打赏人
from common.Config import config as old_config

pay_url = old_config.slp_pay_url
default_num = 10  # 礼物个数
default_money = 1000  # 打赏者默认金额
payUid = 200000128  # 15008520000	支付测试0000	打赏者

gs_A_ceo_uid = 200000118  # 15008520001	支付测试0001	A公会长
gs_B_ceo_uid = 200000120  # 15008520002	支付测试0002	B公会长
gs_A_uid = 200000124  # 15008520003	支付测试0003	A工会-成员
gs_B_uid = 200000125  # 15008520004	支付测试0004	B工会-成员
normal_uid = 200000126  # 15008520005	支付测试0005	普通用户
# 麦位index
microphone_num = {  # todo
	"接待": 0,
	"普通": 1,
	"老板": 8,
}
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

# 分成比例
rates = {
	# 主播,mc
	'gs': {
		"default": 0.6,  # 默认
		"other_room": 0.5,  # 跨档
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

# # 角色配置 todo
# live_role = {
# 	'pack_ceo': 105002314,  # 直播公会公会长
# 	'pack_master_NoPack': 105002319,  # 非公会一代宗师主播
# 	'pack_cal_uid': 105002313,  # 公会签约主播（打包结算），宗师等级可设置为一代和非一代
# 	'live_rid': 193185577,  # 直播间(types=live)，房主:105002313
# 	'auto_rid': 193185484,  # business | types: auto | room_factory_type: business-content | settlement_channel: cp-women
# }
# # 被打赏者（一代宗师） todo
# masterUid = 100500338
