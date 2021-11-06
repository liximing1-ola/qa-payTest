from common.Config import config
from common.conMysql import conMysql
from common.method import reason
import unittest, time
from common import Consts, Request, Assert, basicData
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

    @unittest.skip('NSQ异常')
    def test_01_PayChangeTriggerPunish(self):
        """
        用例描述：
        验证收到打赏时，触发罚款流程，扣款账户：金豆 -》个人魅力值 -》现金余额 -》公会魅力值 -》伴伴币
        脚本步骤：
        1.构造打赏者和被罚款者数据 （更新xs_user_money，xs_user_money_extend）
        2.被罚款者欠款：100分
        2.房间内一对一打赏（打赏100分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额，预期为：62
        5.检查消费记录表消费money（xs_pay_change_new）
        6.检查消费记录表消费方式op
        """
        des = '打赏时触发罚款流程(NoRun)'
        conMysql.updateMoneySql(config.payUid, 100)
        conMysql.insertBeanSql(config.testUid, 20)
        conMysql.updateMoneySql(config.testUid, 20, money_debts=100)
        data = basicData.encodeData(payType='package', money=100, rid=config.super_live_role['auto_rid'],
                                    uid=config.testUid, giftId=5)
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason(des, res['body']))
        time.sleep(1)  # 延迟处理NSQ消息
        Assert.assert_equal(conMysql.selectUserMoneySql('bean', config.testUid), 0)
        Assert.assert_equal(conMysql.selectUserMoneySql('single_money', config.testUid, 'money'), 2)
        Assert.assert_equal(conMysql.selectUserMoneySql('single_money', config.testUid, 'money_cash_b'), 0)
        Assert.assert_equal(conMysql.selectUserMoneySql('single_money', config.testUid, 'money_debts'), 0)
        Assert.assert_equal(conMysql.selectUserMoneySql('pay_change', config.testUid, op='money'), 100)
        Assert.assert_equal(conMysql.selectUserMoneySql('pay_change', config.testUid, op='op'), 'punish')
        Consts.CASE_LIST[des] = Consts.result