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
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

    @pytest.mark.run(order=1)
    def test_01_shopPayChangeMoney(self):
        """
        用例描述：
        验证商城购买道具逻辑
        脚本步骤：
        1.构造购买者数据 （更新xs_user_money和xs_user_commodity）
        2.商城内购买礼物道具*1
        3.校验【status code】和返回值【body】状态
        4.检查购买者余额 (200-100=100)
        5.检查背包内物品
        """
        cid=329  # 四叶草
        des = '检查商城内购买道具的流程'
        Mysql.updateMoneySql(config.payUid, 0, 100, 100, 0)
        Mysql.deleteUserCommoditySql(config.payUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_shop')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 100)
        Assert.assert_equal(Mysql.checkUserCommoditySql(cid, config.payUid), 1)
        Consts.CASE_LIST[des] = 'pass'

    @pytest.mark.run(order=2)
    def test_02_shopPayChangeBuyMore(self):
        """
        用例描述：
        验证商城购买多个道具时
        脚本步骤：
        1.构造购买者数据 （更新xs_user_money和xs_user_commodity）
        2.商城内购买礼物道具*10 9900*10=99000
        3.校验【status code】和返回值【body】状态
        4.检查购买者余额 (103000-99000=4000)
        5.检查背包内物品
        """
        cid=340  # 小天使
        des = '检查商城内购买多个道具时场景'
        Mysql.updateMoneySql(config.payUid, 1000, 100000, 1000, 1000)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_more_shop')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 4000)
        Assert.assert_equal(Mysql.checkUserCommoditySql(cid, config.payUid), 10)
        Consts.CASE_LIST[des] = 'pass'

    @pytest.mark.run(order=3)
    def test_03_shopGiftToUser(self):
        """
        用例描述：
        验证商城购买的道具在房间内赠送给其他人，他人收到的分成比在师徒收益上为 62：38
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.打赏背包道具 cid：340 * 1
        3.校验【status code】和返回值【body】状态
        4.检查背包内物品
        5.检查被打赏者余额 990*0.62 = 6138
        """
        des = '检查背包礼物赠送打赏的场景'
        bag_gift_cid = 340
        Mysql.updateMoneySql(config.payUid)
        Mysql.updateMoneySql(config.testUid)
        cid = int(Mysql.getUserCommodityIdSql(bag_gift_cid, config.payUid))
        payload = 'platform=available&type=package&money=9900&params=%7B%22rid%22%3A193185484%2C%22uids%22%3A%22105002312%22%2C%22positions%22%3A%220%22%2C%22position%22%3A-1%2C%22giftId%22%3A54%2C%22giftNum%22%3A1%2C%22price%22%3A9900%2C%22cid%22%3A{}%2C%22ctype%22%3A%22gift%22%2C%22duction_money%22%3A0%2C%22version%22%3A2%2C%22num%22%3A1%2C%22gift_type%22%3A%22normal%22%2C%22star%22%3A0%2C%22refer%22%3A%22%E7%83%AD%E9%97%A8%3Aroom%22%2C%22useCoin%22%3A-1%7D'.format(cid)
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=payload)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.checkUserCommoditySql(bag_gift_cid, config.payUid), 9)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.testUid), 6138)
        Consts.CASE_LIST[des] = 'pass'

    @pytest.mark.run(order=4)
    def test_04_shopGiftToUserNoEnough(self):
        """
        用例描述：
        验证商城购买的道具赠送时不足的情况
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.打赏背包道具 cid：340 * 10
        3.校验【status code】和返回值【body】状态
        4.检查背包内物品
        5.检查被打赏者余额 预期：0
        """
        des = '检查赠送背包内物品时，物品不足抵扣的场景'
        bag_gift_cid = 340
        Mysql.updateMoneySql(config.payUid)
        Mysql.updateMoneySql(config.testUid)
        cid = Mysql.getUserCommodityIdSql(bag_gift_cid, config.payUid)
        payload = 'platform=available&type=package&money=99000&params=%7B%22rid%22%3A193185484%2C%22uids%22%3A%22105002312%22%2C%22positions%22%3A%220%22%2C%22position%22%3A-1%2C%22giftId%22%3A54%2C%22giftNum%22%3A10%2C%22price%22%3A9900%2C%22cid%22%3A{}%2C%22ctype%22%3A%22gift%22%2C%22duction_money%22%3A0%2C%22version%22%3A2%2C%22num%22%3A10%2C%22gift_type%22%3A%22normal%22%2C%22star%22%3A0%2C%22refer%22%3A%22%E7%83%AD%E9%97%A8%3Aroom%22%2C%22useCoin%22%3A-1%7D'.format(cid)
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=payload)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 0, reason)
        Assert.assert_body(res['body'], 'msg', '余额不足，无法支付', reason)
        Assert.assert_equal(Mysql.checkUserCommoditySql(bag_gift_cid, config.payUid), 9)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.testUid), 0)
        Consts.CASE_LIST[des] = 'pass'