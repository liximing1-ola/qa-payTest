from common.Config import config
from common.method import reason
import unittest
import pytest
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_equal
from common.basicData import encodeData
from common.Consts import case_list, result
from common.runFailed import Retry
from common.conMysql import conMysql
@Retry(max_n=1)
class TestPayCreate(unittest.TestCase):

    dict_config = conMysql.selectUserInfoSql('relation_config', uid=2)  # uid=id
    defend_id = conMysql.selectUserInfoSql('relation_id', config.rewardUid)
    # {'id': 2, 'name': '小宝贝', 'money_value': 52000, 'break_money': 28800, 'upgrade_money': 99900}

    @pytest.mark.run(order=1)
    def test_01_defendPayChangMoney(self, des='开通个人守护场景'):
        """
        用例描述：
        开通个人守护，收益分成在师父收益(非一代宗师)的基础上为 62:38
        脚本步骤：
        1.构造开通者和被守护者数据
        2.开通价值52000钻小宝贝守护（xs_relation_config id=2）
        3.校验接口状态和返回值数据
        4.检查打赏者余额
        5.检查被打赏者余额,预期：52000 * 0.62 = 32240
        """
        conMysql.updateMoneySql(config.payUid, money=52000)
        conMysql.updateMoneySql(config.rewardUid)
        data = encodeData(payType='defend',
                          money=self.dict_config['money_value'],
                          uid=config.rewardUid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.rewardUid), 32240)
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
         4.检查打赏者余额，预期：100000 - 99900 = 100
         5.检查被打赏者余额,预期： 99900 * 0.62 = 61938
         """
        conMysql.updateMoneySql(config.payUid, money=100000)
        conMysql.updateMoneySql(config.rewardUid)
        data = encodeData(payType='defend-upgrade',
                          money=self.dict_config['upgrade_money'],
                          defend_id=self.defend_id)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.rewardUid), 61938)
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
        data = encodeData(payType='defend-break',
                          money=self.dict_config['break_money'],
                          defend_id=self.defend_id)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 11200)
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
        data = encodeData(payType='package-knightDefend',
                          money=99900,
                          uid=config.pack_cal_uid,
                          rid=config.live_role['live_rid'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pack_cal_uid), 59940)
        case_list[des] = result