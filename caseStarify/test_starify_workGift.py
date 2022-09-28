import unittest

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

    def test_01_test(self, des='验证,不能重复打赏同一个作品'):
        """
        用例描述：
        检查账户余额不足时，私聊一对一打赏
        脚本步骤：
        1.构造用户数据
        2.房间打赏金币礼物流程(礼物：人气券)
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额（gold_coin） 100 - 20*2 = 60
        5.检查所有被打赏者账户余额（gold_coin）  20 * 0.6 = 12
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
                "wid": 601
            }""",
            "money_type": "star_coin",
            "total_money": "1",
        }
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'msg', '同一个星币礼物只能打赏同一个作品一次', reason_starify(des, res))
        # assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_testUid), 0)
        case_list[des] = result

    def test_02_test(self, des='验证,对作品进行打赏'):
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
                "wid": 607
            }""",
            "money_type": "star_coin",
            "total_money": "1",
        }
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        # assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_testUid), 0)
        case_list[des] = result
