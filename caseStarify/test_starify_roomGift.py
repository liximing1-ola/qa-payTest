import unittest

from caseStarify.deal_data import deal_pay_data
from caseStarify.need_data import *
from caseStarify.tools import hash_key
from common.Assert import assert_code, assert_body, assert_equal, assert_between
from common.Config import config
from common.Consts import case_list, result
from common.Request import post_request_session_starify
from common.conStarifyMysql import conMysql
# from common.method import reason
from common.method import reason_starify
from common.runFailed import Retry


@Retry(max_n=2)
class TestPayCreate(unittest.TestCase):

    def test_room_001(self, des='房间打赏,星币余额充足,礼物=摩登派对,返奖15%～20%'):
        gift = gift_config['10']
        #  sql:打赏者starify_payUid 修改余额=19999
        conMysql.updateMoneySql(starify_payUid, 19999)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*15% ～ 19999*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'],
                       gift['price'] * gift['reward_upper'])
        case_list[des] = result

    def test_room_002(self, des='房间打赏,星币余额=0'):
        gift = gift_config['10']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        case_list[des] = result

    def test_room_003(self, des='房间打赏,星币余额<礼物价值'):
        gift = gift_config['10']
        #  sql:打赏者starify_payUid 修改余额=19998
        conMysql.updateMoneySql(starify_payUid, 19998)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=19998
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 19998)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        case_list[des] = result

    def test_room_004(self, des='房间打赏,星币余额充足,打赏多人,礼物=聲霸天下,返奖10%～15%'):
        gift = gift_config['9']
        #  sql:打赏者starify_payUid 修改余额=5200*2(人数)=10400
        conMysql.updateMoneySql(starify_payUid, 10400)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=5200*10% ～ 5200*15%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'],
                       gift['price'] * gift['reward_upper'])
        #  sql:被打赏者starify_rewardUid02 查询余额=5200*10% ～ 5200*15%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), gift['price'] * gift['reward_lower'],
                       gift['price'] * gift['reward_upper'])
        case_list[des] = result

    def test_room_005(self, des='房间打赏,打赏多人,星币余额=0'):
        gift = gift_config['9']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        #  sql:被打赏者starify_rewardUid02 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), 0)
        case_list[des] = result

    def test_room_006(self, des='房间打赏,打赏多人,星币余额<礼物价值*打赏人数'):
        gift = gift_config['9']
        #  sql:打赏者starify_payUid 修改余额=5200*2(人数)-1=10399
        conMysql.updateMoneySql(starify_payUid, 10399)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=10399
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 10399)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        #  sql:被打赏者starify_rewardUid02 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), 0)
        case_list[des] = result

    def test_room_007(self, des='房间打赏,打赏多人,星币+背包组合支付,星币余额充足,礼物=摩登派对,返奖15%～20%'):
        gift = gift_config['10']
        #  sql:打赏者starify_payUid 修改余额=19999
        conMysql.updateMoneySql(starify_payUid, 19999)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*1个
        conMysql.insertXsUserCommodity(starify_payUid, gift['cid'], 1)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空,摩登派對-1
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*15% ～ 19999*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'],
                       gift['price'] * gift['reward_upper'])
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*15% ～ 19999*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), gift['price'] * gift['reward_lower'],
                       gift['price'] * gift['reward_upper'])
        case_list[des] = result

    def test_room_008(self, des='房间打赏,打赏多人,星币+背包组合支付,星币余额=0'):
        gift = gift_config['10']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*1个
        conMysql.insertXsUserCommodity(starify_payUid, gift['cid'], 1)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=摩登派對*1
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 1)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        #  sql:被打赏者starify_rewardUid02 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), 0)
        case_list[des] = result

    def test_room_009(self, des='房间打赏,打赏多人,星币+背包组合支付,星币余额<礼物价值'):
        gift = gift_config['9']
        #  sql:打赏者starify_payUid 修改余额=5200-1=5199
        conMysql.updateMoneySql(starify_payUid, 5199)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 背包增加礼物:聲霸天下*1个
        conMysql.insertXsUserCommodity(starify_payUid, gift['cid'], 1)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=5199
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 5199)
        #  sql:打赏者starify_payUid 背包礼物=聲霸天下*1
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 1)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        #  sql:被打赏者starify_rewardUid02 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), 0)
        case_list[des] = result

    def test_room_010(self, des='房间打赏,背包支付,剩余礼物数充足,礼物=聲霸天下,返奖10%～15%'):
        gift = gift_config['9']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 背包增加礼物:聲霸天下*1个
        conMysql.insertXsUserCommodity(starify_payUid, gift['cid'], 1)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空,聲霸天下-1
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=5200*10% ～ 5200*15%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'],
                       gift['price'] * gift['reward_upper'])
        case_list[des] = result

    def test_room_011(self, des='房间打赏,背包支付,剩余礼物数=0'):
        gift = gift_config['9']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        case_list[des] = result

    def test_room_012(self, des='房间打赏,背包支付,打赏多人,剩余礼物数充足,礼物=摩登派对,返奖15%～20%'):
        gift = gift_config['10']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*2个
        conMysql.insertXsUserCommodity(starify_payUid, gift['cid'], 2)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=聲霸天下-2
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*15% ～ 19999*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'],
                       gift['price'] * gift['reward_upper'])
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*15% ～ 19999*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), gift['price'] * gift['reward_lower'],
                       gift['price'] * gift['reward_upper'])
        case_list[des] = result

    def test_room_013(self, des='房间打赏,背包支付,打赏多人,剩余礼物数=0'):
        gift = gift_config['10']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        #  sql:被打赏者starify_rewardUid02 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), 0)
        case_list[des] = result

    def test_room_014(self, des='房间打赏,背包支付,打赏多人,剩余礼物数<打赏人数'):
        gift = gift_config['10']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*1个
        conMysql.insertXsUserCommodity(starify_payUid, gift['cid'], 1)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=摩登派對*1
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 1)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        #  sql:被打赏者starify_rewardUid02 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), 0)
        case_list[des] = result

    def test_room_015(self, des='房间打赏,星币余额充足,连击数=3'):
        gift = gift_config['10']
        #  sql:打赏者starify_payUid 修改余额=19999*3(连击数)
        conMysql.updateMoneySql(starify_payUid, 19999 * 3)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        combo_key = hash_key()  # 连击KEY
        # 1 连击*1
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01], hit_offset=1, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=19999*2
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 19999 * 2)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'] * 1,
                       gift['price'] * gift['reward_upper'] * 1)
        # 2 连击*2
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01], hit_offset=2, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*3*15% ~ 19999*3*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'] * 3,
                       gift['price'] * gift['reward_upper'] * 3)
        case_list[des] = result

    def test_room_016(self, des='房间打赏,背包礼物数+星币余额充足,连击数=3'):
        gift = gift_config['10']
        #  sql:打赏者starify_payUid 修改余额=19999*2(连击数)
        conMysql.updateMoneySql(starify_payUid, 19999 * 2)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*1个
        conMysql.insertXsUserCommodity(starify_payUid, gift['cid'], 1)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        combo_key = hash_key()  # 连击KEY
        # 1 连击
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01], hit_offset=1, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=19999*2
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 19999 * 2)
        #  sql:打赏者starify_payUid 背包礼物=空,摩登派對-1
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'] * 1,
                       gift['price'] * gift['reward_upper'] * 1)
        # 2 连击
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01], hit_offset=2, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空,摩登派對-1
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*3*15% ~ 19999*3*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'] * 3,
                       gift['price'] * gift['reward_upper'] * 3)

    def test_room_017(self, des='房间打赏,背包礼物数充足,连击数=3'):
        gift = gift_config['10']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*3个
        conMysql.insertXsUserCommodity(starify_payUid, gift['cid'], 3)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        combo_key = hash_key()  # 连击KEY
        # 1 连击
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01], hit_offset=1, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空,摩登派對-1
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 2)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'] * 1,
                       gift['price'] * gift['reward_upper'] * 1)
        # 2 连击
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01], hit_offset=2, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空,摩登派對-3
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*3*15% ~ 19999*3*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'] * 3,
                       gift['price'] * gift['reward_upper'] * 3)

    def test_room_018(self, des='房间打赏,星币余额充足,打赏多人,连击数=3'):
        gift = gift_config['10']
        #  sql:打赏者starify_payUid 修改余额=19999*3(连击数)*2
        conMysql.updateMoneySql(starify_payUid, 19999 * 3 * 2)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        combo_key = hash_key()  # 连击KEY
        # 1 连击
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], hit_offset=1, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=19999*2*2
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 19999 * (3-1) * 2)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'] * 1,
                       gift['price'] * gift['reward_upper'] * 1)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), gift['price'] * gift['reward_lower'] * 1,
                       gift['price'] * gift['reward_upper'] * 1)
        # 2 连击
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], hit_offset=2, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*3*15% ~ 19999*3*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'] * 3,
                       gift['price'] * gift['reward_upper'] * 3)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*3*15% ~ 19999*3*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), gift['price'] * gift['reward_lower'] * 3,
                       gift['price'] * gift['reward_upper'] * 3)
        case_list[des] = result

    def test_room_019(self, des='房间打赏,情况1,背包礼物数+星币余额充足,打赏多人,连击数=3'):
        gift = gift_config['10']
        #  sql:打赏者starify_payUid 修改余额=19999*5
        conMysql.updateMoneySql(starify_payUid, 19999 * 5)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*1
        conMysql.insertXsUserCommodity(starify_payUid, gift['cid'], 1)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        combo_key = hash_key()  # 连击KEY
        # 1 连击
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], hit_offset=1, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=19999*(5-1)
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 19999 * (5 - 1))
        #  sql:打赏者starify_payUid 背包礼物=1-1
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 1 - 1)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'] * 1,
                       gift['price'] * gift['reward_upper'] * 1)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), gift['price'] * gift['reward_lower'] * 1,
                       gift['price'] * gift['reward_upper'] * 1)
        # 2 连击
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], hit_offset=2, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*2*15% ~ 19999*2*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'] * 3,
                       gift['price'] * gift['reward_upper'] * 3)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*2*15% ~ 19999*2*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), gift['price'] * gift['reward_lower'] * 3,
                       gift['price'] * gift['reward_upper'] * 3)
        case_list[des] = result

    def test_room_020(self, des='房间打赏,情况2,背包礼物数+星币余额充足,打赏多人,连击数=3'):
        gift = gift_config['10']
        #  sql:打赏者starify_payUid 修改余额=19999*4(连击数)
        conMysql.updateMoneySql(starify_payUid, 19999 * 4)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*2
        conMysql.insertXsUserCommodity(starify_payUid, gift['cid'], 2)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        combo_key = hash_key()  # 连击KEY
        # 1 连击
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], hit_offset=1, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=19999 * 4
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 19999 * (4 - 0))
        #  sql:打赏者starify_payUid 背包礼物=2-2
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 2 - 2)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'] * 1,
                       gift['price'] * gift['reward_upper'] * 1)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), gift['price'] * gift['reward_lower'] * 1,
                       gift['price'] * gift['reward_upper'] * 1)
        # 2 连击
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], hit_offset=2, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*2*15% ~ 19999*2*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'] * 3,
                       gift['price'] * gift['reward_upper'] * 3)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*2*15% ~ 19999*2*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), gift['price'] * gift['reward_lower'] * 3,
                       gift['price'] * gift['reward_upper'] * 3)
        case_list[des] = result

    def test_room_021(self, des='房间打赏,情况3,背包礼物数+星币余额充足,打赏多人,连击数=3'):
        gift = gift_config['10']
        #  sql:打赏者starify_payUid 修改余额=19999*3(连击数)
        conMysql.updateMoneySql(starify_payUid, 19999 * 3)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*3
        conMysql.insertXsUserCommodity(starify_payUid, gift['cid'], 3)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        combo_key = hash_key()  # 连击KEY
        # 1 连击
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], hit_offset=1, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=19999 * 3
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 19999 * 3)
        #  sql:打赏者starify_payUid 背包礼物=3-2
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 3 - 2)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'] * 1,
                       gift['price'] * gift['reward_upper'] * 1)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), gift['price'] * gift['reward_lower'] * 1,
                       gift['price'] * gift['reward_upper'] * 1)
        # 2 连击
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], hit_offset=2, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*2*15% ~ 19999*2*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'] * 3,
                       gift['price'] * gift['reward_upper'] * 3)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*2*15% ~ 19999*2*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), gift['price'] * gift['reward_lower'] * 3,
                       gift['price'] * gift['reward_upper'] * 3)
        case_list[des] = result

    def test_room_022(self, des='房间打赏,背包礼物数充足,打赏多人,连击数=3'):
        gift = gift_config['10']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*6
        conMysql.insertXsUserCommodity(starify_payUid, gift['cid'], 6)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        combo_key = hash_key()  # 连击KEY
        # 1 连击
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], hit_offset=1, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=6-2
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 6 - 2)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'] * 1,
                       gift['price'] * gift['reward_upper'] * 1)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), gift['price'] * gift['reward_lower'] * 1,
                       gift['price'] * gift['reward_upper'] * 1)
        # 2 连击
        data = deal_pay_data("room", gift['gift_id'], to_uids=[starify_rewardUid01, starify_rewardUid02], hit_offset=2, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, gift['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*2*15% ~ 19999*2*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), gift['price'] * gift['reward_lower'] * 3,
                       gift['price'] * gift['reward_upper'] * 3)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*2*15% ~ 19999*2*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), gift['price'] * gift['reward_lower'] * 3,
                       gift['price'] * gift['reward_upper'] * 3)
        case_list[des] = result
