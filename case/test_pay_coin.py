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

    def test_01_moneyChangeExchangeCoin(self):
        """
        用例描述：
        验证money兑换金币流程
        脚本步骤：
        1.构造用户数据 （更新xs_user_money）
        2.金币兑换
        3.校验【status code】和返回值【body】状态
        4.检查账户余额（money, gold_coin） 1000-600=400
        """
        des = '余额兑换金币流程'
        Mysql.updateMoneySql(config.payUid, 1000)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_coin')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 400)
        Assert.assert_equal(Mysql.selectCoinSql(config.payUid), 600)
        Consts.CASE_LIST[des] = 'pass'

    def test_02_roomChangePayCoin(self):
        """
        用例描述：
        验证房间内打赏金币流程
        脚本步骤：
        1.构造用户数据 （更新xs_user_money）
        2.房间打赏金币礼物
        3.校验【status code】和返回值【body】状态
        4.检查打赏者账户余额（gold_coin） 100 - 20*3 = 40
        5.检查被打赏者账户余额（gold_coin）  20 * 0.6 = 12
        """
        des = '房间打赏金币礼物的消费场景'
        Mysql.updateMoneySql(config.payUid, 0, 0, 0, 0, 100)
        Mysql.updateMoneySql(config.testUid)
        Mysql.updateMoneySql(config.testUid_2)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_coins')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectCoinSql(config.payUid), 60)
        Assert.assert_equal(Mysql.selectCoinSql(config.testUid_2), 12)
        Consts.CASE_LIST[des] = 'pass'