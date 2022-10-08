import unittest

from caseStarify.deal_data import deal_pay_data
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

    def test_work_001(self, des='星币余额充足,作品打赏,礼物类型=安可'):
        # todo sql:清除作品已被打赏的标记
        # todo sql:starify_payUid 修改余额
        data = deal_pay_data("work", "2", "todo")
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # todo sql:starify_payUid 查询余额
        case_list[des] = result

    def test_work_002(self, des='作品打赏,星币余额=0'):
        # todo sql:清除作品已被打赏的标记
        # todo sql:starify_payUid 修改余额
        data = deal_pay_data("work", "2", work_state="todo")
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', '支付或打赏失败', reason_starify(des, res))
        # todo sql:starify_payUid 查询余额
        case_list[des] = result

    def test_work_003(self, des='作品打赏,星币余额<礼物价值'):
        # todo sql:清除作品已被打赏的标记
        # todo sql:starify_payUid 修改余额
        data = deal_pay_data("work", "2", "todo")
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", reason_starify(des, res))
        # todo sql:starify_payUid 查询余额
        case_list[des] = result

    def test_work_004(self, des='作品打赏,重复打赏'):
        # todo sql:starify_payUid 修改余额
        data = deal_pay_data("work", "2", "done")
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', '同一个星币礼物只能打赏同一个作品一次', reason_starify(des, res))
        # todo sql:starify_payUid 查询余额
        case_list[des] = result

    def test_work_005(self, des='星币余额充足,作品打赏,礼物类型=星币'):
        # todo sql:清除作品已被打赏的标记
        # todo sql:starify_payUid 修改余额
        data = deal_pay_data("work", "1", "todo")
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # todo sql:starify_payUid 查询余额
        case_list[des] = result
