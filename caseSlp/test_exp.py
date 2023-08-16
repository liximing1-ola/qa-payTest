# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "经验值相关用例"
import unittest

from caseSlp.config import *
from common.Assert import assert_code, assert_equal, assert_body
from common.Consts import case_list_b, result
from common.Request import post_request_session
from common.basicSlpData import encodeData
from common.conSlpMysql import conMysql as mysql
from common.method import reason
from common.runFailed import Retry


@Retry(max_n=3)
class TestPayCreate(unittest.TestCase):

	def test_01_businessPayGiftToGs(self, des='打赏者,贵族爵位=骑士(lv1,1倍)消费,vip经验值1:1增加'):
		"""
		用例描述：
		验证余额足够时，商业房打赏礼物给GS分成为：60，且收入在公会魅力值
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.房间打赏礼物（打赏100分）
		3.校验接口状态和返回值数据
		4.检查被打赏者余额，预期为：1000 * 0.6 =600 (money_cash)
		"""
		rid = gs_soundchat_rid
		assert_equal(mysql.checkRidFactoryType(rid), "business-soundchat")  # 确认rid是直播房
		uid = gsUid
		mysql.updateMoneySql(payUid, default_money)
		mysql.updateMoneySql(uid)
		mysql.updateUserGodSql(uid, 1)
		mysql.deleteUserAccountSql('user_commodity', payUid)
		data = encodeData(
			rid=rid,
			payType='package',
			uid=uid,
			giftId=giftId['69']['gid']
		)
		res = post_request_session(pay_url, data, tokenName='slp')
		assert_code(res['code'])
		assert_body(res['body'], 'success', 1, reason(des, res))
		assert_equal(mysql.selectUserInfoSql('single_money', uid, money_type='money_cash'),
		             giftId['69']['price'] * default_num * rates['gs']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', uid), giftId['69']['price'] * default_num * rates['gs']['default'])
		assert_equal(mysql.selectUserInfoSql('sum_money', payUid), default_money - giftId['69']['price'] * default_num)
		case_list_b[des] = result
		# 关闭贵族,还原数据
		# mysql.deleteUserAccountSql('user_title_new',uid)
		# 开通贵族
		# 修改贵族等级
		# vip值xs_user_profile,人气值xs_user_popularity