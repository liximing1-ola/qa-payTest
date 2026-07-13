import unittest

from caseStarify.deal_data import deal_pay_data
from caseStarify.need_data import commodity_config, starify_payUid, starify_work_state
from common.Assert import assert_body, assert_code, assert_equal
from common.Consts import case_list, result
from common.Request import post_starify
from common.conStarifyMysql import conMysql
from common.method import format_reason
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


@Retry(max_n=1)
class TestPayCreate(unittest.TestCase):
    """作品打赏测试"""

    def _run_work_gift_case(self, desc, commodity_key, clear_reward, work_state,
                            balance, expected_star, expected_wealth, success, expected_msg):
        """作品打赏通用执行流程"""
        commodity = commodity_config[commodity_key]
        if clear_reward:
            conMysql.deleteUserAccountSql("user_work_reward", starify_payUid, starify_work_state['todo'])
        conMysql.updateMoneySql(starify_payUid, balance)
        conMysql.updateWealthSql(starify_payUid, 0)

        data = deal_pay_data("work", commodity, work_state=work_state)
        res = post_starify(data)
        assert_code(res['code'])

        if success:
            assert_body(res['body'], 'success', True, format_reason(desc, res, slp=True))
        else:
            assert_body(res['body'], 'msg', expected_msg, format_reason(desc, res, slp=True))

        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), expected_star)
        expected_w = commodity['wealth'] if expected_wealth is None else expected_wealth
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), expected_w)
        case_list[desc] = result

    def test_work_gift_all(self):
        """作品打赏全场景"""
        for desc, commodity_key, clear_reward, work_state, balance, exp_star, exp_wealth, success, exp_msg in WORK_GIFT_CASES:
            with self.subTest(desc=desc):
                self._run_work_gift_case(desc, commodity_key, clear_reward, work_state,
                                         balance, exp_star, exp_wealth, success, exp_msg)
import unittest

from caseStarify.deal_data import deal_pay_data
from caseStarify.need_data import commodity_config, starify_payUid, starify_work_state
from common.Assert import assert_body, assert_code, assert_equal
from common.Consts import case_list, result
from common.Request import post_starify
from common.conStarifyMysql import conMysql
from common.method import format_reason
from common.runFailed import Retry


@Retry(max_n=1)
class TestPayCreate(unittest.TestCase):
    def test_work_001(self, des='星币余额充足,作品打赏,礼物类型=安可'):
        commodity = commodity_config['2']
        #  sql:清除作品已被打赏的标记
        conMysql.deleteUserAccountSql("user_work_reward", starify_payUid, starify_work_state['todo'])
        #  sql:打赏者starify_payUid 修改余额=2
        conMysql.updateMoneySql(starify_payUid, 2)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        data = deal_pay_data("work", commodity, work_state="todo")
        res = post_starify(data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
        #  sql:starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), commodity['wealth'])
        case_list[des] = result

    def test_work_002(self, des='作品打赏,星币余额=0'):
        commodity = commodity_config['2']
        #  sql:清除作品已被打赏的标记
        conMysql.deleteUserAccountSql("user_work_reward", starify_payUid, starify_work_state['todo'])
        #  sql:starify_payUid 修改余额=0
        conMysql.updateMoneySql(starify_payUid, 0)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        data = deal_pay_data("work", commodity, work_state="todo")
        res = post_starify(data)
        assert_code(res['code'])
        assert_body(res['body'], 'msg', '支付或打赏失败', format_reason(des, res, slp=True))
        #  sql:starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), 0)
        case_list[des] = result

    def test_work_003(self, des='作品打赏,星币余额<礼物价值'):
        commodity = commodity_config['2']
        #  sql:清除作品已被打赏的标记
        conMysql.deleteUserAccountSql("user_work_reward", starify_payUid, starify_work_state['todo'])
        #  sql:starify_payUid 修改余额=1
        conMysql.updateMoneySql(starify_payUid, 1)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        data = deal_pay_data("work", commodity, work_state="todo")
        res = post_starify(data)
        assert_code(res['code'])
        assert_body(res['body'], 'msg', "支付或打赏失败", format_reason(des, res, slp=True))
        #  sql:starify_payUid 查询余额=1
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 1)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), 0)
        case_list[des] = result

    def test_work_004(self, des='作品打赏,重复打赏'):
        commodity = commodity_config['2']
        #  sql:starify_payUid 修改余额=2
        conMysql.updateMoneySql(starify_payUid, 2)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        data = deal_pay_data("work", commodity, work_state="done")
        res = post_starify(data)
        assert_code(res['code'])
        assert_body(res['body'], 'msg', '同一个星币礼物只能打赏同一个作品一次', format_reason(des, res, slp=True))
        #  sql:starify_payUid 查询余额=2
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 2)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), 0)
        case_list[des] = result

    def test_work_005(self, des='作品打赏,星币余额充足,礼物类型=星币'):
        commodity = commodity_config['1']
        #  sql:清除作品已被打赏的标记
        conMysql.deleteUserAccountSql("user_work_reward", starify_payUid, starify_work_state['todo'])
        #  sql:starify_payUid 修改余额=1（星币礼物价格）
        conMysql.updateMoneySql(starify_payUid, 1)
        #  sql:打赏者starify_payUid 修改财富值=0
        conMysql.updateWealthSql(starify_payUid, 0)
        data = deal_pay_data("work", commodity, "todo")
        res = post_starify(data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', True, format_reason(des, res, slp=True))
        #  sql:starify_payUid 查询余额=0
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 0)
        #  sql:打赏者starify_payUid 查询-财富值=礼物价值
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), commodity['wealth'])
        case_list[des] = result
