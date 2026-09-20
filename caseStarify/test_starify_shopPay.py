from caseStarify.base import StarifyCase, StarifyTestBase
from caseStarify.deal_data import deal_pay_data
from caseStarify.need_data import commodity_config, starify_payUid
from common.tools import deal_num
from common.Assert import assert_equal
from common.conStarifyMysql import conMysql
from common.runFailed import Retry

user_money = 200000


def _make_shop_case(des, commodity_key, sale_level):
    """构造单条商城购买场景"""
    commodity = commodity_config[commodity_key]
    cost = deal_num(
        commodity[f'level_{sale_level}']['day']
        * commodity[f'level_{sale_level}']['rate']
        * commodity['price']
    )
    duration = commodity[f'level_{sale_level}']['duration']

    def _assert():
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), user_money - cost)
        assert_equal(conMysql.selectUserInfoSql('commodity_num', starify_payUid, commodity['cid'], duration), 1)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), cost)

    return StarifyCase(
        des=des,
        setup=[
            {'action': 'update_money', 'params': {'uid': starify_payUid, 'money': user_money}},
            {'action': 'delete_user_account',
             'params': {'table': 'user_commodity', 'uid': starify_payUid}},
            {'action': 'update_wealth', 'params': {'uid': starify_payUid, 'wealth': 0}},
        ],
        data=deal_pay_data("shop_buy", commodity, sale_level=sale_level),
        checks=[_assert],
    )


SHOP_CASES = [
    ('星币充足,商城购买-头像框,3天', 'header', 1),
    ('星币充足,商城购买-头像框,7天', 'header', 2),
    ('星币充足,商城购买-头像框,15天', 'header', 3),
    ('星币充足,商城购买-进场横幅,3天', 'effect', 1),
    ('星币充足,商城购买-麦上光圈,3天', 'ring', 1),
]

SHOP_SCENES = [_make_shop_case(*case) for case in SHOP_CASES]


@Retry(max_n=1)
class TestPayCreate(StarifyTestBase):

    def test_shop_all(self, des='商城购买各类物品档位组合'):
        """数据驱动：覆盖不同商品与购买档位的商城购买场景"""
        for scene in SHOP_SCENES:
            with self.subTest(des=scene.des):
                self.run_case(scene)
