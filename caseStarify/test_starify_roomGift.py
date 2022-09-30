import unittest

from caseStarify.deal_data import deal_pay_data
from caseStarify.need_data import *
from caseStarify.tools import hash_key
from common.Assert import assert_code, assert_body
from common.Config import config
from common.Consts import case_list, result
from common.Request import post_request_session_starify
# from common.conPtMysql import conMysql
# from common.method import reason
from common.method import reason_starify
from common.runFailed import Retry


@Retry(max_n=1)
class TestPayCreate(unittest.TestCase):

    def test_work_01(self, des='星币充足,房间星币打赏,礼物=摩登派对'):
        # todo sql:清除作品已被打赏的标记
        # todo sql:starify_payUid 修改余额
        data = deal_pay_data("room", "10", to_uids=[starify_rewardUid01], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # todo sql:starify_payUid 查询余额
        case_list[des] = result

    def test_work_02(self, des='星币充足,房间星币打赏,多人,礼物=聲霸天下'):
        # todo sql:清除作品已被打赏的标记
        # todo sql:starify_payUid 修改余额
        data = deal_pay_data("room", "9", to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # todo sql:starify_payUid 查询余额
        case_list[des] = result

    def test_work_03(self, des='星币充足,房间星币打赏,礼物=摩登派对,连击=2'):
        # todo sql:清除作品已被打赏的标记
        # todo sql:starify_payUid 修改余额
        combo_key = hash_key()
        # 1 连击
        data = deal_pay_data("room", "10", to_uids=[starify_rewardUid01], hit_num=1, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))

        # 2 连击
        data = deal_pay_data("room", "10", to_uids=[starify_rewardUid01], hit_num=2, combo_key=combo_key)
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # todo sql:starify_payUid 查询余额
        case_list[des] = result
