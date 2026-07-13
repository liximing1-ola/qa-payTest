import unittest

from caseStarify.deal_data import deal_pay_data
from caseStarify.need_data import commodity_config, starify_payUid
from common.tools import deal_num
from common.Assert import assert_body, assert_code, assert_equal
from common.Consts import case_list, result
from common.Request import post_starify
from common.conStarifyMysql import conMysql
from common.method import format_reason
from common.runFailed import Retry

user_money = 200000


@Retry(max_n=1)
class TestPayCreate(unittest.TestCase):
    SHOP_CASES = [
        ('星币充足,商城购买-头像框,3天', 'header', 1),
        ('星币充足,商城购买-头像框,7天', 'header', 2),
        ('星币充足,商城购买-头像框,15天', 'header', 3),
        ('星币充足,商城购买-进场横幅,3天', 'effect', 1),
        ('星币充足,商城购买-麦上光圈,3天', 'ring', 1),
    ]

    def _run_shop_case(self, des, commodity_key, sale_level):
        """商城购买单条用例的执行逻辑"""
        commodity = commodity_config[commodity_key]
        conMysql.updateMoneySql(starify_payUid, user_money)
        conMysql.deleteUserAccountSql('user_commodity', starify_payUid)
        conMysql.updateWealthSql(starify_payUid, 0)
        data = deal_pay_data("shop_buy", commodity, sale_level=sale_level)
        res = post_starify(data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
        cost = deal_num(
            commodity[f'level_{sale_level}']['day']
            * commodity[f'level_{sale_level}']['rate']
            * commodity['price']
        )
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), user_money - cost)
        duration = commodity[f'level_{sale_level}']['duration']
        assert_equal(conMysql.selectUserInfoSql('commodity_num', starify_payUid, commodity['cid'], duration), 1)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), cost)
        case_list[des] = result

    def test_shop_all(self, des='商城购买各类物品档位组合'):
        """数据驱动：覆盖不同商品与购买档位的商城购买场景"""
        for case_des, commodity_key, sale_level in self.SHOP_CASES:
            with self.subTest(des=case_des, commodity_key=commodity_key, sale_level=sale_level):
                self._run_shop_case(case_des, commodity_key, sale_level)
