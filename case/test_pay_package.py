from common.Config import config
from common import Request
from common.params_Yaml import Yaml
from common.sqlScript import Mysql
import unittest
from common import Consts, Assert
from common.runFailed import Retry
@Retry
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

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
        des = '房间一对一打赏但余额不足'
        Mysql.updateMoneySql(config.payUid)
        Mysql.updateMoneySql(config.testUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_package_1')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 0, reason)
        Assert.assert_body(res['body'], 'msg', '余额不足，无法支付', reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.testUid), 0)
        Consts.CASE_LIST[des] = 'pass'

    def test_02_RoomPayChangeMoney(self):
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
        des = '非直播一对一打赏'
        Mysql.updateMoneySql(config.payUid, 30, 30, 30, 10)
        Mysql.updateMoneySql(config.testUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_package_2')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.testUid, 'money_cash_b'), 62)
        Assert.assert_equal(Mysql.selectPayChangeSql(config.payUid), 100)
        Assert.assert_equal(Mysql.selectPayChangeOpSql(config.payUid), 'consume')
        Consts.CASE_LIST[des] = 'pass'

    def test_03_couponNoStatePayChange(self):
        """
        用例描述：
        有未激活券(state=0)的情况下，验证打赏
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money和xs_user_commodity）
        2.房间内打赏（券可抵扣500分）
        3.校验【status code】和返回值【body】状态，预期结果： "msg": "余额不足，无法支付"
        4.检查被打赏者余额和账户，预期为：0
        5.检查打赏者余额,预期为：3000
        """
        des = '打赏礼物券未激活'
        gift_cid = 54  # 老司机
        Mysql.deleteUserCommoditySql(config.payUid)
        Mysql.insertXsUserCommodity(config.payUid, gift_cid, 1)
        Mysql.updateMoneySql(config.payUid, 3000)
        Mysql.updateMoneySql(config.testUid)
        cid = Mysql.getUserCommodityIdSql(gift_cid, config.payUid)
        payload = {'platform': 'available',
                   'type': 'package',
                   'money': '3000',
                   'params': '{"rid":193186934,"uids":"105002312","positions":"0","position":-1,"giftId":11,"giftNum":1,"price":3000,"cid": %s,"ctype":"coupon","duction_money":500,"version":2,"num":1,"gift_type":"normal","star":0,"show_pac_man_guide":1,"refer":"热门_开黑:room","useCoin":-1}' % cid}
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=payload)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 0, reason)
        Assert.assert_body(res['body'], 'msg', '余额不足，无法支付', reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.testUid), 0)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 3000)
        Consts.CASE_LIST[des] = 'pass'

    def test_04_couponStatePayChange(self):
        """
        用例描述：
        有激活券(state=1)的情况下，验证打赏流程
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money和xs_user_commodity）
        2.房间内打赏（券可抵扣500分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额和账户，预期为：3000 * 0.62 = 1860
        5.检查打赏者余额,预期为：3000 -2500 = 500
        """
        des = '打赏礼物券已激活'
        gift_cid = 54  # 老司机
        Mysql.deleteUserCommoditySql(config.payUid)
        Mysql.insertXsUserCommodity(config.payUid, gift_cid, 1, 1)
        Mysql.updateMoneySql(config.payUid, 3000)
        Mysql.updateMoneySql(config.testUid)
        cid = Mysql.getUserCommodityIdSql(gift_cid, config.payUid)
        payload = {
            'platform': 'available',
            'type': 'package',
            'money': '3000',
            'params': '{"rid":193186934,"uids":"105002312","positions":"0","position":-1,"giftId":11,"giftNum":1,"price":3000,"cid": %s,"ctype":"coupon","duction_money":500,"version":2,"num":1,"gift_type":"normal","star":0,"show_pac_man_guide":1,"refer":"热门_开黑:room","useCoin":-1}' % cid}
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=payload)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.testUid), 1860)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 500)
        Consts.CASE_LIST[des] = 'pass'

    def test_05_RoomToMorePayChange(self):
        """
        用例描述：
        验证非直播类型房间内一对多打赏场景
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.房间内一对多打赏
        3.校验【status code】和返回值【body】状态
        4.检查打赏者余额,预期为：12000-10800=1200
        5.检查被打赏者余额，预期为：600*6*0.7=2520
        """
        des = '礼物打赏多人'
        Mysql.updateMoneySql(config.payUid, 3000, 3000, 3000, 3000)
        Mysql.updateMoneySql(config.testUid_2)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_more')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.testUid_2), 2520)
        Assert.assert_equal(Mysql.selectMoneySql(config.payUid, 'money_cash'), 1200)
        Consts.CASE_LIST[des] = 'pass'


if __name__ == '__main__':
    pay = TestPayCreate()
    pay.test_01_RoomPayNoMoney()