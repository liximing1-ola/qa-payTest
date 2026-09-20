# coding=utf-8
"""
APP 海外版支付测试 - 疯狂转盘验证

验证疯狂转盘的购买券和抽奖功能。
"""
import unittest

from caseOversea.base import OverseaBizCase, OverseaBizTestBase
from common.Config import config
from common.Consts import case_list, result
from common.Crazyspin import CrazySpin
from common.conPtMysql import conMysql
from common.runFailed import Retry

# 场景：扣除钻石购买欢乐券（2000 钻购买 10 张，cid=32）
SCENE_001 = OverseaBizCase(
    des='扣除钻石购买欢乐转盘欢乐券',
    setup=[
        {'action': 'delete_user_account', 'params': {'table': 'user_commodity', 'uid': config.oversea_payUid}},
        {'action': 'update_money', 'params': {'uid': config.oversea_payUid, 'money': 2000}},
    ],
    data={'payType': 'shop-buy-crazyspin'},
    url=CrazySpin.spin_buy_url(uid=config.oversea_payUid),
    checks=[
        {'field': 'sum_money', 'expected': 1000},
        {'field': 'sum_commodity_32', 'expected': 10},
    ],
)


@Retry
class TestPayCreate(OverseaBizTestBase):
    """APP 疯狂转盘测试类"""

    def test_01_crazySpinExchange(self, des: str = '扣除钻石购买欢乐转盘欢乐券'):
        """购买欢乐券验证：2000-10*100=1000 钻，背包得到 10 张欢乐券"""
        self.run_case(SCENE_001)

    @unittest.skip('待补充 go 的接口服务')
    def test_02_playCrazySpin(self, des: str = '开启大转盘抽奖场景', cid: int = 32):
        """大转盘抽奖验证（占位：抽奖逻辑待业务接口就绪后补充）"""
        # 1. 构造数据
        conMysql.deleteUserAccountSql('user_commodity', config.oversea_payUid)
        conMysql.insertXsUserCommodity(config.oversea_payUid, cid=cid, num=100)  # 背包插入 100 个欢乐券

        # 抽奖逻辑待业务接口就绪后补充，当前仅保留跳过占位
        case_list[des] = result
