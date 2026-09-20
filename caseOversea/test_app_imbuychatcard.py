# coding=utf-8
"""
APP 海外版支付测试 - 私聊卡购买验证

验证余额购买私聊卡的流程。
"""
from caseOversea.base import OverseaBizCase, OverseaBizTestBase
from common.Config import config
from common.runFailed import Retry

# 场景：余额购买私聊卡（money 100-16*10=0，背包得到 10 张私聊卡 cid=42598）
SCENE_001 = OverseaBizCase(
    des='余额购买私聊卡场景',
    setup=[
        {'action': 'update_money', 'params': {'uid': config.oversea_payUid, 'money': 100, 'money_cash': 60}},
        {'action': 'delete_user_account', 'params': {'table': 'user_commodity', 'uid': config.oversea_payUid}},
        {'action': 'delete_user_account', 'params': {'table': 'chat_pay_card_record', 'uid': config.oversea_payUid}},
    ],
    data={'payType': 'chat-pay-card'},
    checks=[
        {'field': 'sum_money', 'expected': 0},
        {'field': 'chat-pay-card', 'expected': 10},
    ],
)


@Retry(max_n=3, func_prefix='test_01_chatPayCard')
class TestPayCreate(OverseaBizTestBase):
    """APP 私聊卡购买测试类"""

    check_gift_config = True

    def test_01_chatPayCard(self, des: str = '余额购买私聊卡场景'):
        """余额购买私聊卡验证：160 钻购买 10 张私聊卡，余额清零"""
        self.run_case(SCENE_001)
