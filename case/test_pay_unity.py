from common.Config import config
from common.params_Yaml import Yaml
from common.sqlScript import Mysql
import unittest
from common import Consts, Request, Assert, newData
from common.runFailed import Retry
import time
@Retry
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

    @classmethod
    def tearDownClass(cls) -> None:
        Consts.endTime = time.time()

    def test_01_unityGameBugPayChange(self):
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
        Mysql.updateMoneySql(config.payUid, 100)
        # data = Yaml.read_yaml('Basic.yml', 'dev_pay_unityGame')
        data = newData.encodeData(payType='unity-game-buy', money=100)
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0)
        Consts.CASE_LIST[des] = Consts.result