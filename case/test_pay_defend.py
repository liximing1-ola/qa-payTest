from common.Config import config
from common.method import reason
import unittest
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_equal
from common import basicData
from common.Consts import case_list, result
from common.runFailed import Retry
from common.conMysql import conMysql
@Retry(max_n=3)
class TestPayCreate(unittest.TestCase):

    def test_01_defendPayChangMoney(self, des='开通个人守护场景'):
        """
        用例描述：
        开通个人守护，收益分成在师父收益的基础上为 62:38
        脚本步骤：
        1.构造开通者和被守护者数据
        2.开通价值52000钻守护
        3.校验接口状态和返回值数据
        4.检查打赏者余额
        5.检查被打赏者余额,预期：52000 * 0.62 = 32240
        """
        conMysql.updateMoneySql(config.payUid, money=52000)
        conMysql.updateMoneySql(config.rewardUid)
        data = basicData.encodeData(payType='defend', money=52000, uid=config.rewardUid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 0)
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.rewardUid), 32240)
        case_list[des] = result

    def test_02_knightDefendPayChangeMoney(self, des='开通房间守护团场景'):
        """
         用例描述：
         开通直播间守护团，收益分成在师父收益（一代宗师）的基础上为 70:30
         脚本步骤：
         1.构造开通者和被守护者数据
         2.开通真爱守护
         3.校验接口状态和返回值数据
         4.检查打赏者余额，预期：100000 - 99900 = 100
         5.检查被打赏者余额,预期：99900 * 0.7 = 69930
         """
        conMysql.updateMoneySql(config.payUid, money=100000)
        conMysql.updateMoneySql(config.pack_cal_uid)
        data = basicData.encodeData(payType='package-knightDefend', money=99900, uids=config.pack_cal_uid,
                                    rid=config.live_role['live_rid'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 100)
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.pack_cal_uid), 69930)
        case_list[des] = result

    @unittest.skip('未完成')
    def test_03_DefendPayChangeMoney(self, des='开通电台守护场景'):
        """
         用例描述：
         开通直播间守护团，收益分成在师父收益（一代宗师）的基础上为 70:30
         脚本步骤：
         1.构造开通者和被守护者数据
         2.开通真爱守护
         3.校验接口状态和返回值数据
         4.检查打赏者余额，预期：30000 - 28800 = 1200
         5.检查被打赏者余额,预期：28800 * 0.7 = 20160
         """
        conMysql.updateMoneySql(config.payUid, money=30000)
        conMysql.updateMoneySql(config.pack_cal_uid)
        data = basicData.encodeData(payType='package-knightDefend', money=28800, uid=config.pack_cal_uid,
                                    rid=config.live_role['live_rid'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 1200)
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.pack_cal_uid), 20160)
        case_list[des] = result