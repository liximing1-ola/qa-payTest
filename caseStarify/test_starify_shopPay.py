import unittest

from caseStarify.deal_data import deal_pay_data
from caseStarify.need_data import *
from common.Assert import *
from common.Consts import case_list, result
# from common.method import reason
from common.Request import post_request_session_starify
from common.conStarifyMysql import conMysql
from common.method import reason_starify
from common.runFailed import Retry


@Retry(max_n=1)
class TestPayCreate(unittest.TestCase):
    def test_shop_001(self, des='星币充足,商城购买-头像框'):
        commodity = commodity_config['header']
        #  sql:打赏者starify_payUid 修改余额=10000
        conMysql.updateMoneySql(starify_payUid, 10000)
        data = deal_pay_data("shop_buy", commodity['cid'])
        res = post_request_session_starify(config.starify_pay_url, data, tokenName='starify')
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, reason_starify(des, res))
        #  sql:starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 10000-3*commodity['price'])
        case_list[des] = result
    # def test_shop_001(self, des='星币充足,商城购买-进场横幅'):
    #     pass
    # def test_shop_001(self, des='星币充足,商城购买-麦上光圈'):
    #     pass
    # def test_shop_001(self, des='星币充足,商城购买单个道具场景'):
    #     pass
    # def test_shop_001(self, des='星币充足,商城购买单个道具场景'):
    #     pass


if __name__ == '__main__':
    """
    http://47.243.83.154/go/starify/pay/create?package=com.starify.ola.android&_ipv=1&_platform=android&_index=175&_model=GM1910&_timestamp=1667976298&_abi=arm64-v8a&format=pb&_sign=f99ad125f640fd14985a3002d1906fcd&_blid=124498&_versionName=1.0.5.2&_versionCode=100005002
    """
    params = {
        "_abi": "arm64-v8a",
        "format": "pb",
        "_sign": "f99ad125f640fd14985a3002d1906fcd",
        "_blid": "124498",
        "_versionName": "1.0.5.2",
        "_versionCode": "100005002",
    }
    data={
        """
op_type	shop_buy
params	{"cid":83,"sale_level":1,"count":1}
money_type	star_coin
total_money	893584
        """
    }