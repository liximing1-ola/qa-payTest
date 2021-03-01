from Common.config import config
from Common import Request, api
from Common.params_Yaml import Yaml
from Common.sqlScript import mysqlScript
import unittest
from Common import consts


class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_package_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

    def test_01_defendPayChangMoney(self):
        """
        用例描述：
        开通个人守护，收益分成在师父收益的基础上为 62:38
        脚本步骤：
        1.构造开通者和被守护者数据 （更新xs_user_money）
        2.开通520守护
        3.校验【status code】和返回值【body】状态
        4.检查打赏者余额
        5.检查被打赏者余额,预期：52000 * 0.62 = 32240
        6.检查消费记录
        """
        mysqlScript.updateMoneySql(52000, 0, 0, 0, config.payUid)
        mysqlScript.updateMoneySql(0, 0, 0, 0, config.testUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_defend')
        res = Request.post_request_session(url=TestPayCreate.pay_package_url, data=data)
        assert res['code'] == 200
        # api.errorMsg(res)
        assert res['body']['success'] == 1
        assert len(res['body']['args']) > 1
        assert mysqlScript.selectAllMoneySql(config.payUid) == 0
        assert mysqlScript.selectAllMoneySql(config.testUid) == 32240
        assert mysqlScript.selectPayChangeSql(config.payUid) == 52000
        assert mysqlScript.selectPayChangeOpSql(config.payUid) == 'consume'
        consts.CASE_LIST['验证开通个人守护的收益分成'] = 'pass'

