from common.Config import config
from common import Request
from common.params_Yaml import Yaml
from common.sqlScript import Mysql
import unittest
import pytest
from common import Consts, Assert
from common.runFailed import Retry

@Retry(max_n=2)
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.pt_host + 'pay/create'

    @pytest.mark.run(order=1)
    def test_01_shopPayChangeMoney(self):
        """
        用例描述：
        验证商城购买道具逻辑
        脚本步骤：
        1.构造购买者数据 （更新xs_user_money和xs_user_commodity）
        2.商城内购买礼物道具*1 cid=5
        3.校验【status code】和返回值【body】状态
        4.检查购买者余额 (300+300-600=0)
        5.检查背包内物品
        """
        cid = 5  # 铜钥匙
        des = '检查商城内购买道具的流程'
        Mysql.updateMoneySql(config.pt_payUid, 0, 300, 300, 0)
        Mysql.deleteUserCommoditySql(config.pt_payUid)
        data = Yaml.read_yaml('Basic_pt.yml', 'pt_pay_shop')
        res = Request.pt_post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.pt_payUid), 0)
        Assert.assert_equal(Mysql.checkUserCommoditySql(cid, config.pt_payUid), 1)
        Consts.CASE_LIST[des] = 'pass'

    @pytest.mark.run(order=2)
    def test_02_shopPayChangeBuyMore(self):
        """
        用例描述：
        验证商城购买多个道具时
        脚本步骤：
        1.构造购买者数据 （更新xs_user_money和xs_user_commodity）
        2.商城内购买礼物道具*3 2100*3
        3.校验【status code】和返回值【body】状态
        4.检查购买者余额 (40000-6300=33700)
        5.检查背包内物品(6把钥匙。6个头像框)
        """
        cid = 6  # 银钥匙
        des = '检查商城内购买多个道具时场景'
        Mysql.updateMoneySql(config.pt_payUid, 10000, 10000, 10000, 10000)
        data = Yaml.read_yaml('Basic_pt.yml', 'pt_pay_moreShop')
        res = Request.pt_post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.pt_payUid), 33700)
        Assert.assert_equal(Mysql.checkUserCommoditySql(cid, config.pt_payUid), 12)
        Consts.CASE_LIST[des] = 'pass'