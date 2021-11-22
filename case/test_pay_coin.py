from common.Config import config
from common.method import reason
from common.conMysql import conMysql
from common.Request import post_request_session
import unittest
from common.Assert import assert_body, assert_code, assert_equal
from common import Consts, basicData
from common.runFailed import Retry
@Retry(max_n=3, func_prefix='test_02_roomChangePayCoin')
class TestPayCreate(unittest.TestCase):
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'  # 内网支付接口

    def test_01_moneyChangeExchangeCoin(self):
        """
        用例描述：
        验证money兑换金币流程
        脚本步骤：
        1.构造用户数据
        2.金币兑换流程
        3.校验接口状态和返回值数据
        4.检查账户钻石余额：money：1000 - 600 = 400
        5.检查账户金币余额：gold_coin：600
        """
        des = '余额兑换金币场景'
        conMysql.updateMoneySql(config.payUid, money=1000)
        data = basicData.encodeData(payType='exchange_gold')
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 400)
        assert_equal(conMysql.selectUserMoneySql('single_money', config.payUid, money_type='gold_coin'), 600)
        Consts.CASE_LIST[des] = Consts.result

    def test_02_roomChangePayCoin(self):
        """
        用例描述：
        验证房间内打赏金币流程
        脚本步骤：
        1.构造用户数据
        2.房间打赏金币礼物流程
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额（gold_coin） 100 - 20*3 = 40
        5.检查被打赏者账户余额（gold_coin）  20 * 0.6 = 12
        """
        des = '房间打赏金币礼物的场景'
        conMysql.updateMoneySql(config.payUid, gold_coin=100)
        conMysql.updateUserMoneyClearSql(config.testUid, config.testUid_2)
        data = basicData.encodeData(payType='package-more', rid=config.live_role['auto_rid'], money=20, giftId=62, giftType='coin')
        res = post_request_session(TestPayCreate.pay_url, data)
        print(res)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('single_money', config.payUid, money_type='gold_coin'), 60)
        assert_equal(conMysql.selectUserMoneySql('single_money', config.testUid_2, money_type='gold_coin'), 12)
        Consts.CASE_LIST[des] = Consts.result