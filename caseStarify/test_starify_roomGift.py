from caseStarify.base import StarifyCase, StarifyTestBase
from caseStarify.deal_data import deal_pay_data
from caseStarify.need_data import commodity_config, starify_payUid, starify_rewardUid01, starify_rewardUid02, wealth_lv
from common.tools import hash_key
from common.Assert import assert_code, assert_body, assert_equal, assert_between
from common.Consts import case_list, result
from common.Request import post_starify
from common.conStarifyMysql import conMysql
from common.runFailed import Retry


def _reset_state_steps(pay_balance=0, bag_num=0, commodity=None, to_uids=None):
    """构造打赏者、被打赏者状态重置步骤（_prepare_test_data 格式）"""
    to_uids = to_uids or []
    steps = [
        {'action': 'update_money', 'params': {'uid': starify_payUid, 'money': pay_balance}},
        {'action': 'delete_user_account',
         'params': {'table': 'user_commodity', 'uid': starify_payUid}},
        {'action': 'update_wealth', 'params': {'uid': starify_payUid, 'wealth': 0}},
    ]
    if bag_num > 0 and commodity is not None:
        steps.append({'action': 'insert_commodity',
                      'params': {'uid': starify_payUid, 'cid': commodity['cid'],
                                 'num': bag_num}})
    for uid in to_uids:
        steps.append({'action': 'update_money', 'params': {'uid': uid, 'money': 0}})
        steps.append({'action': 'update_charm', 'params': {'uid': uid, 'charm': 0}})
    return steps


def _assert_single_step(commodity, to_uids, pay_balance, bag_num, total_hit,
                        success=True, reward=True):
    """断言某一步执行后的数据库状态

    Args:
        commodity: 礼物配置
        to_uids: 被打赏者列表
        pay_balance: 打赏者初始余额
        bag_num: 打赏者初始背包礼物数
        total_hit: 当前累计连击数
        success: 是否支付成功
        reward: 成功后是否返奖（免费礼物为 False）
    """
    people = len(to_uids)
    total_gifts = people * total_hit

    if success and reward:
        bag_used = min(bag_num, total_gifts)
        star_cost = commodity['price'] * (total_gifts - bag_used)
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), pay_balance - star_cost)
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']),
                     bag_num - bag_used)
        for uid in to_uids:
            assert_between(conMysql.selectUserInfoSql('star_coin', uid),
                           int(commodity['price'] * commodity['reward_lower']) * total_hit,
                           int(commodity['price'] * commodity['reward_upper']) * total_hit)
            assert_equal(conMysql.selectUserInfoSql('charm', uid), commodity['charm'] * total_hit)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid),
                     commodity['wealth'] * (total_gifts - bag_used))
    else:
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), pay_balance)
        assert_equal(conMysql.selectUserInfoSql('gift_num', starify_payUid, commodity['cid']), bag_num)
        for uid in to_uids:
            assert_equal(conMysql.selectUserInfoSql('star_coin', uid), 0)
            assert_equal(conMysql.selectUserInfoSql('charm', uid), 0)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), 0)


# ========== 单请求场景（余额/背包/人数组合） ==========

ROOM_GIFT_CASES = [
    # (描述, 礼物key, 被打赏者, 初始余额, 初始背包数, 是否成功, 失败提示, 是否返奖)
    ('房间打赏,星币余额充足,礼物=摩登派对,返奖15%～20%', '10', [starify_rewardUid01], 19999, 0, True, None, True),
    ('房间打赏,星币余额=0', '10', [starify_rewardUid01], 0, 0, False, "支付或打赏失败", True),
    ('房间打赏,星币余额<礼物价值', '10', [starify_rewardUid01], 19998, 0, False, "支付或打赏失败", True),
    ('房间打赏,星币余额充足,打赏多人,礼物=聲霸天下,返奖5%～10%', '9', [starify_rewardUid01, starify_rewardUid02], 10400, 0, True, None, True),
    ('房间打赏,打赏多人,星币余额=0', '9', [starify_rewardUid01, starify_rewardUid02], 0, 0, False, "支付或打赏失败", True),
    ('房间打赏,打赏多人,星币余额<礼物价值*打赏人数', '9', [starify_rewardUid01, starify_rewardUid02], 10399, 0, False, "支付或打赏失败", True),
    ('房间打赏,打赏多人,星币+背包组合支付,星币余额充足,礼物=摩登派对,返奖15%～20%', '10', [starify_rewardUid01, starify_rewardUid02], 19999, 1, True, None, True),
    ('房间打赏,打赏多人,星币+背包组合支付,星币余额=0', '10', [starify_rewardUid01, starify_rewardUid02], 0, 1, False, "支付或打赏失败", True),
    ('房间打赏,打赏多人,星币+背包组合支付,星币余额<礼物价值', '9', [starify_rewardUid01, starify_rewardUid02], 5199, 1, False, "支付或打赏失败", True),
    ('房间打赏,背包支付,剩余礼物数充足,礼物=聲霸天下,返奖5%～10%', '9', [starify_rewardUid01], 0, 1, True, None, True),
    ('房间打赏,背包支付,剩余礼物数=0', '9', [starify_rewardUid01], 0, 0, False, "支付或打赏失败", True),
    ('房间打赏,背包支付,打赏多人,剩余礼物数充足,礼物=摩登派对,返奖15%～20%', '10', [starify_rewardUid01, starify_rewardUid02], 0, 2, True, None, True),
    ('房间打赏,背包支付,打赏多人,剩余礼物数=0', '10', [starify_rewardUid01, starify_rewardUid02], 0, 0, False, "支付或打赏失败", True),
    ('房间打赏,背包支付,打赏多人,剩余礼物数<打赏人数', '10', [starify_rewardUid01, starify_rewardUid02], 0, 1, False, "支付或打赏失败", True),
    ('房间打赏,背包支付,礼物=日常宝箱-免费礼物(下架状态)', '51', [starify_rewardUid01], 0, 1, True, None, False),
]


def _make_room_gift_case(des, commodity_key, to_uids, pay_balance, bag_num,
                         expected_success, expected_msg, reward):
    """构造单条房间打赏场景"""
    commodity = commodity_config[commodity_key]

    def _assert():
        _assert_single_step(commodity, to_uids, pay_balance, bag_num, 1,
                            success=expected_success, reward=reward)

    return StarifyCase(
        des=des,
        setup=_reset_state_steps(pay_balance, bag_num, commodity, to_uids),
        data=deal_pay_data("room", commodity, to_uids=to_uids),
        success=True if expected_success else None,
        msg=None if expected_success else expected_msg,
        checks=[_assert],
    )


ROOM_GIFT_SCENES = [_make_room_gift_case(*case) for case in ROOM_GIFT_CASES]

# ========== 连击场景 ==========

ROOM_COMBO_CASES = [
    # (描述, 礼物key, 被打赏者, 初始余额, 初始背包数)
    ('房间打赏,星币余额充足,连击数=3', '10', [starify_rewardUid01], 19999 * 3, 0),
    ('房间打赏,背包礼物数+星币余额充足,连击数=3', '10', [starify_rewardUid01], 19999 * 2, 1),
    ('房间打赏,背包礼物数充足,连击数=3', '10', [starify_rewardUid01], 0, 3),
    ('房间打赏,星币余额充足,打赏多人,连击数=3', '10', [starify_rewardUid01, starify_rewardUid02], 19999 * 3 * 2, 0),
    ('房间打赏,情况1,背包礼物数+星币余额充足,打赏多人,连击数=3', '10', [starify_rewardUid01, starify_rewardUid02], 19999 * 5, 1),
    ('房间打赏,情况2,背包礼物数+星币余额充足,打赏多人,连击数=3', '10', [starify_rewardUid01, starify_rewardUid02], 19999 * 4, 2),
    ('房间打赏,情况3,背包礼物数+星币余额充足,打赏多人,连击数=3', '10', [starify_rewardUid01, starify_rewardUid02], 19999 * 3, 3),
    ('房间打赏,背包礼物数充足,打赏多人,连击数=3', '10', [starify_rewardUid01, starify_rewardUid02], 0, 6),
]

# ========== 批量礼物种类 ==========

GIFT_RANGE_CASES = list(range(3, 9))

# ========== 特权礼物 ==========

PRIVILEGE_FAIL_CASES = [(lv, gift_lv) for lv in range(0, 6) for gift_lv in range(lv + 1, 7)]


def _make_privilege_fail_case(des, lv, gift_lv):
    """构造送>当前财富等级特权礼物的失败场景"""
    commodity = commodity_config[f'lv{gift_lv}']
    level_min = wealth_lv[f'lv{lv}']['min']

    def _assert():
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 50000)
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), level_min)
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), 0)

    return StarifyCase(
        des=des,
        setup=[
            {'action': 'update_money', 'params': {'uid': starify_payUid, 'money': 50000}},
            {'action': 'delete_user_account',
             'params': {'table': 'user_commodity', 'uid': starify_payUid}},
            {'action': 'update_wealth', 'params': {'uid': starify_payUid, 'wealth': level_min}},
            {'action': 'update_money', 'params': {'uid': starify_rewardUid01, 'money': 0}},
            {'action': 'update_charm', 'params': {'uid': starify_rewardUid01, 'charm': 0}},
        ],
        data=deal_pay_data("room", commodity, to_uids=[starify_rewardUid01]),
        success=None,
        msg="当前特权级别无法使用此礼物",
        checks=[_assert],
    )


PRIVILEGE_FAIL_SCENES = [
    _make_privilege_fail_case('房间打赏,送>当前财富等级的特权礼物', lv, gift_lv)
    for lv, gift_lv in PRIVILEGE_FAIL_CASES
]

PRIVILEGE_SUCCESS_CASES = [(lv, gift_lv) for lv in range(1, 7) for gift_lv in range(1, lv + 1)]


def _make_privilege_success_case(des, lv, gift_lv):
    """构造送<=当前财富等级特权礼物的成功场景"""
    commodity = commodity_config[f'lv{gift_lv}']
    level_min = wealth_lv[f'lv{lv}']['min']

    def _assert():
        assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), 50000 - commodity['price'])
        if gift_lv in (5, 6):
            assert_between(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01),
                           int(commodity['price'] * commodity['reward_lower']),
                           int(commodity['price'] * commodity['reward_upper']))
        else:
            assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
        assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid),
                     level_min + commodity['wealth'])
        assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), commodity['charm'])

    return StarifyCase(
        des=des,
        setup=[
            {'action': 'update_money', 'params': {'uid': starify_payUid, 'money': 50000}},
            {'action': 'delete_user_account',
             'params': {'table': 'user_commodity', 'uid': starify_payUid}},
            {'action': 'update_wealth', 'params': {'uid': starify_payUid, 'wealth': level_min}},
            {'action': 'update_money', 'params': {'uid': starify_rewardUid01, 'money': 0}},
            {'action': 'update_charm', 'params': {'uid': starify_rewardUid01, 'charm': 0}},
        ],
        data=deal_pay_data("room", commodity, to_uids=[starify_rewardUid01]),
        checks=[_assert],
    )


PRIVILEGE_SUCCESS_SCENES = [
    _make_privilege_success_case('房间打赏,送<=当前财富等级的特权礼物', lv, gift_lv)
    for lv, gift_lv in PRIVILEGE_SUCCESS_CASES
]


@Retry(max_n=2)
class TestPayCreate(StarifyTestBase):

    def _reset_state(self, pay_balance=0, bag_num=0, commodity=None, to_uids=None):
        """重置打赏者、被打赏者状态"""
        self._prepare_test_data(_reset_state_steps(pay_balance, bag_num, commodity, to_uids))

    def _send_room_gift(self, commodity, to_uids, hit_offset=1, combo_key=None):
        """发送房间打赏请求"""
        data = deal_pay_data(
            "room", commodity,
            to_uids=to_uids,
            hit_offset=hit_offset,
            combo_key=combo_key if combo_key is not None else hash_key()
        )
        return post_starify(data)

    def _assert_response(self, des, res, success=True, msg=None):
        """断言接口响应"""
        assert_code(res['code'])
        if success:
            assert_body(res['body'], 'success', True)
        else:
            assert_body(res['body'], 'msg', msg)

    def _assert_single_step(self, commodity, to_uids, pay_balance, bag_num, total_hit,
                            success=True, reward=True):
        """断言某一步执行后的数据库状态（委托模块级实现，与场景表共用）"""
        _assert_single_step(commodity, to_uids, pay_balance, bag_num, total_hit,
                            success=success, reward=reward)

    # ========== 单请求场景（余额/背包/人数组合） ==========

    def test_room_gift_all(self):
        for scene in ROOM_GIFT_SCENES:
            with self.subTest(des=scene.des):
                self.run_case(scene)

    # ========== 连击场景 ==========

    def _run_room_combo_case(self, des, commodity_key, to_uids, pay_balance, bag_num):
        commodity = commodity_config[commodity_key]
        self._reset_state(pay_balance, bag_num, commodity, to_uids)
        combo_key = hash_key()

        # 第 1 次连击
        res = self._send_room_gift(commodity, to_uids, hit_offset=1, combo_key=combo_key)
        self._assert_response(des, res, True)
        self._assert_single_step(commodity, to_uids, pay_balance, bag_num, 1)

        # 第 2 次连击（累计 1 + 2 = 3）
        res = self._send_room_gift(commodity, to_uids, hit_offset=2, combo_key=combo_key)
        self._assert_response(des, res, True)
        self._assert_single_step(commodity, to_uids, pay_balance, bag_num, 3)

        case_list[des] = result

    def test_room_combo_all(self):
        for case in ROOM_COMBO_CASES:
            with self.subTest(des=case[0]):
                self._run_room_combo_case(*case)

    # ========== 批量礼物种类 ==========

    def test_room_gift_range(self, des='房间打赏,打赏3~8号礼物种类,不返奖'):
        money = 100000
        self._reset_state(money, 0, None, [starify_rewardUid01])
        wealth = 0
        charm = 0
        for gift_id in GIFT_RANGE_CASES:
            with self.subTest(gift_id=gift_id):
                commodity = commodity_config[str(gift_id)]
                res = self._send_room_gift(commodity, [starify_rewardUid01])
                assert_code(res['code'])
                assert_body(res['body'], 'success', True)
                money -= commodity['price']
                wealth += commodity['wealth']
                charm += commodity['charm']
                assert_equal(conMysql.selectUserInfoSql('star_coin', starify_payUid), money)
                assert_equal(conMysql.selectUserInfoSql('star_coin', starify_rewardUid01), 0)
                assert_equal(conMysql.selectUserInfoSql('wealth', starify_payUid), wealth)
                assert_equal(conMysql.selectUserInfoSql('charm', starify_rewardUid01), charm)
        case_list[des] = result

    # ========== 特权礼物 ==========

    def test_room_privilege_fail_all(self, des='房间打赏,送>当前财富等级的特权礼物'):
        for (lv, gift_lv), scene in zip(PRIVILEGE_FAIL_CASES, PRIVILEGE_FAIL_SCENES):
            with self.subTest(lv=lv, gift_lv=gift_lv):
                self.run_case(scene)

    def test_room_privilege_success_all(self, des='房间打赏,送<=当前财富等级的特权礼物'):
        for (lv, gift_lv), scene in zip(PRIVILEGE_SUCCESS_CASES, PRIVILEGE_SUCCESS_SCENES):
            with self.subTest(lv=lv, gift_lv=gift_lv):
                self.run_case(scene)
