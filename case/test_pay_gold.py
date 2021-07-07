from common.Config import config
from common import Request
from common.params_Yaml import Yaml
from common.sqlScript import Mysql
import unittest
from common import Consts
from common import Assert
from common.runFailed import Retry
@Retry(max_n=2)
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

    def test_01_NoGoldPayGoldGift(self):
        """
        用例描述：
        验证账户内金豆不足时打赏金豆礼物的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money_extend）
        2.房间内打赏金豆礼物
        3.校验【status code】和返回值【body】状态
        4.检查预期返回msg，预期：支付失败，提示Toast
        5.检查被打赏者余额,预期：0
        """
        des = '验证账户内金豆不足时打赏金豆礼物的场景'
        Mysql.deleteUserBeanSql(config.payUid)
        Mysql.deleteUserBeanSql(config.testUid)
        Mysql.updateMoneySql(config.payUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_gold_NoGold')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 0, reason)
        Assert.assert_body(res['body'], 'msg', '金豆不足', reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.testUid), 0)
        Consts.CASE_LIST[des] = 'pass'

    @unittest.skip
    def test_02_GoldPayGoldGift(self):
        """
        用例描述：
        验证打赏金豆礼物的场景（足够）
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money, xs_user_money_extend）
        2.房间内打赏金豆礼物
        3.校验【status code】和返回值【body】状态
        4.检查预期返回msg，预期：支付失败，提示Toast
        5.检查被打赏者余额,预期：0
        """
        des = '验证打赏金豆礼物时金豆足够的场景'
        Mysql.updateMoneySql(config.payUid)
        Mysql.updateMoneySql(config.testUid)
        Mysql.deleteXsBrokerUser(config.testUid)  # 删除用户工会记录
        Mysql.deleteXsChatroom(config.testUid)  # 删除用户商业房
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_chatGift')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 0, reason)
        Assert.assert_body(res['body'], 'msg', '余额不足，无法支付', reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.testUid), 0)
        Consts.CASE_LIST[des] = 'pass'

    @unittest.skip
    def test_03_MoneyConvertGoldPayGift(self):
        """
        用例描述：
        验证打赏金豆礼物的场景（不足）
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money, xs_user_money_extend）
        2.房间内打赏金豆礼物
        3.校验【status code】和返回值【body】状态
        4.检查预期返回msg，预期：支付失败，提示Toast
        5.检查被打赏者余额,预期：0
        """
        des = '验证打赏金豆礼物时金豆不足用钻转换的场景'
        Mysql.updateMoneySql(config.payUid)
        Mysql.updateMoneySql(config.testUid)
        Mysql.deleteXsBrokerUser(config.testUid)  # 删除用户工会记录
        Mysql.deleteXsChatroom(config.testUid)  # 删除用户商业房
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_chatGift')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 0, reason)
        Assert.assert_body(res['body'], 'msg', '余额不足，无法支付', reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.testUid), 0)
        Consts.CASE_LIST[des] = 'pass'

    @unittest.skip
    def test_04_ImMoneyPayChangeGoldDeduct(self):
        """
        用例描述：
        验证打赏金豆礼物的场景（不足）
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money, xs_user_money_extend）
        2.房间内打赏金豆礼物
        3.校验【status code】和返回值【body】状态
        4.检查预期返回msg，预期：支付失败，提示Toast
        5.检查被打赏者余额,预期：0
        """
        des = '验证私聊场景打赏钻石礼物时金豆抵扣平台手续费的场景'
        Mysql.updateMoneySql(config.payUid)
        Mysql.updateMoneySql(config.testUid)
        Mysql.deleteXsBrokerUser(config.testUid)  # 删除用户工会记录
        Mysql.deleteXsChatroom(config.testUid)  # 删除用户商业房
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_chatGift')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 0, reason)
        Assert.assert_body(res['body'], 'msg', '余额不足，无法支付', reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.testUid), 0)
        Consts.CASE_LIST[des] = 'pass'

    @unittest.skip
    def test_05_RoomMoneyConvertGoldPayGift(self):
        """
        用例描述：
        验证打赏金豆礼物的场景（不足）
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money, xs_user_money_extend）
        2.房间内打赏金豆礼物
        3.校验【status code】和返回值【body】状态
        4.检查预期返回msg，预期：支付失败，提示Toast
        5.检查被打赏者余额,预期：0
        """
        des = '验证房间内打赏金豆礼物时金豆抵扣平台手续费的场景'
        Mysql.updateMoneySql(config.payUid)
        Mysql.updateMoneySql(config.testUid)
        Mysql.deleteXsBrokerUser(config.testUid)  # 删除用户工会记录
        Mysql.deleteXsChatroom(config.testUid)  # 删除用户商业房
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_chatGift')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 0, reason)
        Assert.assert_body(res['body'], 'msg', '余额不足，无法支付', reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.testUid), 0)
        Consts.CASE_LIST[des] = 'pass'

    @unittest.skip
    def test_06_GoldPayChangeCombo(self):
        """
        用例描述：
        验证打赏金豆礼物的场景（不足）
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money, xs_user_money_extend）
        2.房间内打赏金豆礼物
        3.校验【status code】和返回值【body】状态
        4.检查预期返回msg，预期：支付失败，提示Toast
        5.检查被打赏者余额,预期：0
        """
        des = '验证打赏金豆礼物时金豆不足用钻转换的场景'
        Mysql.updateMoneySql(config.payUid)
        Mysql.updateMoneySql(config.testUid)
        Mysql.deleteXsBrokerUser(config.testUid)  # 删除用户工会记录
        Mysql.deleteXsChatroom(config.testUid)  # 删除用户商业房
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_chatGift')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 0, reason)
        Assert.assert_body(res['body'], 'msg', '余额不足，无法支付', reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.testUid), 0)
        Consts.CASE_LIST[des] = 'pass'