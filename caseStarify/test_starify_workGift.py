from caseStarify.base import StarifyCase, StarifyTestBase
from caseStarify.deal_data import deal_pay_data
from caseStarify.need_data import commodity_config, starify_payUid, starify_work_state
from common.Assert import assert_equal
from common.conStarifyMysql import conMysql
from common.runFailed import Retry


# (desc, commodity_key, clear_reward, work_state, balance, expected_star, expected_wealth, success, expected_msg)
# expected_wealth=None 时取 commodity['wealth']
WORK_GIFT_CASES = [
    ('星币余额充足,作品打赏,礼物类型=安可', '2', True, 'todo', 2, 0, None, True, None),
    ('作品打赏,星币余额=0', '2', True, 'todo', 0, 0, 0, False, '支付或打赏失败'),
    ('作品打赏,星币余额<礼物价值', '2', True, 'todo', 1, 1, 0, False, '支付或打赏失败'),
    ('作品打赏,重复打赏', '2', False, 'done', 2, 2, 0, False, '同一个星币礼物只能打赏同一个作品一次'),
    ('作品打赏,星币余额充足,礼物类型=星币', '1', True, 'todo', 1, 0, None, True, None),
]


def _make_work_gift_case(desc, commodity_key, clear_reward, work_state,
                         balance, expected_star, expected_wealth, success, expected_msg):
    """构造单条作品打赏场景"""
    commodity = commodity_config[commodity_key]
    setup = []
    if clear_reward:
        setup.append({'action': 'delete_user_account',
                      'params': {'table': 'user_work_reward', 'uid': starify_payUid,
                                 'wid': starify_work_state['todo']}})
    setup.append({'action': 'update_money', 'params': {'uid': starify_payUid, 'money': balance}})
    setup.append({'action': 'update_wealth', 'params': {'uid': starify_payUid, 'wealth': 0}})

    expected_w = commodity['wealth'] if expected_wealth is None else expected_wealth

    def _assert():
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), expected_star)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), expected_w)

    return StarifyCase(
        des=desc,
        setup=setup,
        data=deal_pay_data("work", commodity, work_state=work_state),
        success=True if success else None,
        msg=None if success else expected_msg,
        checks=[_assert],
    )


WORK_GIFT_SCENES = [_make_work_gift_case(*case) for case in WORK_GIFT_CASES]


@Retry(max_n=1)
class TestPayCreate(StarifyTestBase):
    """作品打赏测试"""

    def test_work_gift_all(self):
        """作品打赏全场景"""
        for scene in WORK_GIFT_SCENES:
            with self.subTest(desc=scene.des):
                self.run_case(scene)
