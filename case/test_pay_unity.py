from common.Config import config
from common.conMysql import conMysql
from common.method import reason
import unittest
from common.Request import post_request_session
from common.Assert import assert_body, assert_code, assert_equal
from common import Consts, basicData
class TestPayCreate(unittest.TestCase):
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'   # 内网支付接口

    @unittest.skip('暂无入口')
    def test_01_unityGamePayChange(self):
        """
        用例描述：
        验证unity游戏内道具购买
        脚本步骤：
        1.构造用户数据
        2.购买道具流程
        3.校验接口状态和返回值数据
        4.检查账户余额，预期值为：100 - 100 = 0
        """
        des = 'unity道具购买场景'
        conMysql.updateMoneySql(config.payUid, money=100)
        data = basicData.encodeData(payType='unity-game-buy', money=100)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 0)
        Consts.CASE_LIST[des] = Consts.result