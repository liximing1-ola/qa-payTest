from Common.config import config
from Common import Request, api
from Common.params_Yaml import Yaml
from Common.sqlScript import Mysql
import unittest
from Common import consts, Assert
import sys
from Common.runfailed import Retry

@Retry(max_n=1)
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_package_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

    def test_01_RoomPayNoMoney(self):
        """
        用例描述：
        验证余额不足时，房间一对一打赏
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.房间内一对一打赏
        3.校验【status code】和返回值【body】状态
        4.检查预期返回msg，预期：支付失败
        5.检查被打赏者余额,预期：0
        """
        Mysql.updateMoneySql(0, 0, 0, 0, config.payUid)
        Mysql.updateMoneySql(0, 0, 0, 0, config.testUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_package_1')
        res = Request.post_request_session(url=TestPayCreate.pay_package_url, data=data)
        des = '验证余额不足时，房间进行一对一打赏'
        reason = '用例说明: {}, --失败原因: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200, reason)
        Assert.assert_body(res['body'], 'success', 0, reason)
        Assert.assert_body(res['body'], 'msg', '余额不足，无法支付', reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.testUid), 0, reason)
        consts.CASE_LIST[des] = 'pass'


    def test_02_RoomPayLiveMoney(self):
        """
        用例描述：
        验证余额足够时，直播类型房间（types=live）一对一打赏,打赏分成满足师徒收益的基础上为：52:48
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.直播类房间一对一打赏（打赏100分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额，预期为：52
        5.检查消费记录表消费money（xs_pay_change_new）
        6.检查消费记录表消费方式op
        """
        Mysql.updateMoneySql(30, 30, 30, 10, config.payUid)
        Mysql.updateMoneySql(0, 0, 0, 0, config.testUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_package_1')
        res = Request.post_request_session(url=TestPayCreate.pay_package_url, data=data)
        des = '验证余额足够时，直播类型房间一对一打赏'
        reason = '用例说明: {}, --失败原因: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200, reason)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.testUid, 'money_cash'), 52, reason)
        Assert.assert_equal(Mysql.selectPayChangeSql(config.payUid), 100, reason)
        Assert.assert_equal(Mysql.selectPayChangeOpSql(config.payUid), 'consume', reason)
        consts.CASE_LIST[des] = 'pass'

    def test_03_RoomPayChangeMoney(self):
        """
        用例描述：
        验证余额足够时，非直播类型房间一对一打赏,打赏分成满足师徒收益的基础上为：62:38
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.房间内一对一打赏（打赏100分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额，预期为：62
        5.检查消费记录表消费money（xs_pay_change_new）
        6.检查消费记录表消费方式op
        """
        Mysql.updateMoneySql(30, 30, 30, 10, config.payUid)
        Mysql.updateMoneySql(0, 0, 0, 0, config.testUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_package_2')
        res = Request.post_request_session(url=TestPayCreate.pay_package_url, data=data)
        des = '验证余额足够时，非直播类型房间一对一打赏比例'
        reason = '用例说明: {}, --失败原因: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200, reason)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_len(res['body'], 'args', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.testUid, 'money_cash'), 62, reason)
        Assert.assert_equal(Mysql.selectPayChangeSql(config.payUid), 100, reason)
        Assert.assert_equal(Mysql.selectPayChangeOpSql(config.payUid), 'consume', reason)
        consts.CASE_LIST[des] = 'pass'

    def test_04_livePackCalPayChange(self):
        """
        用例描述：
        验证直播间打赏主播（打包结算主播pack_cal=1），打赏分成满足：6:4，且收入在money_cash账户
        脚本步骤：
        1.构造打赏者和主播数据 （更新xs_user_money和xs_broker_user）
        2.房间内一对一打赏（打赏1000分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额和账户，预期为：money_cash=600
        5.检查打赏者余额
        """
        Mysql.updateChatroomUid(config.pack_cal_uid)
        Mysql.updateBrokerUser(config.pack_cal_uid)
        Mysql.updateMoneySql(100, 0, 0, 0, config.payUid)
        Mysql.updateMoneySql(0, 0, 0, 0, config.pack_cal_uid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pack_cal')
        res = Request.post_request_session(url=TestPayCreate.pay_package_url, data=data)
        des = '验证直播间打赏主播（打包结算主播），打赏分成满足：6:4，且收入在money_cash账户'
        reason = '用例说明: {}, --失败原因: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200, reason)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_len(res['body'], 'args', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.pack_cal_uid, 'money_cash'), 60, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0, reason)
        consts.CASE_LIST[des] = 'pass'

    # @unittest.skip
    def test_05_mentorPayChange(self):
        """
        用例描述：
        验证直播间内打赏一代宗师用户，在师徒收益基础上，分成比例应为7:3
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money和xs_mentor_exp）
        2.房间内一对一打赏（打赏1000分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额和账户，预期为：700
        5.检查打赏者余额
        """
        Mysql.updateMoneySql(100, 0, 0, 0, config.testUid)
        Mysql.updateMoneySql(0, 0, 0, 0, config.payUid)  # 一代宗师
        data = Yaml.read_yaml('Basic.yml', 'dev_mentor_pay')
        res = Request.post_request_session(url=TestPayCreate.pay_package_url, data=data)
        des = '验证直播间内打赏一代宗师用户，在师徒收益基础上，分成比例应为7:3'
        reason = '用例说明: {}, --失败原因: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200, reason)
        Assert.assert_body(res['body'], 'success', 0, reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.testUid), 0, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 70, reason)
        Assert.assert_equal(Mysql.selectPayChangeSql(config.testUid), 0, reason)
        consts.CASE_LIST[des] = 'pass'


if __name__ == '__main__':
    pay = TestPayCreate()
    pay.test_01_RoomPayNoMoney()