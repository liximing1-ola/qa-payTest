from common.Config import config
from common import Request
from common.params_Yaml import Yaml
from common.sqlScript import mysql
import unittest
import pytest
from common import Consts, Assert
from common.runFailed import Retry

@Retry(max_n=2)
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.pt_host + 'pay/create'

    @unittest.skip('case 取消')
    @pytest.mark.run(order=1)
    def test_01_TitlePayChangeMoney(self):
        """
        用例描述：
        验证爵位开通但海外爵位购买不反钻石
        脚本步骤：
        1.清空背包内物品，模拟开通者数据（更新xs_user_money）
        2.开通子爵
        3.校验【status code】和返回值【body】状态
        4.检查剩余钱值,预期值：（50000 - 40000  = 10000）
        """
        des = '检查PT用户开通爵位不返钱的流程'
        mysql.deleteUserCommoditySql(config.pt_payUid)
        mysql.deleteUserTitleSql(config.pt_payUid)
        mysql.updateUserTitleSql(config.pt_payUid)
        mysql.updateMoneySql(config.pt_payUid, 50000)
        data = Yaml.read_yaml('Basic_pt.yml', 'pt_pay_title')
        res = Request.pt_post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(mysql.selectMoneySql(config.pt_payUid, 'money'), 10000)
        Consts.CASE_LIST[des] = 'pass'

    @unittest.skip('case取消')
    @pytest.mark.run(order=2)
    def test_02_TitlePayChangeRenew(self):
        """
        用例描述：
        续01步骤，验证爵位续费*60%
        脚本步骤：
        1.清空背包内物品，模拟开通者数据（更新xs_user_money）
        2.续费子爵
        3.校验【status code】和返回值【body】状态
        4.检查剩余钱值,预期值：（40000 - 24000  = 16000）
        """
        des = '检查PT用户续费爵位的流程'
        mysql.updateMoneySql(config.pt_payUid, 40000)
        data = Yaml.read_yaml('Basic_pt.yml', 'pt_pay_title')
        res = Request.pt_post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(mysql.selectMoneySql(config.pt_payUid, 'money'), 16000)
        Consts.CASE_LIST[des] = 'pass'