from common.Config import config
from common import Request
from common.params_Yaml import Yaml
from common.sqlScript import Mysql
import unittest
import pytest
from common import Consts, Assert

class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

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
        Mysql.selectUserCommoditySql(config.payUid)
        Mysql.deleteUserTitleSql(config.payUid)
        Mysql.updateUserTitleSql(config.payUid)
        Mysql.updateMoneySql(200000, 0, 0, 0, config.payUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_title')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        des = '验证爵位开通及返钱的场景'
        reason = '用例说明: {}, --失败原因: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.payUid, 'money'), 160000)
        Consts.CASE_LIST[des] = 'pass'

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
        Mysql.updateMoneySql(200000, 0, 0, 0, config.payUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_title')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        des = '验证爵位续费及返钱的场景'
        reason = '用例说明: {}, --失败原因: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.payUid, 'money'), 176000)
        Consts.CASE_LIST[des] = 'pass'


if __name__ == '__main__':
    pay = TestPayCreate()