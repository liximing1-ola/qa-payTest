from common.Config import config
from common import Request
from common.params_Yaml import Yaml
from common.sqlScriptOversea import Mysql
import unittest
from common import Consts
from common import Assert
from common.runFailed import Retry

@Retry(max_n=2)
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.pt_host + 'pay/create'

    def test_01_moneyChangeExchangeCoin(self):
        """
        用例描述：
        验证money兑换金币流程
        脚本步骤：
        1.构造用户数据 （更新xs_user_money）
        2.金币兑换
        3.校验【status code】和返回值【body】状态
        4.检查账户余额（money, gold_coin） 1000-600=400
        """
        des = '检查余额兑换金币流程'
        Mysql.updateMoneySql(config.pt_payUid, 1000)
        data = Yaml.read_yaml('Basic_pt.yml', '')
        res = Request.pt_post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.pt_payUid), 400)
        Assert.assert_equal(Mysql.selectCoinSql(config.pt_payUid), 600)
        Consts.CASE_LIST[des] = 'pass'