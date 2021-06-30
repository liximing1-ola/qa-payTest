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

    def test_01_openBoxPayChange(self):
        """
        用例描述：
        验证背包内开箱子得到物品
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
         * 清空用户背包内所有物品
         * 用户背包内插入箱子
         * 修改用户指定箱子礼物刷新
         * 修改用户钱包余额
        2.openBox
        3.校验【status code】和返回值【body】状态
        4.检查账户余额，预期值为：100
        5.检查背包内开出物品，预期值应为：2（赠送头像框，开出礼物个数）
        """
        des = '检查背包内开箱子获得对应物品的场景'
        Mysql.deleteUserBox(config.payUid)
        Mysql.deleteUserCommoditySql(config.payUid)
        Mysql.insertXsUserCommodity(config.payUid, 2, 1)
        Mysql.insertXsUserBox(9, config.payUid, 'copper')
        Mysql.updateMoneySql(config.payUid, 400, 100, 100, 100)
        data = Yaml.read_yaml('Basic.yml', 'dev_shop_box')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 100)
        Assert.assert_equal(Mysql.selectUserCommodity(config.payUid), 2)
        Consts.CASE_LIST[des] = 'pass'

    def test_02_openMoreBoxPayChange(self):
        """
        用例描述：
        验证背包内开箱子得到物品
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
            * 清空用户背包内所有物品
            * 用户背包内插入多个箱子*6 2100*6=12600
            * 修改用户指定箱子礼物刷新
            * 修改用户钱包余额
        2.openBox
        3.校验【status code】和返回值【body】状态
        4.检查账户余额，预期值为：0
        5.检查背包内开出物品，预期值应大于2（赠送头像框*1，开出礼物个数大于*2）
        """
        des = '检查背包内多开箱子获得多个物品的场景'
        Mysql.deleteUserBox(config.payUid)
        Mysql.deleteUserCommoditySql(config.payUid)
        Mysql.insertXsUserCommodity(config.payUid, 3, 6)
        Mysql.insertXsUserBox(9, config.payUid, 'silver')
        Mysql.updateMoneySql(config.payUid, 12600)
        data = Yaml.read_yaml('Basic.yml', 'dev_shop_moreBox')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0)
        Assert.assert_len(Mysql.selectUserCommodity(config.payUid), 12)
        Consts.CASE_LIST[des] = 'pass'

    def test_03_giveBoxPayChange(self):
        """
        用例描述：
        验证房间内送箱子逻辑正常
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
        2.giveBox
        3.校验【status code】和返回值【body】状态
        4.检查账户余额，预期值为：100
        5.检查收箱用户账户余额，预期值为：大于0
        """
        des = '检查房间内赠送箱子打赏的场景'
        Mysql.updateMoneySql(config.payUid, 400, 100, 100, 100)
        Mysql.updateMoneySql(config.testUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_package_giveBox')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 100)
        Assert.assert_len(Mysql.selectAllMoneySql(config.payUid), 0)
        Consts.CASE_LIST[des] = 'pass'

    def test_04_giveBoxMorePeople(self):
        """
        用例描述：
        验证房间内送箱子给多个人时逻辑正常
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
        2.giveBox
        3.校验【status code】和返回值【body】状态
        4.检查账户余额，预期值为：10000 - 2100*2*2 = 1600
        5.检查收箱用户账户余额，预期值为：大于0
        """
        des = '检查房间内赠送多人多个箱子的消费场景'
        Mysql.updateMoneySql(config.payUid, 10000)
        Mysql.updateMoneySql(config.testUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_OpenBox')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 1600)
        Assert.assert_len(Mysql.selectAllMoneySql(config.payUid), 1000)
        Consts.CASE_LIST[des] = 'pass'