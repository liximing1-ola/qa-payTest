from common.Config import config
from common import Request
from common.params_Yaml import Yaml
from common.sqlScript import mysql
import unittest
from common import Consts
from common import Assert
from common.runFailed import Retry

@Retry(max_n=2)
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.pt_host + 'pay/create'

    def test_01_unityGameBugPayChange(self):
        """
        用例描述：
        验证unity游戏内购买
        脚本步骤：
        1.构造用户数据（更新xs_user_money）
        2.购买流程
        3.校验【status code】和返回值【body】状态
        4.检查账户余额，预期值为：200-100=100
        """
        des = '检查unity小游戏内道具购买场景'
        mysql.updateMoneySql(config.pt_payUid, 200)
        data = Yaml.read_yaml('Basic_pt.yml', 'pt_pay_unityGame')
        res = Request.pt_post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(mysql.selectAllMoneySql(config.pt_payUid), 100)
        Consts.case_list[des] = 'pass'