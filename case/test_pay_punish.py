from common.Config import config
from common.conMysql import conMysql
from common.method import reason
import unittest
from time import sleep
from common.Assert import assert_body, assert_code, assert_equal
from common.Request import post_request_session
from common.basicData import encodeData
from common.Consts import case_list_c, result
from common.runFailed import Retry
class TestPayCreate(unittest.TestCase):

    @Retry
    @unittest.skip
    def test_01_PayChangeTriggerPunish(self, des='打赏时触发罚款流程'):
        """
        用例描述：
        验证收到打赏时，触发罚款流程，扣款账户：金豆 -》个人魅力值 -》现金余额 -》公会魅力值 -》伴伴币
        脚本步骤：
        1.构造打赏者和被罚款者数据
        2.被罚款者欠款：100分
        2.房间内一对一打赏（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.62 = 62
        5.检查消费记录表消费money
        6.检查消费记录表消费方式op
        """
        conMysql.updateMoneySql(config.payUid, money=100)
        conMysql.insertBeanSql(config.rewardUid, money_coupon=20)
        conMysql.updateMoneySql(config.rewardUid, money=20, money_debts=100)
        data = encodeData(payType='package',
                          money=100,
                          rid=config.star_role['auto_rid'],
                          uid=config.rewardUid,
                          giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        sleep(2)  # 延迟处理NSQ消息
        assert_equal(conMysql.selectUserInfoSql('bean', config.rewardUid), 0)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.rewardUid, 'money'), 2)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.rewardUid, 'money_cash_b'), 0)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.rewardUid, 'money_debts'), 0)
        assert_equal(conMysql.selectUserInfoSql('pay_change', config.rewardUid, op='money'), 100)
        assert_equal(conMysql.selectUserInfoSql('pay_change', config.rewardUid, op='op'), 'punish')
        case_list_c[des] = result