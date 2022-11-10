# import math
# import unittest
#
# from caseStarify.deal_data import deal_pay_data
# from caseStarify.need_data import *
# from caseStarify.tools import deal_num
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
#     def test_shop_001(self, des='星币充足,商城购买-头像框,3天'):
#         commodity = commodity_config['header']
#         sale_level = 1
#         #  sql:打赏者starify_payUid 修改余额=10000
#         conMysql.updateMoneySql(starify_payUid, 100000)
#         #  sql:打赏者starify_payUid 清空背包礼物
#         conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
#         data = deal_pay_data("shop_buy", commodity, sale_level=sale_level)
#         res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
#         assert_code(res['code'])
#         assert_body(res['body'], 'success', True, reason_starify(des, res))
#         #  sql:starify_payUid 查询余额=0
#         cost = deal_num(commodity[f'level_{sale_level}']['day'] * commodity[f'level_{sale_level}']['rate'] * commodity[
#             'price'])
#         assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 100000 - cost)
#         #  sql:检查背包物品=1
#         assert_equal(conMysql.selectUserInfoSql('commodity_num', starify_payUid, commodity['cid'], 86400 * 3), 1)
#         case_list[des] = result
#
#     def test_shop_002(self, des='星币充足,商城购买-头像框,7天'):
#         commodity = commodity_config['header']
#         sale_level = 2
#         #  sql:打赏者starify_payUid 修改余额=10000
#         conMysql.updateMoneySql(starify_payUid, 100000)
#         #  sql:打赏者starify_payUid 清空背包礼物
#         conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
#         data = deal_pay_data("shop_buy", commodity, sale_level=sale_level)
#         res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
#         assert_code(res['code'])
#         assert_body(res['body'], 'success', True, reason_starify(des, res))
#         #  sql:starify_payUid 查询余额=0
#         cost = deal_num(commodity[f'level_{sale_level}']['day'] * commodity[f'level_{sale_level}']['rate'] * commodity[
#             'price'])
#         assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 100000 - cost)
#         #  sql:检查背包物品=1
#         assert_equal(conMysql.selectUserInfoSql('commodity_num', starify_payUid, commodity['cid'], 86400 * 7), 1)
#         case_list[des] = result
#
#     def test_shop_003(self, des='星币充足,商城购买-头像框,15天'):
#         commodity = commodity_config['header']
#         sale_level = 3
#         #  sql:打赏者starify_payUid 修改余额=10000
#         conMysql.updateMoneySql(starify_payUid, 100000)
#         #  sql:打赏者starify_payUid 清空背包礼物
#         conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
#         data = deal_pay_data("shop_buy", commodity, sale_level=sale_level)
#         res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
#         assert_code(res['code'])
#         assert_body(res['body'], 'success', True, reason_starify(des, res))
#         #  sql:starify_payUid 查询余额=0
#         cost = deal_num(commodity[f'level_{sale_level}']['day'] * commodity[f'level_{sale_level}']['rate'] * commodity[
#             'price'])
#         assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 100000 - cost)
#         #  sql:检查背包物品=1
#         assert_equal(conMysql.selectUserInfoSql('commodity_num', starify_payUid, commodity['cid'], 86400 * 15), 1)
#         case_list[des] = result
#
#     def test_shop_004(self, des='星币充足,商城购买-进场横幅,3天'):
#         commodity = commodity_config['effect']
#         sale_level = 1
#         #  sql:打赏者starify_payUid 修改余额=10000
#         conMysql.updateMoneySql(starify_payUid, 100000)
#         #  sql:打赏者starify_payUid 清空背包礼物
#         conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
#         data = deal_pay_data("shop_buy", commodity, sale_level=sale_level)
#         res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
#         assert_code(res['code'])
#         assert_body(res['body'], 'success', True, reason_starify(des, res))
#         #  sql:starify_payUid 查询余额=0
#         cost = deal_num(commodity[f'level_{sale_level}']['day'] * commodity[f'level_{sale_level}']['rate'] * commodity[
#             'price'])
#         assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 100000 - cost)
#         #  sql:检查背包物品=1
#         assert_equal(conMysql.selectUserInfoSql('commodity_num', starify_payUid, commodity['cid'], 86400 * 3), 1)
#         case_list[des] = result
#
#     def test_shop_005(self, des='星币充足,商城购买-麦上光圈,3天'):
#         commodity = commodity_config['ring']
#         sale_level = 1
#         #  sql:打赏者starify_payUid 修改余额=10000
#         conMysql.updateMoneySql(starify_payUid, 100000)
#         #  sql:打赏者starify_payUid 清空背包礼物
#         conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
#         data = deal_pay_data("shop_buy", commodity, sale_level=sale_level)
#         res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
#         assert_code(res['code'])
#         assert_body(res['body'], 'success', True, reason_starify(des, res))
#         #  sql:starify_payUid 查询余额=0
#         cost = deal_num(commodity[f'level_{sale_level}']['day'] * commodity[f'level_{sale_level}']['rate'] * commodity[
#             'price'])
#         assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 100000 - cost)
#         #  sql:检查背包物品=1
#         assert_equal(conMysql.selectUserInfoSql('commodity_num', starify_payUid, commodity['cid'], 86400 * 3), 1)
#         case_list[des] = result
