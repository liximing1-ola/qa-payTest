from common.Config import config
from common.method import reason
import unittest
from common import Consts, Assert, basicData, Request
from common.runFailed import Retry
from common.conMysql import conMysql
@Retry(max_n=3)
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

    def test_01_defendPayChangMoney(self):
        """
        用例描述：
        开通个人守护，收益分成在师父收益的基础上为 62:38
        脚本步骤：
        1.构造开通者和被守护者数据 （更新xs_user_money）
        2.开通价值5200元守护
        3.校验【status code】和返回值【body】状态
        4.检查打赏者余额
        5.检查被打赏者余额,预期：52000 * 0.62 = 32240
        6.检查消费记录
        """
        des = '开通个人守护场景'
        conMysql.updateMoneySql(config.payUid, 52000)
        conMysql.updateMoneySql(config.testUid)
        data = basicData.encodeData(payType='defend', money=52000, uid=config.testUid)
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason(des, res))
        Assert.assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 0)
        Assert.assert_equal(conMysql.selectUserMoneySql('sum_money', config.testUid), 32240)
        Consts.CASE_LIST[des] = Consts.result
