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

    def test_room_001(self, des='房间打赏,星币余额充足,礼物=摩登派对,返奖15%～20%'):
        # todo sql:清除作品已被打赏的标记
        # todo sql:starify_payUid 修改余额
        data = deal_pay_data("room", "10", to_uids=[starify_rewardUid01], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # todo sql:starify_payUid 查询余额
        case_list[des] = result

    def test_room_002(self, des='房间打赏,星币余额=0'):
        # todo sql:清除作品已被打赏的标记
        # todo sql:starify_payUid 修改余额
        data = deal_pay_data("room", "10", to_uids=[starify_rewardUid01], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # todo sql:starify_payUid 查询余额
        case_list[des] = result

    def test_room_003(self, des='房间打赏,星币余额<礼物价值'):
        # todo sql:清除作品已被打赏的标记
        # todo sql:starify_payUid 修改余额
        data = deal_pay_data("room", "10", to_uids=[starify_rewardUid01], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # todo sql:starify_payUid 查询余额
        case_list[des] = result

    def test_room_004(self, des='房间打赏,星币余额充足,打赏多人,礼物=聲霸天下,返奖10%～15%'):
        # todo sql:清除作品已被打赏的标记
        # todo sql:starify_payUid 修改余额
        data = deal_pay_data("room", "9", to_uids=[starify_rewardUid01, starify_rewardUid02], )
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # todo sql:starify_payUid 查询余额
        case_list[des] = result

    def test_room_005(self, des='房间打赏,打赏多人,星币余额=0'):
        # todo
        pass

    def test_room_006(self, des='房间打赏,打赏多人,星币余额<礼物价值*打赏人数'):
        # todo
        pass

    def test_room_007(self, des='房间打赏,打赏多人,星币+背包组合支付,星币余额充足,礼物=摩登派对,返奖15%～20%'):
        # todo
        pass

    def test_room_008(self, des='房间打赏,打赏多人,星币+背包组合支付,星币余额=0'):
        # todo
        pass

    def test_room_009(self, des='房间打赏,打赏多人,星币+背包组合支付,星币余额<礼物价值'):
        # todo
        pass

    def test_room_010(self, des='房间打赏,背包支付,剩余礼物数充足,礼物=聲霸天下,返奖10%～15%'):
        # todo
        pass

    def test_room_011(self, des='房间打赏,背包支付,剩余礼物数=0'):
        # todo
        pass

    def test_room_012(self, des='房间打赏,背包支付,打赏多人,剩余礼物数充足,礼物=摩登派对,返奖15%～20%'):
        # todo
        pass

    def test_room_013(self, des='房间打赏,背包支付,打赏多人,剩余礼物数=0'):
        # todo
        pass

    def test_room_014(self, des='房间打赏,背包支付,打赏多人,剩余礼物数<打赏人数'):
        # todo
        pass

    def test_room_015(self, des='房间打赏,星币余额充足,连击数=2'):
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

    def test_room_016(self, des='房间打赏,背包礼物数+星币余额充足,连击数=2'):
        # todo
        pass

    def test_room_017(self, des='房间打赏,背包礼物数充足,连击数=2'):
        # todo
        pass

    def test_room_018(self, des='房间打赏,星币余额充足,打赏多人,连击数=2'):
        # todo
        pass

    def test_room_019(self, des='房间打赏,情况1,背包礼物数+星币余额充足,打赏多人,连击数=2'):
        # todo
        pass

    def test_room_020(self, des='房间打赏,情况2,背包礼物数+星币余额充足,打赏多人,连击数=2'):
        # todo
        pass

    def test_room_021(self, des='房间打赏,情况3,背包礼物数+星币余额充足,打赏多人,连击数=2'):
        # todo
        pass

    def test_room_022(self, des='房间打赏,背包礼物数充足,打赏多人,连击数=2'):
        # todo
        pass
