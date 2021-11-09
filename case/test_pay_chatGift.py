from common.Config import config
from common.conMysql import conMysql
from common.Request import post_request_session
import unittest
from common.method import reason
from common import Assert, Consts, basicData
from common.runFailed import Retry
@Retry(max_n=2)
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

    def test_01_IMPayNoMoney(self):
        """
        用例描述：
        检查账户余额不足时，私聊一对一打赏
        脚本步骤：
        1.构造打赏者和被打赏者数据 （xs_user_money）
        2.私聊一对一打赏流程
        3.校验 statusCode和返回值数据
        4.检查预期返回msg，预期：支付失败，提示Toast
        5.检查被打赏者余额,预期：0
        """
        des = '私聊打赏余额不足的场景'
        conMysql.updateUserMoneyClearSql(config.payUid, config.testUid)
        conMysql.deleteUserAccountSql('broker_user', config.testUid)
        conMysql.deleteUserAccountSql('chatroom', config.testUid)
        data = basicData.encodeData(payType='chat-gift', uid=config.testUid, num=10, giftId=5)
        res = post_request_session(TestPayCreate.pay_url, data)
        Assert.assert_code(res['code'])
        Assert.assert_body(res['body'], 'success', 0, reason(des, res))
        Assert.assert_body(res['body'], 'msg', '余额不足，无法支付', reason(des, res))
        Assert.assert_equal(conMysql.selectUserMoneySql('sum_money', config.testUid), 0)
        Consts.CASE_LIST[des] = Consts.result