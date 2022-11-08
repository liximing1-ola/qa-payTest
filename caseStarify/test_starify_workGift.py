# import unittest
#
# from caseStarify.deal_data import deal_pay_data
# from caseStarify.need_data import *
# from common.Assert import *
# from common.Consts import case_list, result
# # from common.method import reason
# from common.Request import post_request_session_starify
# from common.conStarifyMysql import conMysql
# from common.method import reason_starify
# from common.runFailed import Retry
#
#
# @Retry(max_n=1)
# class TestPayCreate(unittest.TestCase):
#     def test_work_001(self, des='星币余额充足,作品打赏,礼物类型=安可'):
#         gift = gift_config['2']
#         #  sql:清除作品已被打赏的标记
#         conMysql.deleteUserAccountSql("user_work_reward", starify_payUid, starify_work_state['todo'])
#         #  sql:打赏者starify_payUid 修改余额=2
#         conMysql.updateMoneySql(starify_payUid, 2)
#         data = deal_pay_data("work", gift['gift_id'], work_state="todo")
#         res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
#         assert_code(res['code'])
#         assert_body(res['body'], 'success', True, reason_starify(des, res))
#         #  sql:starify_payUid 查询余额=0
#         assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
#         case_list[des] = result
#
#     def test_work_002(self, des='作品打赏,星币余额=0'):
#         gift = gift_config['2']
#         #  sql:清除作品已被打赏的标记
#         conMysql.deleteUserAccountSql("user_work_reward", starify_payUid, starify_work_state['todo'])
#         #  sql:starify_payUid 修改余额=0
#         conMysql.updateMoneySql(starify_payUid, 0)
#         data = deal_pay_data("work", gift['gift_id'], work_state="todo")
#         res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
#         assert_code(res['code'])
#         assert_body(res['body'], 'msg', '支付或打赏失败', reason_starify(des, res))
#         #  sql:starify_payUid 查询余额=0
#         assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
#         case_list[des] = result
# 
#     def test_work_003(self, des='作品打赏,星币余额<礼物价值'):
#         gift = gift_config['2']
#         #  sql:清除作品已被打赏的标记
#         conMysql.deleteUserAccountSql("user_work_reward", starify_payUid, starify_work_state['todo'])
#         #  sql:starify_payUid 修改余额=1
#         conMysql.updateMoneySql(starify_payUid, 1)
#         data = deal_pay_data("work", gift['gift_id'], work_state="todo")
#         res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
#         assert_code(res['code'])
#         assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
#         #  sql:starify_payUid 查询余额=1
#         assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 1)
#         case_list[des] = result
#
#     def test_work_004(self, des='作品打赏,重复打赏'):
#         gift = gift_config['2']
#         #  sql:starify_payUid 修改余额=2
#         conMysql.updateMoneySql(starify_payUid, 2)
#         data = deal_pay_data("work", gift['gift_id'], work_state="done")
#         res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
#         assert_code(res['code'])
#         assert_body(res['body'], 'msg', '同一个星币礼物只能打赏同一个作品一次', reason_starify(des, res))
#         #  sql:starify_payUid 查询余额=2
#         assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 2)
#         case_list[des] = result
#
#     def test_work_005(self, des='作品打赏,星币余额充足,礼物类型=星币'):
#         gift = gift_config['1']
#         #  sql:清除作品已被打赏的标记
#         conMysql.deleteUserAccountSql("user_work_reward", starify_payUid, starify_work_state['todo'])
#         #  sql:starify_payUid 修改余额
#         conMysql.updateMoneySql(starify_payUid, 1)
#         data = deal_pay_data("work", gift['gift_id'], "todo")
#         res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
#         assert_code(res['code'])
#         assert_body(res['body'], 'success', True, reason_starify(des, res))
#         #  sql:starify_payUid 查询余额
#         assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
#         case_list[des] = result