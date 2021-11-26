from common.Config import config
from common.conMysql import conMysql
from common.method import reason
import unittest
from common.Request import post_request_session
from common.Assert import assert_body, assert_code, assert_equal
from common.Consts import case_list, result
from common import basicData
class TestPayCreate(unittest.TestCase):
    pay_url = config.pay_url

    @unittest.skip('暂无入口')
    def test_01_unityGamePayChange(self, des='unity道具购买场景'):
        """
        用例描述：
        验证unity游戏内道具购买
        脚本步骤：
        1.构造用户数据
        2.购买道具流程
        3.校验接口状态和返回值数据
        4.检查账户余额，预期值为：100 - 100 = 0
        """
        conMysql.updateMoneySql(config.payUid, money=100)
        data = basicData.encodeData(payType='unity-game-buy', money=100)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 0)
        case_list[des] = result