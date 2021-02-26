from Common.config import config
from Common import Request, api
from Common.params_Yaml import Yaml
from Common.sqlScript import mysqlScript
import unittest
import pytest


class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_package_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

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
        mysqlScript.updateMoneySql(0, 100, 100, 0, config.payUid)
        mysqlScript.deleteUserCommoditySql(config.payUid, 10)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_shop')
        res = Request.post_request_session(url=TestPayCreate.pay_package_url, data=data)
        assert res['code'] == 200
        api.errorMsg(res)
        assert res['body']['success'] == 1
        assert mysqlScript.selectAllMoneySql(config.payUid) == 100
        assert mysqlScript.checkUserCommoditySql(329, config.payUid) == 1

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
        mysqlScript.updateMoneySql(1000, 100000, 1000, 1000, config.payUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_more_shop')
        res = Request.post_request_session(url=TestPayCreate.pay_package_url, data=data)
        assert res['code'] == 200
        api.errorMsg(res)
        assert res['body']['success'] == 1
        assert mysqlScript.selectAllMoneySql(config.payUid) == 4000
        assert mysqlScript.checkUserCommoditySql(340, config.payUid) == 10

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
        mysqlScript.updateMoneySql(0, 0, 0, 0, config.payUid)
        mysqlScript.updateMoneySql(0, 0, 0, 0, config.testUid)
        cid = int(mysqlScript.getUserCommodityIdSql(340, config.payUid))
        payload = 'platform=available&type=package&money=9900&params=%7B%22rid%22%3A193185484%2C%22uids%22%3A%22105002312%22%2C%22positions%22%3A%220%22%2C%22position%22%3A-1%2C%22giftId%22%3A54%2C%22giftNum%22%3A1%2C%22price%22%3A9900%2C%22cid%22%3A{}%2C%22ctype%22%3A%22gift%22%2C%22duction_money%22%3A0%2C%22version%22%3A2%2C%22num%22%3A1%2C%22gift_type%22%3A%22normal%22%2C%22star%22%3A0%2C%22refer%22%3A%22%E7%83%AD%E9%97%A8%3Aroom%22%2C%22useCoin%22%3A-1%7D'.format(cid)
        res = Request.post_request_session(url=TestPayCreate.pay_package_url, data=payload)
        assert res['code'] == 200
        api.errorMsg(res)
        assert res['body']['success'] == 1
        assert mysqlScript.checkUserCommoditySql(340, config.payUid) == 9
        assert mysqlScript.selectAllMoneySql(config.testUid) == 6138

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
        mysqlScript.updateMoneySql(0, 0, 0, 0, config.payUid)
        mysqlScript.updateMoneySql(0, 0, 0, 0, config.testUid)
        cid = mysqlScript.getUserCommodityIdSql(340, config.payUid)
        payload = 'platform=available&type=package&money=99000&params=%7B%22rid%22%3A193185484%2C%22uids%22%3A%22105002312%22%2C%22positions%22%3A%220%22%2C%22position%22%3A-1%2C%22giftId%22%3A54%2C%22giftNum%22%3A10%2C%22price%22%3A9900%2C%22cid%22%3A{}%2C%22ctype%22%3A%22gift%22%2C%22duction_money%22%3A0%2C%22version%22%3A2%2C%22num%22%3A10%2C%22gift_type%22%3A%22normal%22%2C%22star%22%3A0%2C%22refer%22%3A%22%E7%83%AD%E9%97%A8%3Aroom%22%2C%22useCoin%22%3A-1%7D'.format(cid)
        res = Request.post_request_session(url=TestPayCreate.pay_package_url, data=payload)
        assert res['code'] == 200
        api.errorMsg(res)
        assert res['body']['success'] == 0
        assert res['body']['msg'] == '物品不足抵扣！'
        assert mysqlScript.checkUserCommoditySql(340, config.payUid) == 9
        assert mysqlScript.selectAllMoneySql(config.testUid) == 0