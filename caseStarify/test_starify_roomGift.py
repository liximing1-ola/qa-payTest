import unittest

from common.Assert import assert_code, assert_equal, assert_body
from common.Config import config
from common.Consts import case_list, result
from common.Request import post_request_session, post_request_session_starify
# from common.conPtMysql import conMysql
# from common.method import reason
from common.method import reason, reason_starify
from common.runFailed import Retry


@Retry(max_n=1)
class TestPayCreate(unittest.TestCase):

    def test_01_test(self, des='test'):
        """
        用例描述：
        检查账户余额不足时，私聊一对一打赏
        脚本步骤：

        """
        # conMysql.updateUserMoneyClearSql(config.pt_payUid, config.pt_testUid)
        # data = encodePtData(payType='chat-gift')4

        data = {
            "op_type": "work",
            "params": """{
                "gift_id": 1,
                "gift_num": 1,
                "price": 1,
                "num": 1,
                "gift_type": "normal",
                "uid": 124313,
                "wid": 602
            }""",
            "money_type": "star_coin",
            "total_money": "1",
        }
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # assert_body(res['body'], 'msg', '同一个星币礼物只能打赏同一个作品一次', reason_starify(des, res))
        # assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_testUid), 0)
        case_list[des] = result
