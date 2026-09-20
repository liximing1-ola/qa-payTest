# -*- encoding=utf8 -*-
__author__ = "Wu.Zhenxing"
__title__ = ""
__desc__ = "甄选礼盒"

from caseSlp.base import SlpCase, SlpTestBase
from caseSlp.config import gsUid, juewei_level, normal_uid, payUid, rates, zx_box
from common.Assert import assert_equal
from common.conSlpMysql import conMysql as mysql
from common.runFailed import Retry

# 礼盒打赏后等待结算数据落库的时长（秒）
BOX_SETTLE_WAIT = 5

# 送礼人爵位=亲王(vip=1.2倍)
_JW = juewei_level['亲王']
# 送礼人初始余额
BASE_MONEY = 10000000


def _validate_zx_box_settle(ctx):
	"""校验收礼人气值/分成、送礼人VIP值/贵族成长值/扣费"""
	send_gift_data = mysql.selectZxPayData(payUid)
	# 校验收礼人气值
	normal_rq_total = 0
	gs_rq_total = 0
	normal_fencheng_total = 0
	gs_fencheng_total = 0
	for data in send_gift_data:
		if int(data['to_uid']) == gsUid:
			price = zx_box['6'][data['gid']]['price']
			RQ = zx_box['6'][data['gid']]['RQ']
			total_num = int(data['total_num'])
			gs_rq_total += price * RQ * total_num
			gs_fencheng_total += price * total_num
		if int(data['to_uid']) == normal_uid:
			price = zx_box['6'][data['gid']]['price']
			RQ = zx_box['6'][data['gid']]['RQ']
			total_num = int(data['total_num'])
			normal_rq_total += price * RQ * total_num
			normal_fencheng_total += price * total_num
	assert_equal(mysql.selectUserInfoSql("popularity", normal_uid), normal_rq_total)
	assert_equal(mysql.selectUserInfoSql("popularity", gsUid), gs_rq_total)
	# 校验收礼人分成
	assert_equal(mysql.selectUserInfoSql('single_money', gsUid, 'money_cash'), gs_fencheng_total * rates['gs']['default'])
	assert_equal(mysql.selectUserInfoSql('single_money', normal_uid, 'money_cash_b'), normal_fencheng_total * rates['normal']['default'])
	# 校验送礼人VIP值
	pay_vip_total = 0
	for data in send_gift_data:
		price = zx_box['6'][data['gid']]['price']
		VIP = zx_box['6'][data['gid']]['VIP']
		total_num = int(data['total_num'])
		pay_vip_total += price * VIP * total_num
	assert_equal(mysql.selectUserInfoSql("pay_room_money", payUid), pay_vip_total * _JW['update'] / 100)

	# 校验送礼人贵族成长值
	pay_czz_total = 0
	for data in send_gift_data:
		price = zx_box['6'][data['gid']]['price']
		CZZ = zx_box['6'][data['gid']]['CZZ']
		total_num = int(data['total_num'])
		if price >= 10000:  # 大于10000钻+送礼人成长值
			pay_czz_total += price * CZZ * total_num
	assert_equal(mysql.selectUserInfoSql("growth", payUid), pay_czz_total + _JW['base'])

	# 校验送礼人扣费
	pay_total_money = 0
	for data in send_gift_data:
		price = zx_box['6'][data['gid']]['price']
		total_num = int(data['total_num'])
		pay_total_money += price * total_num
	assert_equal(mysql.selectUserInfoSql('sum_money', payUid), BASE_MONEY - pay_total_money)


# 场景：送礼人=亲王(vip=1.2倍),甄选礼盒(6元),送多人多个
SCENE_001 = SlpCase(
	des='送礼人=亲王(vip=1.2倍),甄选礼盒(6元),送多人多个',
	setup=[
		{'action': 'clear_user_money', 'uids': [payUid, normal_uid, gsUid]},
		{'action': 'delete_commodity', 'uid': payUid},
		{'action': 'delete_user_account',
		 'params': {'table': 'user_title_new', 'uid': payUid}},  # 关闭贵族,还原数据
		{'action': 'update_user_god', 'params': {'uid': gsUid, 'god': 1}},
		# 清除打赏流水
		{'action': 'delete_user_account', 'params': {'table': 'pay_change', 'uid': payUid}},
		# 清空人气值
		{'action': 'delete_user_account', 'params': {'table': 'user_popularity', 'uid': normal_uid}},
		{'action': 'delete_user_account', 'params': {'table': 'user_popularity', 'uid': gsUid}},
		# 清空VIP值
		{'action': 'delete_user_account', 'params': {'table': 'pay_room_money', 'uid': payUid}},
		# 开启爵位
		{'action': 'update_user_title', 'params': {'uid': payUid, 'level': _JW['level']}},
		{'action': 'update_money', 'params': {'uid': payUid, 'money': BASE_MONEY}},
	],
	data={
		'payType': 'zx_box',
		'num': 1000,
		'gift_id': zx_box['6']['gid'],
		'price': zx_box['6']['price'],
		'uids': ('{}'.format(normal_uid), '{}'.format(gsUid)),
	},
	post_wait=BOX_SETTLE_WAIT,
	checks=[{'assert_func': _validate_zx_box_settle}],
)


@Retry(max_n=3)
class TestPayCreate(SlpTestBase):

	def test_001(self, des='送礼人=亲王(vip=1.2倍),甄选礼盒(6元),送多人多个'):
		"""
		用例描述：
		甄选礼盒,送礼人爵位=亲王,送多人多个场景
		脚本步骤：
		1.构造打赏者和被打赏者数据
		2.私聊一对一打赏流程(礼物:棒棒糖)
		3.校验接口和返回值数据
		4.检查预期返回msg，预期：支付失败，提示Toast
		5.检查被打赏者余额,预期：0
		"""
		self.run_case(SCENE_001)
