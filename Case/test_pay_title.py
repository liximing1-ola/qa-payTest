from Common.config import config
from Common import Request
from Common.params_Yaml import Yaml
from Common.sqlScript import mysqlScript
import unittest
import pytest


class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_package_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

    @pytest.mark.run(order=1)
    def test_01_TitlePayChangeMoney(self):
        """
        用例描述：
        验证爵位开通及返钱到余额（money）
        脚本步骤：
        1.清空背包内物品，模拟开通者数据（更新xs_user_money）
        2.开通子爵
        3.校验【status code】和返回值【body】状态
        4.检查剩余钱值,预期值：（200000 - 100000 + 60000 = 160000）
        """
        mysqlScript.selectUserCommoditySql(config.payUid)
        mysqlScript.deleteUserTitleSql(config.payUid)
        mysqlScript.updateUserTitleSql(config.payUid)
        mysqlScript.updateMoneySql(200000, 0, 0, 0, config.payUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_title')
        res = Request.post_request_session(url=TestPayCreate.pay_package_url, data=data)
        assert res['code'] == 200
        assert res['body']['success'] == 1
        assert len(res['body']['args']) > 1
        # pytest.assume(mysqlScript.selectMoneySql(103273407, 'money') == 160000)
        assert mysqlScript.selectMoneySql(config.payUid, 'money') == 160000

    @pytest.mark.run(order=2)
    def test_02_TitlePayChangeRenew(self):
        """
          用例描述：
          续test_01步骤，验证爵位续费及返钱到余额（money）
          脚本步骤：
          1.清空背包内物品，模拟开通者数据（更新xs_user_money）
          2.续费子爵
          3.校验【status code】和返回值【body】状态
          4.检查剩余钱值,预期值：（200000 - 60000 + 36000 = 176000）
          """
        mysqlScript.updateMoneySql(200000, 0, 0, 0, config.payUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_title')
        res = Request.post_request_session(url=TestPayCreate.pay_package_url, data=data)
        assert res['code'] == 200
        assert res['body']['success'] == 1
        assert len(res['body']['args']) > 1
        assert mysqlScript.selectMoneySql(config.payUid, 'money') == 176000


if __name__ == '__main__':
    pay = TestPayCreate()