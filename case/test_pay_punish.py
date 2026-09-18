# coding=utf-8
"""
罚款支付测试

场景差异通过模块级 SCENES 表声明，由 PayTestBase.run_case 统一执行。
"""
from case.base import PayCase, PayTestBase
from common.Config import config
from common.runFailed import Retry

# NSQ 异步扣款消息处理等待（秒）
NSQ_SETTLE_WAIT = 2

SCENES = [
    PayCase(
        des='打赏时触发罚款流程',
        setup=[
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 100}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid, 'money': 20, 'money_cash': 20,
                                                   'money_debts': 100}}
        ],
        data={'money': 100, 'rid': config.live_role['auto_rid'], 'giftId': config.giftId['5']},
        post_wait=NSQ_SETTLE_WAIT,
        checks=[
            {'field': 'single_money', 'uid': config.rewardUid, 'money_type': 'money', 'expected': 2},
            {'field': 'single_money', 'uid': config.rewardUid, 'money_type': 'money_cash', 'expected': 0},
            {'field': 'single_money', 'uid': config.rewardUid, 'money_type': 'money_debts', 'expected': 0}
        ],
        report='case_list_c'),
]


@Retry(max_n=3)
class TestPayPunish(PayTestBase):
    """罚款支付测试类"""

    def test_01_PayChangeTriggerPunish(self):
        """收到打赏时触发罚款流程，扣款账户：个人魅力值 → 现金余额 → 公会魅力值 → APP币"""
        self.run_case(SCENES[0])
