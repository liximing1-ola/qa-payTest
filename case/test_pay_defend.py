from common.Config import config
from common.method import reason
import unittest, pytest
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_equal
from common import basicData
from common.Consts import case_list, result
from common.runFailed import Retry
from common.conMysql import conMysql
@Retry(max_n=1)
class TestPayCreate(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        conMysql.selectUserMoneySql('relation_config', uid=2)  # uid=id

    @pytest.mark.run(order=1)
    def test_01_defendPayChangMoney(self, des='开通个人守护场景'):
        """
        用例描述：
        开通个人守护，收益分成在师父收益(非一代宗师)的基础上为 62:38
        脚本步骤：
        1.构造开通者和被守护者数据
        2.开通价值52000钻小宝贝守护（xs_relation_config id=2）
        3.校验接口状态和返回值数据
        4.检查打赏者余额`
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

    @pytest.mark.run(order=2)
    def test_02_defendUpgradePayChangeMoney(self, des='守护进阶场景'):
        """
         用例描述：
         个人守护关系开通后，购买进阶版特权，收益分成在师父收益（非一代宗师）的基础上为：62:38
         脚本步骤：
         1.接test_01
         2.购买进阶版（99900钻），黄金小宝贝对应进阶价格
         3.校验接口状态和返回值数据
         4.检查打赏者余额，预期：100000 - 99900 = 100钻
         5.检查被打赏者余额,预期： 99900 * 0.62 = 61938
         """
        conMysql.updateMoneySql(config.payUid, money=100000)
        conMysql.updateMoneySql(config.rewardUid)
        defend_id = conMysql.selectUserMoneySql('relation_id', config.rewardUid)
        data = basicData.encodeData(payType='defend-upgrade', money=99900, defend_id=defend_id)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 100)
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.rewardUid), 61938)
        case_list[des] = result

    @pytest.mark.run(order=3)
    def test_03_defendBreakPayChangeMoney(self, des='守护解除场景'):
        """
         用例描述：
         个人守护关系开通后，购买进阶版特权后，强行解除关系，收益归官方
         脚本步骤：
         1.接test_01，test_02
         2.强制解除关系
         3.校验接口状态和返回值数据
         4.检查打赏者余额，预期：40000 - 36000 = 4000
         """
        conMysql.updateMoneySql(config.payUid, money=40000)
        defend_id = conMysql.selectUserMoneySql('relation_id', config.rewardUid)
        data = basicData.encodeData(payType='defend-break', money=36000, defend_id=defend_id)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 4000)
        case_list[des] = result

    def test_04_knightDefendPayChangeMoney(self, des='开通房间守护团场景'):
        """
         用例描述：
         开通直播间守护团，收益分成在师父收益（一代宗师）的基础上为 60:25:15
         脚本步骤：
         1.构造开通者和被守护者数据
         2.开通真爱守护
         3.校验接口状态和返回值数据
         4.检查打赏者余额，预期：100000 - 99900 = 100
         5.检查被打赏者余额,预期：99900 * 0.6 = 59940
         """
        conMysql.updateMoneySql(config.payUid, money=100000)
        conMysql.updateMoneySql(config.pack_cal_uid)
        data = basicData.encodeData(payType='package-knightDefend', money=99900, uid=config.pack_cal_uid,
                                    rid=config.live_role['live_rid'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 100)
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.pack_cal_uid), 59940)
        case_list[des] = result