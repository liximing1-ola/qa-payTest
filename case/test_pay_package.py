from common.Config import config
from common.method import reason
from common.conMysql import conMysql
from common.Request import post_request_session
import unittest
from common.Assert import assert_code, assert_body, assert_equal
from common import basicData
from common.Consts import case_list, result
from common.runFailed import Retry
@Retry
class TestPayCreate(unittest.TestCase):
    pay_url = config.pay_url

    def test_01_RoomPayNoMoney(self):
        """
        用例描述：
        验证余额不足时，房间一对一打赏
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏流程
        3.校验接口状态和返回值数据
        4.检查预期返回msg，预期：支付失败
        5.检查被打赏者余额,预期：0
        """
        des = '房间1V1打赏但余额不足的场景'
        conMysql.updateUserMoneyClearSql(config.payUid, config.testUid)
        data = basicData.encodeData(payType='package', money=100, rid=193185408, uid=config.testUid, giftId=5)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, reason(des, res))
        assert_body(res['body'], 'msg', '余额不足，无法支付', reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.testUid), 0)
        case_list[des] = result

    def test_02_RoomPayChangeMoney(self):
        """
        用例描述：
        验证余额足够时，非直播类型房间一对一打赏,打赏分成满足师徒收益的基础上为：62:38
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.62 = 62
        """
        des = '非直播1V1打赏场景'
        conMysql.updateMoneySql(config.payUid, money=30, money_cash=30, money_cash_b=30, money_b=10)
        conMysql.updateMoneySql(config.testUid)
        data = basicData.encodeData(payType='package', money=100, rid=config.super_live_role['auto_rid'], uid=config.testUid, giftId=5)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('single_money', config.testUid), 62)
        case_list[des] = result

    def test_03_couponNoStatePayChange(self):
        """
        用例描述：
        有未激活券(state=0)的情况下，验证打赏
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内打赏（券可抵扣500分）
        3.校验接口状态和返回值数据
        4.预期结果： "msg": "余额不足，无法支付"
        5.检查被打赏者余额和账户，预期为：0
        6.检查打赏者余额,预期为：3000
        """
        des = '打赏礼物使用未激活券的场景'
        gift_cid = 54  # 老司机
        conMysql.deleteUserAccountSql('user_commodity', config.payUid)
        conMysql.insertXsUserCommodity(config.payUid, gift_cid, num=1)
        conMysql.updateMoneySql(config.payUid, money=3000)
        conMysql.updateMoneySql(config.testUid)
        cid = conMysql.selectUserMoneySql('id_commodity', config.payUid, cid=gift_cid)
        data = basicData.encodeData(payType='package', rid=config.live_role['auto_rid'], uid=config.testUid, giftId=11, money=3000,
                                    package_cid=cid, ctype='coupon', duction_money=500)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, reason(des, res))
        assert_body(res['body'], 'msg', '余额不足，无法支付', reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.testUid), 0)
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 3000)
        case_list[des] = result

    def test_04_couponStatePayChange(self):
        """
        用例描述：
        有激活券(state=1)的情况下，验证打赏流程
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内打赏（券可抵扣500分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为：3000 * 0.62 = 1860
        5.检查打赏者余额,预期为：3000 -2500 = 500
        """
        des = '打赏礼物时有激活券的场景'
        gift_cid = 54  # 老司机
        conMysql.deleteUserAccountSql('user_commodity', config.payUid)
        conMysql.insertXsUserCommodity(config.payUid, gift_cid, num=1, state=1)
        conMysql.updateMoneySql(config.payUid, money=3000)
        conMysql.updateMoneySql(config.testUid)
        cid = conMysql.selectUserMoneySql('id_commodity', config.payUid, cid=gift_cid)
        data = basicData.encodeData(payType='package', rid=config.live_role['auto_rid'], uid=config.testUid, giftId=11, money=3000,
                                    package_cid=cid, ctype='coupon', duction_money=500)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.testUid), 1860)
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 500)
        case_list[des] = result

    def test_05_RoomToMorePayChange(self):
        """
        用例描述：
        验证非直播类型房间内一对多打赏场景
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对多打赏流畅
        3.校验接口状态和返回值数据
        4.检查打赏者余额,预期为：12000-10800=1200
        5.检查被打赏者余额，预期为：600*6*0.7=2520
        """
        des = '房间内打赏多人场景'
        conMysql.updateMoneySql(config.payUid, money=3000, money_cash=3000, money_cash_b=3000, money_b=3000)
        conMysql.updateMoneySql(config.testUid_2)
        data = basicData.encodeData(payType='package-more', giftId=10, num=6, money=600,
                                    uids=('105002312', '100500131', '100500205'))
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'], 200)
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('single_money', config.testUid_2), 2520)
        assert_equal(conMysql.selectUserMoneySql('single_money', config.payUid, money_type='money_cash'), 1200)
        case_list[des] = result