import unittest
from common.basicData import encodeData
from common.Assert import assert_body, assert_code, assert_equal
from common.Config import config
from common.Consts import case_list_b, result
from common.Request import post_request_session
from common.conMysql import conMysql
from common.method import reason
from common.runFailed import Retry
from common.Session import Session
@Retry
class TestPayCreate(unittest.TestCase):
    rate_role = {
        "bid": 100011021,  # 公会的bid
        'rewardUid': 131554725,  # 打赏者
        'rewardedUid': 131564968,  # 被打赏者
    }

    def test_01_roomPayCustomRate_60(self, des='商业房打赏自定义分成:60'):
        """
        用例描述：
        tdr:后台自定义分成比例为60%
        脚本步骤：
        1.构造打赏者，被打赏者数据
        2.房间内打赏（打赏100分）
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：100 - 100 = 0
        5.检查被打赏者余额，预期为：100 * 0.6 = 60
        """
        Session.getSession('rush')
        testUid = self.rate_role["rewardedUid"]  # 被打赏者
        payUid = self.rate_role["rewardUid"]  # 打赏
        conMysql.updateUserMoneyClearSql(testUid, payUid)
        conMysql.updateMoneySql(payUid, money=100)  # 打赏者
        conMysql.checkUserBroker(testUid, bid=self.rate_role["bid"])  # 被打赏者加入工会
        conMysql.check_uid_white(testUid)  # 被打赏者加入白名单，分成为60%
        data = encodeData(money=100, rid=200064778, uid=testUid, giftId=config.giftId['5'])
        res = post_request_session(config.rush_pay_url, data, tokenName='rush')
        print(res)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', payUid), 0)  # 打赏者金额剩余
        assert_equal(conMysql.selectUserInfoSql('sum_money', testUid), 60)  # 被打赏者金额总数
        case_list_b[des] = result

    @unittest.skip
    def test_02_chatPayCustomRate_60(self, des='私聊打赏自定义分成:60'):
        """
        用例描述：
        tdr:后台自定义分成比例为60%
        脚本步骤：
        1.构造打赏者，被打赏者
        2.私聊打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：1000 - 1000 = 0
        5.检查被打赏者总余额，预期为：1000 * 0.6 = 600
        """
        testUid = self.rate_role["rewardedUid"]  # 被打赏者
        payUid = self.rate_role["rewardUid"]
        conMysql.updateUserMoneyClearSql(testUid, payUid)
        conMysql.updateMoneySql(payUid, money=1000)  # 打赏者
        conMysql.checkUserBroker(testUid, bid=self.rate_role["bid"])  # 被打赏者加入工会
        conMysql.check_uid_white(testUid)  # 被打赏者加入白名单，分成为60%
        data = encodeData(payType='chat-gift', uid=testUid, giftId=20)
        res = post_request_session(config.rush_pay_url, data, tokenName='rush')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', payUid), 0)  # 打赏者金额剩余
        assert_equal(conMysql.selectUserInfoSql('sum_money', testUid), 600)  # 被打赏者金额总数
        case_list_b[des] = result

    @unittest.skip
    def test_03_defendPayCustomRate_60(self, des='个人守护打赏自定义分成:60'):
        """
        用例描述：
        tdr:后台自定义分成比例为60%
        脚本步骤：
        1.构造打赏者，被打赏者
        2.开通守护
        3.校验接口状态和返回值数据
        4.检查打赏者余额，预期为：52000 - 52000 = 0
        5.检查被打赏者总余额，预期为：52000 * 0.6 = 31200
        """
        testUid = self.rate_role["rewardedUid"]  # 被打赏者
        payUid = self.rate_role["rewardUid"]
        conMysql.updateUserMoneyClearSql(testUid, payUid)
        conMysql.updateMoneySql(payUid, money=52000)  # 打赏者
        conMysql.checkUserBroker(testUid, bid=self.rate_role["bid"])  # 被打赏者加入工会
        conMysql.check_uid_white(testUid) # 被打赏者加入白名单，分成为60%
        data = encodeData(payType='defend', uid=testUid, money=52000)
        res = post_request_session(config.rush_pay_url, data, tokenName='rush')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('sum_money', testUid), 31200)
        case_list_b[des] = result