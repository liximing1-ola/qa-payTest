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
# 角色配置 todo
live_role = {
	'pack_ceo': 105002314,  # 直播公会公会长
	'pack_master_NoPack': 105002319,  # 非公会一代宗师主播
	'pack_cal_uid': 105002313,  # 公会签约主播（打包结算），宗师等级可设置为一代和非一代
	'live_rid': 193185577,  # 直播间(types=live)，房主:105002313
	'auto_rid': 193185484,  # business | types: auto | room_factory_type: business-content | settlement_channel: cp-women
}
# 被打赏者（一代宗师） todo
masterUid = 100500338