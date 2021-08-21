from common.Config import config
from common import Request
from common.params_Yaml import Yaml
from common.sqlScript import Mysql
import unittest
from common import Consts, Assert
from common.runFailed import Retry
@Retry(max_n=3)
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

    def test_01_defendPayChangMoney(self):
        """
        用例描述：
        开通个人守护，收益分成在师父收益的基础上为 62:38
        脚本步骤：
        1.构造开通者和被守护者数据 （更新xs_user_money）
        2.开通价值5200元守护
        3.校验【status code】和返回值【body】状态
        4.检查打赏者余额
        5.检查被打赏者余额,预期：52000 * 0.62 = 32240
        6.检查消费记录
        """
        des = '开通个人守护'
        Mysql.updateMoneySql(config.payUid, 52000)
        Mysql.updateMoneySql(config.testUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_defend')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.testUid), 32240)
        Assert.assert_equal(Mysql.selectPayChangeSql(config.payUid), 52000)
        Assert.assert_equal(Mysql.selectPayChangeOpSql(config.payUid), 'consume')
        Consts.CASE_LIST[des] = 'pass'

