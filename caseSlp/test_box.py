# # -*- encoding=utf8 -*-
# __author__ = "Wu.Zhenxing"
# __title__ = ""
# __desc__ = "甄选礼盒"
#
# import unittest
#
# from caseSlp.config import *
# from common.Assert import assert_code, assert_equal, assert_body
# from common.Consts import case_list, result
# from common.Request import post_request_session
# from common.basicSlpData import encodeData
# from common.conSlpMysql import conMysql as mysql
# from common.method import reason
# from common.runFailed import Retry
#
#
# @Retry(max_n=3)
# class TestPayCreate(unittest.TestCase):
# 	def test_001(self, des='甄选礼盒'):
# 		"""
# 		用例描述：
# 		甄选礼盒,送礼人爵位=亲王,送多人多个场景
# 		脚本步骤：
# 		1.构造打赏者和被打赏者数据
# 		2.私聊一对一打赏流程(礼物:棒棒糖)
# 		3.校验接口和返回值数据
# 		4.检查预期返回msg，预期：支付失败，提示Toast
# 		5.检查被打赏者余额,预期：0
# 		"""
# 		mysql.updateUserMoneyClearSql(payUid, normal_uid, gsUid)
# 		mysql.deleteUserAccountSql('user_commodity', payUid)
# 		mysql.deleteUserAccountSql('user_title_new', payUid)  # 关闭贵族,还原数据
# 		# 清除打赏流水
# 		mysql.deleteUserAccountSql('pay_change', payUid)
# 		# 清空人气值
# 		mysql.deleteUserAccountSql('user_popularity', normal_uid)
# 		mysql.deleteUserAccountSql('user_popularity', gsUid)
# 		# 清空VIP值
# 		mysql.deleteUserAccountSql('pay_room_money', payUid)
# 		# 开启爵位
# 		mysql.updateUserInfoSql('user_title_new', payUid, level=juewei_level['亲王']['level'])
# 		mysql.updateMoneySql(payUid, 10000000)
#
# 		data = encodeData(
# 			payType='zx_box',
# 			num=1000,
# 			giftId=zx_box['6']['gid'],
# 			price=zx_box['6']['price'],
# 			uids=('{}'.format(normal_uid), '{}'.format(gsUid))
# 		)
# 		res = post_request_session(pay_url, data, tokenName='slp')
# 		assert_code(res['code'])
# 		assert_body(res['body'], 'success', 1, reason(des, res))
# 		# 查询 打赏人/收礼人数据,用于计算
# 		send_gift_data= mysql.selectZxPayData(payUid)
# 		# 校验收礼人气值
# 		# 校验送礼人VIP值
# 		# 校验送礼人贵族成长值
# 		# 校验送礼人扣费
# 		# 校验收礼人分成
#
#
# 		case_list[des] = result
