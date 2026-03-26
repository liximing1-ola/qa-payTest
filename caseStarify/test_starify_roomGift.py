import unittest

from caseStarify.deal_data import deal_pay_data
from caseStarify.need_data import *
from caseStarify.tools import hash_key
from common.Assert import assert_code, assert_body, assert_equal, assert_between
from common.Config import config
from common.Consts import case_list, result
from common.Request import post_request_session_starify
from common.conStarifyMysql import conMysql
from common.method import reason_starify
from common.runFailed import Retry


@Retry(max_n=2)
class TestPayCreate(unittest.TestCase):

    def test_room_001(self, des='房间打赏,星币余额充足,礼物=摩登派对,返奖15%～20%'):
        commodity = commodity_config['10']
        #  sql:打赏者starify_payUid 修改余额=19999
        conMysql.updateMoneySql(starify_payUid, 19999)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01], )
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*15% ～ 19999*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']),
                       int(commodity['price'] * commodity['reward_upper']))
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), commodity['wealth'] * (1 * 1 - 0))
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), commodity['charm'] * 1)
        case_list[des] = result

    def test_room_002(self, des='房间打赏,星币余额=0'):
        commodity = commodity_config['10']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01], )
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), 0)
        case_list[des] = result

    def test_room_003(self, des='房间打赏,星币余额<礼物价值'):
        commodity = commodity_config['10']
        #  sql:打赏者starify_payUid 修改余额=19998
        conMysql.updateMoneySql(starify_payUid, 19998)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01], )
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=19998
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 19998)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), 0)
        case_list[des] = result

    def test_room_004(self, des='房间打赏,星币余额充足,打赏多人,礼物=聲霸天下,返奖5%～10%'):
        commodity = commodity_config['9']
        #  sql:打赏者starify_payUid 修改余额=5200*2(人数)=10400
        conMysql.updateMoneySql(starify_payUid, 10400)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        #  sql:被打赏者starify_rewardUid02 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid02, 0)
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=5200*5% ～ 5200*10%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']),
                       int(commodity['price'] * commodity['reward_upper']))
        #  sql:被打赏者starify_rewardUid02 查询余额=5200*5% ～ 5200*10%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02),
                       int(commodity['price'] * commodity['reward_lower']),
                       int(commodity['price'] * commodity['reward_upper']))
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), commodity['wealth'] * (2 * 1 - 0))
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), commodity['charm'] * 1)
        #  sql:被打赏者starify_rewardUid02 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid02), commodity['charm'] * 1)
        case_list[des] = result

    def test_room_005(self, des='房间打赏,打赏多人,星币余额=0'):
        commodity = commodity_config['9']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        #  sql:被打赏者starify_rewardUid02 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid02, 0)
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        #  sql:被打赏者starify_rewardUid02 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), 0)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), 0)
        #  sql:被打赏者starify_rewardUid02 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid02), 0)
        case_list[des] = result

    def test_room_006(self, des='房间打赏,打赏多人,星币余额<礼物价值*打赏人数'):
        commodity = commodity_config['9']
        #  sql:打赏者starify_payUid 修改余额=5200*2(人数)-1=10399
        conMysql.updateMoneySql(starify_payUid, 10399)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        #  sql:被打赏者starify_rewardUid02 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid02, 0)
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=10399
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 10399)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        #  sql:被打赏者starify_rewardUid02 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), 0)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), 0)
        #  sql:被打赏者starify_rewardUid02 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid02), 0)
        case_list[des] = result

    def test_room_007(self, des='房间打赏,打赏多人,星币+背包组合支付,星币余额充足,礼物=摩登派对,返奖15%～20%'):
        commodity = commodity_config['10']
        #  sql:打赏者starify_payUid 修改余额=19999
        conMysql.updateMoneySql(starify_payUid, 19999)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*1个
        conMysql.insertXsUserCommodity(starify_payUid, commodity['cid'], 1)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        #  sql:被打赏者starify_rewardUid02 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid02, 0)
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空,摩登派對-1
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*15% ～ 19999*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']),
                       int(commodity['price'] * commodity['reward_upper']))
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*15% ～ 19999*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02),
                       int(commodity['price'] * commodity['reward_lower']),
                       int(commodity['price'] * commodity['reward_upper']))
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), commodity['wealth'] * (2 * 1 - 1))
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), commodity['charm'] * 1)
        #  sql:被打赏者starify_rewardUid02 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid02), commodity['charm'] * 1)
        case_list[des] = result

    def test_room_008(self, des='房间打赏,打赏多人,星币+背包组合支付,星币余额=0'):
        commodity = commodity_config['10']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*1个
        conMysql.insertXsUserCommodity(starify_payUid, commodity['cid'], 1)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        #  sql:被打赏者starify_rewardUid02 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid02, 0)
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=摩登派對*1
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 1)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        #  sql:被打赏者starify_rewardUid02 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), 0)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), 0)
        #  sql:被打赏者starify_rewardUid02 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid02), 0)
        case_list[des] = result

    def test_room_009(self, des='房间打赏,打赏多人,星币+背包组合支付,星币余额<礼物价值'):
        commodity = commodity_config['9']
        #  sql:打赏者starify_payUid 修改余额=5200-1=5199
        conMysql.updateMoneySql(starify_payUid, 5199)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 背包增加礼物:聲霸天下*1个
        conMysql.insertXsUserCommodity(starify_payUid, commodity['cid'], 1)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        #  sql:被打赏者starify_rewardUid02 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid02, 0)
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=5199
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 5199)
        #  sql:打赏者starify_payUid 背包礼物=聲霸天下*1
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 1)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        #  sql:被打赏者starify_rewardUid02 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), 0)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), 0)
        #  sql:被打赏者starify_rewardUid02 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid02), 0)
        case_list[des] = result

    def test_room_010(self, des='房间打赏,背包支付,剩余礼物数充足,礼物=聲霸天下,返奖5%～10%'):
        commodity = commodity_config['9']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 背包增加礼物:聲霸天下*1个
        conMysql.insertXsUserCommodity(starify_payUid, commodity['cid'], 1)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01], )
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空,聲霸天下-1
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=5200*5% ～ 5200*10%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']),
                       int(commodity['price'] * commodity['reward_upper']))
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), commodity['wealth'] * (1 * 1 - 1))
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), commodity['charm'] * 1)
        case_list[des] = result

    def test_room_011(self, des='房间打赏,背包支付,剩余礼物数=0'):
        commodity = commodity_config['9']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01], )
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), 0)
        case_list[des] = result

    def test_room_012(self, des='房间打赏,背包支付,打赏多人,剩余礼物数充足,礼物=摩登派对,返奖15%～20%'):
        commodity = commodity_config['10']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*2个
        conMysql.insertXsUserCommodity(starify_payUid, commodity['cid'], 2)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        #  sql:被打赏者starify_rewardUid02 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid02, 0)
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=聲霸天下-2
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*15% ～ 19999*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']),
                       int(commodity['price'] * commodity['reward_upper']))
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*15% ～ 19999*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02),
                       int(commodity['price'] * commodity['reward_lower']),
                       int(commodity['price'] * commodity['reward_upper']))
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), commodity['wealth'] * (2 * 1 - 2))
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), commodity['charm'] * 1)
        #  sql:被打赏者starify_rewardUid02 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid02), commodity['charm'] * 1)
        case_list[des] = result

    def test_room_013(self, des='房间打赏,背包支付,打赏多人,剩余礼物数=0'):
        commodity = commodity_config['10']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        #  sql:被打赏者starify_rewardUid02 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid02, 0)
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        #  sql:被打赏者starify_rewardUid02 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), 0)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), 0)
        case_list[des] = result

    def test_room_014(self, des='房间打赏,背包支付,打赏多人,剩余礼物数<打赏人数'):
        commodity = commodity_config['10']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*1个
        conMysql.insertXsUserCommodity(starify_payUid, commodity['cid'], 1)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        #  sql:被打赏者starify_rewardUid02 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid02, 0)
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=摩登派對*1
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 1)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        #  sql:被打赏者starify_rewardUid02 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02), 0)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), 0)
        #  sql:被打赏者starify_rewardUid02 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid02), 0)
        case_list[des] = result

    def test_room_015(self, des='房间打赏,星币余额充足,连击数=3'):
        commodity = commodity_config['10']
        #  sql:打赏者starify_payUid 修改余额=19999*3(连击数)
        conMysql.updateMoneySql(starify_payUid, 19999 * 3)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        combo_key = hash_key()  # 连击KEY
        # 1 连击*1
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01], hit_offset=1,
                             combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=19999*2
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 19999 * 2)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']) * 1,
                       int(commodity['price'] * commodity['reward_upper']) * 1)
        # 2 连击*2
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01], hit_offset=2,
                             combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*3*15% ~ 19999*3*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']) * 3,
                       int(commodity['price'] * commodity['reward_upper']) * 3)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), commodity['wealth'] * (1 * 3 - 0))
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), commodity['charm'] * 3)
        case_list[des] = result

    def test_room_016(self, des='房间打赏,背包礼物数+星币余额充足,连击数=3'):
        commodity = commodity_config['10']
        #  sql:打赏者starify_payUid 修改余额=19999*2(连击数)
        conMysql.updateMoneySql(starify_payUid, 19999 * 2)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*1个
        conMysql.insertXsUserCommodity(starify_payUid, commodity['cid'], 1)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        combo_key = hash_key()  # 连击KEY
        # 1 连击
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01], hit_offset=1,
                             combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=19999*2
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 19999 * 2)
        #  sql:打赏者starify_payUid 背包礼物=空,摩登派對-1
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']) * 1,
                       int(commodity['price'] * commodity['reward_upper']) * 1)
        # 2 连击
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01], hit_offset=2,
                             combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空,摩登派對-1
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*3*15% ~ 19999*3*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']) * 3,
                       int(commodity['price'] * commodity['reward_upper']) * 3)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), commodity['wealth'] * (1 * 3 - 1))
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), commodity['charm'] * 3)
        case_list[des] = result

    def test_room_017(self, des='房间打赏,背包礼物数充足,连击数=3'):
        commodity = commodity_config['10']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*3个
        conMysql.insertXsUserCommodity(starify_payUid, commodity['cid'], 3)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        combo_key = hash_key()  # 连击KEY
        # 1 连击
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01], hit_offset=1,
                             combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空,摩登派對-1
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 2)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']) * 1,
                       int(commodity['price'] * commodity['reward_upper']) * 1)
        # 2 连击
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01], hit_offset=2,
                             combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空,摩登派對-3
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*3*15% ~ 19999*3*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']) * 3,
                       int(commodity['price'] * commodity['reward_upper']) * 3)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), commodity['wealth'] * (1 * 3 - 3))
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), commodity['charm'] * 3)
        case_list[des] = result

    def test_room_018(self, des='房间打赏,星币余额充足,打赏多人,连击数=3'):
        commodity = commodity_config['10']
        #  sql:打赏者starify_payUid 修改余额=19999*3(连击数)*2
        conMysql.updateMoneySql(starify_payUid, 19999 * 3 * 2)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        #  sql:被打赏者starify_rewardUid02 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid02, 0)
        combo_key = hash_key()  # 连击KEY
        # 1 连击
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02],
                             hit_offset=1, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=19999*2*2
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 19999 * (3 - 1) * 2)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']) * 1,
                       int(commodity['price'] * commodity['reward_upper']) * 1)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02),
                       int(commodity['price'] * commodity['reward_lower']) * 1,
                       int(commodity['price'] * commodity['reward_upper']) * 1)
        # 2 连击
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02],
                             hit_offset=2, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*3*15% ~ 19999*3*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']) * 3,
                       int(commodity['price'] * commodity['reward_upper']) * 3)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*3*15% ~ 19999*3*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02),
                       int(commodity['price'] * commodity['reward_lower']) * 3,
                       int(commodity['price'] * commodity['reward_upper']) * 3)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), commodity['wealth'] * (2 * 3 - 0))
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), commodity['charm'] * 3)
        #  sql:被打赏者starify_rewardUid02 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid02), commodity['charm'] * 3)
        case_list[des] = result

    def test_room_019(self, des='房间打赏,情况1,背包礼物数+星币余额充足,打赏多人,连击数=3'):
        commodity = commodity_config['10']
        #  sql:打赏者starify_payUid 修改余额=19999*5
        conMysql.updateMoneySql(starify_payUid, 19999 * 5)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*1
        conMysql.insertXsUserCommodity(starify_payUid, commodity['cid'], 1)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        #  sql:被打赏者starify_rewardUid02 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid02, 0)
        combo_key = hash_key()  # 连击KEY
        # 1 连击
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02],
                             hit_offset=1, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=19999*(5-1)
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 19999 * (5 - 1))
        #  sql:打赏者starify_payUid 背包礼物=1-1
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 1 - 1)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']) * 1,
                       int(commodity['price'] * commodity['reward_upper']) * 1)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02),
                       int(commodity['price'] * commodity['reward_lower']) * 1,
                       int(commodity['price'] * commodity['reward_upper']) * 1)
        # 2 连击
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02],
                             hit_offset=2, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*2*15% ~ 19999*2*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']) * 3,
                       int(commodity['price'] * commodity['reward_upper']) * 3)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*2*15% ~ 19999*2*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02),
                       int(commodity['price'] * commodity['reward_lower']) * 3,
                       int(commodity['price'] * commodity['reward_upper']) * 3)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), commodity['wealth'] * (2 * 3 - 1))
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), commodity['charm'] * 3)
        #  sql:被打赏者starify_rewardUid02 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid02), commodity['charm'] * 3)
        case_list[des] = result

    def test_room_020(self, des='房间打赏,情况2,背包礼物数+星币余额充足,打赏多人,连击数=3'):
        commodity = commodity_config['10']
        #  sql:打赏者starify_payUid 修改余额=19999*4(连击数)
        conMysql.updateMoneySql(starify_payUid, 19999 * 4)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*2
        conMysql.insertXsUserCommodity(starify_payUid, commodity['cid'], 2)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        #  sql:被打赏者starify_rewardUid02 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid02, 0)
        combo_key = hash_key()  # 连击KEY
        # 1 连击
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02],
                             hit_offset=1, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=19999 * 4
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 19999 * (4 - 0))
        #  sql:打赏者starify_payUid 背包礼物=2-2
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 2 - 2)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']) * 1,
                       int(commodity['price'] * commodity['reward_upper']) * 1)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02),
                       int(commodity['price'] * commodity['reward_lower']) * 1,
                       int(commodity['price'] * commodity['reward_upper']) * 1)
        # 2 连击
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02],
                             hit_offset=2, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*2*15% ~ 19999*2*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']) * 3,
                       int(commodity['price'] * commodity['reward_upper']) * 3)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*2*15% ~ 19999*2*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02),
                       int(commodity['price'] * commodity['reward_lower']) * 3,
                       int(commodity['price'] * commodity['reward_upper']) * 3)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), commodity['wealth'] * (2 * 3 - 2))
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), commodity['charm'] * 3)
        #  sql:被打赏者starify_rewardUid02 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid02), commodity['charm'] * 3)
        case_list[des] = result

    def test_room_021(self, des='房间打赏,情况3,背包礼物数+星币余额充足,打赏多人,连击数=3'):
        commodity = commodity_config['10']
        #  sql:打赏者starify_payUid 修改余额=19999*3(连击数)
        conMysql.updateMoneySql(starify_payUid, 19999 * 3)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*3
        conMysql.insertXsUserCommodity(starify_payUid, commodity['cid'], 3)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        #  sql:被打赏者starify_rewardUid02 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid02, 0)
        combo_key = hash_key()  # 连击KEY
        # 1 连击
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02],
                             hit_offset=1, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=19999 * 3
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 19999 * 3)
        #  sql:打赏者starify_payUid 背包礼物=3-2
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 3 - 2)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']) * 1,
                       int(commodity['price'] * commodity['reward_upper']) * 1)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02),
                       int(commodity['price'] * commodity['reward_lower']) * 1,
                       int(commodity['price'] * commodity['reward_upper']) * 1)
        # 2 连击
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02],
                             hit_offset=2, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*2*15% ~ 19999*2*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']) * 3,
                       int(commodity['price'] * commodity['reward_upper']) * 3)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*2*15% ~ 19999*2*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02),
                       int(commodity['price'] * commodity['reward_lower']) * 3,
                       int(commodity['price'] * commodity['reward_upper']) * 3)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), commodity['wealth'] * (2 * 3 - 3))
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), commodity['charm'] * 3)
        #  sql:被打赏者starify_rewardUid02 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid02), commodity['charm'] * 3)
        case_list[des] = result

    def test_room_022(self, des='房间打赏,背包礼物数充足,打赏多人,连击数=3'):
        commodity = commodity_config['10']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 背包增加礼物:摩登派對*6
        conMysql.insertXsUserCommodity(starify_payUid, commodity['cid'], 6)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid02 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid02, 0)
        #  sql:被打赏者starify_rewardUid02 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid02, 0)
        combo_key = hash_key()  # 连击KEY
        # 1 连击
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02],
                             hit_offset=1, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=6-2
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 6 - 2)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']) * 1,
                       int(commodity['price'] * commodity['reward_upper']) * 1)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*1*15% ~ 19999*1*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02),
                       int(commodity['price'] * commodity['reward_lower']) * 1,
                       int(commodity['price'] * commodity['reward_upper']) * 1)
        # 2 连击
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01, starify_rewardUid02],
                             hit_offset=2, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 背包礼物=空
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=19999*2*15% ~ 19999*2*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                       int(commodity['price'] * commodity['reward_lower']) * 3,
                       int(commodity['price'] * commodity['reward_upper']) * 3)
        #  sql:被打赏者starify_rewardUid02 查询余额=19999*2*15% ~ 19999*2*20%
        assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid02),
                       int(commodity['price'] * commodity['reward_lower']) * 3,
                       int(commodity['price'] * commodity['reward_upper']) * 3)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), commodity['wealth'] * (2 * 3 - 6))
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), commodity['charm'] * 3)
        #  sql:被打赏者starify_rewardUid02 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid02), commodity['charm'] * 3)
        case_list[des] = result

    def test_room_023(self, des='房间打赏,打赏3~8号礼物种类,不返奖'):
        # 打赏编号3~8的礼物,不返奖
        money = 100000
        wealth = 0
        charm = 0
        #  sql:打赏者starify_payUid 修改余额=100000
        conMysql.updateMoneySql(starify_payUid, money)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        for i in range(3, 9):
            commodity = commodity_config[str(i)]
            data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01], )
            res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
            assert_code(res['code'])
            assert_body(res['body'], 'success', True, reason_starify(des, res))
            #  sql:打赏者starify_payUid 查询余额=100000-gift['price']
            money -= commodity['price']
            wealth += commodity['wealth']
            charm += commodity['charm']
            assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), money)
            #  sql:被打赏者starify_rewardUid01 查询余额=0
            assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)

            #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
            assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), wealth)
            #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
            assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), charm)
        case_list[des] = result

    def test_room_024(self, des='房间打赏,送>当前财富等级的特权礼物'):

        for lv in range(0, 6):  # 财富等级 0~5级有限制,6级无限制
            for gift_lv in range(lv + 1, 7):  # 特权礼物等级
                commodity = commodity_config[f'lv{gift_lv}']
                #  sql:打赏者starify_payUid 修改余额=50000
                conMysql.updateMoneySql(starify_payUid, 50000)
                #  sql:打赏者starify_payUid 清空背包礼物
                conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
                #  sql:打赏者starify_payUid 修改财富值=0
                conMysql.updateWealthSql(starify_payUid, wealth_lv[f'lv{lv}']['min'])
                #  sql:被打赏者starify_rewardUid01 修改余额=0
                conMysql.updateMoneySql(starify_rewardUid01, 0)
                #  sql:被打赏者starify_rewardUid01 修改魅力值=0
                conMysql.updateCharmSql(starify_rewardUid01, 0)
                data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01], )
                res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
                assert_code(res['code'])
                assert_body(res['body'], 'msg', "当前特权级别无法使用此礼物", reason_starify(des, res))

                #  sql:打赏者starify_payUid 查询余额=0
                assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 50000)
                #  sql:被打赏者starify_rewardUid01 查询余额=0
                assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
                #  sql:打赏者starify_payUid 查询-财富值=0
                assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), wealth_lv[f'lv{lv}']['min'])
                #  sql:被打赏者starify_rewardUid01 查询-魅力值=0
                assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), 0)
        case_list[des] = result

    def test_room_025(self, des='房间打赏,送<=当前财富等级的特权礼物'):
        for lv in range(1, 7):  # 财富等级
            for gift_lv in range(1, lv + 1):  # 特权礼物等级
                commodity = commodity_config[f'lv{gift_lv}']
                #  sql:打赏者starify_payUid 修改余额=50000
                conMysql.updateMoneySql(starify_payUid, 50000)
                #  sql:打赏者starify_payUid 清空背包礼物
                conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
                #  sql:打赏者starify_payUid 修改财富值=0
                conMysql.updateWealthSql(starify_payUid, wealth_lv[f'lv{lv}']['min'])
                #  sql:被打赏者starify_rewardUid01 修改余额=0
                conMysql.updateMoneySql(starify_rewardUid01, 0)
                #  sql:被打赏者starify_rewardUid01 修改魅力值=0
                conMysql.updateCharmSql(starify_rewardUid01, 0)
                data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01], )
                res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
                assert_code(res['code'])
                assert_body(res['body'], 'success', True, reason_starify(des, res))

                #  sql:打赏者starify_payUid 查询余额=0
                assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 50000 - commodity['price'])
                if gift_lv in [5, 6]:  # lv5~lv6分成
                    assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                                   int(commodity['price'] * commodity['reward_lower']),
                                   int(commodity['price'] * commodity['reward_upper']))
                else:  # lv1~lv4礼物,不分成
                    #  sql:被打赏者starify_rewardUid01 查询余额=0
                    assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
                #  sql:打赏者starify_payUid 查询-财富值=礼物价值*(人数*连击数-背包礼物数)
                assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid),
                             wealth_lv[f'lv{lv}']['min'] + commodity['wealth'] * (1 * 1 - 0))
                #  sql:被打赏者starify_rewardUid01 查询-魅力值=0
                assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), commodity['charm'])
        case_list[des] = result

    def test_room_026(self, des='房间打赏,背包支付,礼物=日常宝箱-免费礼物(下架状态)'):
        commodity = commodity_config['51']
        #  sql:打赏者starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 清空背包礼物
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 背包增加礼物:免费礼物*1个
        conMysql.insertXsUserCommodity(starify_payUid, commodity['cid'], 1)
        #  sql:被打赏者starify_rewardUid01 修改余额=0
        conMysql.updateMoneySql(starify_rewardUid01, 0)
        #  sql:被打赏者starify_rewardUid01 修改魅力值=0
        conMysql.updateCharmSql(starify_rewardUid01, 0)
        data = deal_pay_data("room", commodity, to_uids=[starify_rewardUid01], )
        res = post_request_session_starify(config.starify_pay_url, data, token_name='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:打赏者starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        #  sql:打赏者starify_payUid 查询-财富值=0
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), 0)
        #  sql:被打赏者starify_rewardUid01 查询-魅力值=礼物对应魅力值*连击数
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), 0)
        case_list[des] = result