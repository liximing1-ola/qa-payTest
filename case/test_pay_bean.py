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

    def setUp(self) -> None:
        # 每个case执行前处理下数据
        Mysql.deleteUserBeanSql(config.payUid)
        Mysql.deleteUserBeanSql(config.testUid)
        pass

    def tearDown(self) -> None:
        pass

    def test_01_NoBeanPayBeanGift(self):
        """
        用例描述：
        验证账户内金豆不足时打赏金豆礼物的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money_extend）
        2.房间内打赏金豆礼物
        3.校验【status code】和返回值【body】状态
        4.检查预期返回msg，预期：支付失败，提示Toast
        5.检查被打赏者金豆余额,预期：0
        """
        des = '验证账户内金豆不足时打赏金豆礼物的场景'
        Mysql.updateMoneySql(config.payUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_gold_NoBean')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 0, reason)
        Assert.assert_body(res['body'], 'msg', '金豆不足', reason)
        Assert.assert_equal(Mysql.selectBeanSql(config.testUid), 0)
        Consts.CASE_LIST[des] = 'pass'

    def test_02_beanPayChangeGoldGift(self):
        """
        用例描述：
        验证打赏金豆礼物的场景（金豆足够）
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money_extend）
        2.房间内打赏金豆礼物
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者金豆余额，预期为：0
        5.检查打赏者剩余金豆余额，预期为：6000 * 0.7 = 4200
        """
        des = '验证正常打赏金豆礼物的场景'
        Mysql.updateBeanSql(config.payUid, 6000)
        data = Yaml.read_yaml('Basic.yml', 'dev_gold_BeanEnough')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectBeanSql(config.payUid), 0)
        Assert.assert_equal(Mysql.selectBeanSql(config.testUid), 4200)
        Consts.CASE_LIST[des] = 'pass'

    def test_03_MoneyConvertGoldPayGift(self):
        """
        用例描述：
        验证打赏金豆礼物时金豆不足用钻转换的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money, xs_user_money_extend）
        2.房间内打赏金豆礼物
        3.校验【status code】和返回值【body】状态
        4.检查打赏者金豆余额，预期为：500
        5.检查打赏者钻石余额，预期为：10000 - 1000（转换） = 9000
        6.检查被打赏者金豆余额，预期为：1000 * 0.7 = 700
        """
        des = '验证打赏金豆礼物时金豆不足用钻转换的场景'
        Mysql.updateMoneySql(config.payUid, 10000)
        Mysql.updateMoneySql(config.testUid)
        Mysql.updateBeanSql(config.payUid, 500)
        data = Yaml.read_yaml('Basic.yml', 'dev_gold_moneyToBean')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectBeanSql(config.payUid), 500)
        Assert.assert_equal(Mysql.selectMoneySql(config.payUid, money_type='money'), 9000)
        Assert.assert_equal(Mysql.selectBeanSql(config.testUid), 700)
        Consts.CASE_LIST[des] = 'pass'

    def test_04_ImMoneyPayChangeBeanDeduct(self):
        """
        用例描述：
        验证私聊场景打赏钻石礼物时金豆抵扣平台手续费的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money, xs_user_money_extend）
        2.私聊页打赏钻石礼物
        3.校验【status code】和返回值【body】状态
        4.检查打赏者金豆余额，预期为：200 - 200 = 0
        5.检查打赏者钻石余额，预期为：1000 - 800 = 200
        6.检查被打赏者钻石余额，预期为：1000 * 0.72 = 720
        """
        des = '验证私聊场景打赏钻石礼物时金豆抵扣平台手续费的场景'
        Mysql.updateMoneySql(config.payUid, 1000)
        Mysql.updateMoneySql(config.testUid)
        Mysql.updateBeanSql(config.payUid, 200)
        data = Yaml.read_yaml('Basic.yml', 'dev_gold_BeanDeduct')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectBeanSql(config.payUid), 0)
        Assert.assert_equal(Mysql.selectMoneySql(config.payUid, money_type='money'), 200)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.testUid), 720)
        Consts.CASE_LIST[des] = 'pass'

    def test_05_RoomMoneyConvertGoldPayGift(self):
        """
        用例描述：
        验证房间内打赏钻石礼物时金豆抵扣平台手续费的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money, xs_user_money_extend）
        2.房间内打赏金豆礼物
        3.校验【status code】和返回值【body】状态
        4.检查打赏者金豆余额，预期为：400 - 300 = 100
        5.检查打赏者钻石余额，预期为：1000 - 700 = 300
        6.检查被打赏者钻石余额，预期为：1000 * 0.62 = 620
        """
        des = '验证房间内打赏钻石礼物时金豆抵扣平台手续费的场景'
        Mysql.updateMoneySql(config.payUid, 1000)
        Mysql.updateMoneySql(config.testUid)
        Mysql.updateBeanSql(config.payUid, 400)
        data = Yaml.read_yaml('Basic.yml', 'dev_gold_RoomBeanDeduct')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectBeanSql(config.payUid), 100)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.testUid), 620)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 300)
        Consts.CASE_LIST[des] = 'pass'

    def test_06_MoneyConvertGoldPayGift(self):
        """
        用例描述：
        验证房间内打赏钻石礼物时金豆抵扣平台手续费的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money, xs_user_money_extend）
        2.房间内打赏金豆礼物
        3.校验【status code】和返回值【body】状态
        4.检查预期返回msg，预期：支付失败，提示Toast
        5.检查被打赏者余额,预期：0
        """
        des = '验证房间内打赏钻石礼物时金豆抵扣平台手续费但钻石少于礼物价格时的场景'
        Mysql.updateMoneySql(config.payUid, 700)
        Mysql.updateMoneySql(config.testUid)
        Mysql.updateBeanSql(config.payUid, 400)
        data = Yaml.read_yaml('Basic.yml', 'dev_gold_RoomBeanDeduct')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 0, reason)
        Assert.assert_body(res['body'], 'msg', '余额不足，无法支付', reason)
        Consts.CASE_LIST[des] = 'pass'

    def test_07_BeanPayChangeCombo(self):
        """
        用例描述：
        验证卡座内购买套餐的场景（钻补）
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money, xs_user_money_extend）
        2.卡座内购买酒桌套餐
        3.校验【status code】和返回值【body】状态
        4.检查购买者金豆余额，预期为：400
        5.检查购买者钻石余额，预期为：80000 - 79900 = 100
        """
        des = '验证卡座内购买套餐的场景'
        Mysql.deleteUserCommoditySql(config.payUid)
        Mysql.updateMoneySql(config.payUid, 80000)
        Mysql.updateBeanSql(config.payUid, 400)
        data = Yaml.read_yaml('Basic.yml', 'dev_gold_Combo')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 100)
        Assert.assert_equal(Mysql.selectBeanSql(config.payUid), 400)
        Consts.CASE_LIST[des] = 'pass'