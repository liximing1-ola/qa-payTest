from common.Config import config
from common import Request
from common.params_Yaml import Yaml
from common.sqlScriptOversea import Mysql
import unittest
from common import Consts, Assert
from common.runFailed import Retry

@Retry(max_n=2)
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.pt_host + 'pay/create'

    def test_01_defendPayChangMoney(self):
        """
        用例描述：
        开通个人守护，收益分成为 70:30
        脚本步骤：
        1.构造开通者和被守护者数据 （更新xs_user_money）
        2.开通价值520守护
        3.校验【status code】和返回值【body】状态
        4.检查打赏者余额
        5.检查被打赏者余额,预期：52000 * 0.70 = 36400
        6.检查消费记录
        """
        des = '检查PT开通个人守护支付场景'
        Mysql.updateMoneySql(config.pt_payUid, 5200)
        Mysql.updateMoneySql(config.pt_testUid)
        data = Yaml.read_yaml('Basic_pt.yml', 'pt_pay_defend')
        res = Request.pt_post_request_session(url=TestPayCreate.pay_url, data=data)
        print(res)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.pt_payUid), 0)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.pt_testUid), 36400)
        Assert.assert_equal(Mysql.selectPayChangeSql(config.pt_payUid), 52000)
        Assert.assert_equal(Mysql.selectPayChangeOpSql(config.pt_payUid), 'consume')
        Consts.CASE_LIST[des] = 'pass'