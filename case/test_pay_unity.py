from common.Config import config
from common.conMysql import conMysql
import unittest
from common import Consts, Request, Assert, basicData
from common.runFailed import Retry
@Retry
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

    @unittest.skip('暂无unity购买入口')
    def test_01_unityGamePayChange(self):
        """
        用例描述：
        验证unity游戏内道具购买
        脚本步骤：
        1.构造用户数据（更新xs_user_money）
        2.购买流程
        3.校验【status code】和返回值【body】状态
        4.检查账户余额，预期值为：100-100=0
        """
        des = 'unity道具购买场景'
        conMysql.updateMoneySql(config.payUid, 100)
        data = basicData.encodeData(payType='unity-game-buy', money=100)
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 0)
        Consts.CASE_LIST[des] = Consts.result