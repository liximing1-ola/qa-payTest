from Common.Config import config
from Common import Request
from Common.params_Yaml import Yaml
from Common.sqlScript import Mysql
import unittest
from Common import Consts
from Common import Assert
from Common.runFailed import Retry

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
        Mysql.deleteUserCommoditySql(config.payUid, 17)
        Mysql.insertXsUserCommodity(config.payUid, 2, 1)
        Mysql.updateXsUserBox(9, config.payUid, 'copper')
        Mysql.updateMoneySql(400, 100, 100, 100, config.payUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_shop_box')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        des = '检查背包内开箱后正常开出物品'
        reason = '用例说明: {}, --失败原因: {}'.format(des, res['body'])
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
            * 用户背包内插入多个箱子*6
            * 修改用户指定箱子礼物刷新
            * 修改用户钱包余额
        2.openBox
        3.校验【status code】和返回值【body】状态
        4.检查账户余额，预期值为：0
        5.检查背包内开出物品，预期值应大于2（赠送头像框*1，开出礼物个数大于*2）
        """
        Mysql.deleteUserCommoditySql(config.payUid, 17)
        Mysql.insertXsUserCommodity(config.payUid, 3, 6)
        Mysql.updateXsUserBox(9, config.payUid, 'silver')
        Mysql.updateMoneySql(12600, 0, 0, 0, config.payUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_shop_moreBox')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        des = '检查背包内开多个箱子后正常开出物品'
        reason = '用例说明: {}, --失败原因: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0)
        Assert.assert_len(Mysql.selectUserCommodity(config.payUid), 12)
        Consts.CASE_LIST[des] = 'pass'

    def test_03_giveBoxPayChange(self):
        """
        用例描述：
        验证房间内送箱子玩法
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity）
        2.giveBox
        3.校验【status code】和返回值【body】状态
        4.检查账户余额
        5.检查背包内开出物品
        """
        pass