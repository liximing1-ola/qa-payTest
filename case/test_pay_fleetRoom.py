from common.Config import config
from common.conMysql import conMysql as mysql
from common.method import reason
import unittest
from common.Request import post_request_session
from common.Assert import assert_body, assert_code, assert_equal, assert_len
from common.basicData import encodeData
from common.runFailed import Retry
from common.Consts import case_list_b, result


@Retry(max_n=3)
class TestPayCreate(unittest.TestCase):

    other_fleet_rid = mysql.selectUserInfoSql('fleet')  # 非本家族房
    fleet_rid = config.bb_user['fleetRid']  # 本家族房
    pack_cal_uid = config.bb_user['pack_cal_uid']  # 直播公会gs

    def test_01_sameFleetRoomLiveGsRate(self, des='家族房打赏直播公会gs场景'):
        """
        用例描述：
        tdr：同家族房内直播公会成员礼物打赏到账70%个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.7 = 700(money_cash_b)
        5.检查打赏者余额，预期为：1000 - 1000 = 0
        """
        mysql.updateMoneySql(config.payUid, money=1000)
        mysql.updateMoneySql(self.pack_cal_uid)
        data = encodeData(payType='package',
                          rid=self.fleet_rid,
                          uid=self.pack_cal_uid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(mysql.selectUserInfoSql('single_money', self.pack_cal_uid, money_type='money_cash_b'), 300)
        assert_equal(mysql.selectUserInfoSql('sum_money', self.pack_cal_uid), 800)
        assert_equal(mysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    def test_02_otherFleetRoomLiveGsRate(self, des='非本家族房打赏直播公会GS场景'):
        """
        用例描述：
        tdr：other家族房内直播公会成员礼物打赏到账70%个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.7 = 700(money_cash_b)
        5.检查打赏者余额，预期为：1000 - 1000 = 0
        """
        mysql.updateMoneySql(config.payUid, money=1000)
        mysql.updateMoneySql(self.pack_cal_uid)
        data = encodeData(payType='package',
                          rid=self.other_fleet_rid,
                          uid=self.pack_cal_uid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(mysql.selectUserInfoSql('single_money', self.pack_cal_uid, money_type='money_cash'), 700)
        assert_equal(mysql.selectUserInfoSql('sum_money', self.pack_cal_uid), 700)
        assert_equal(mysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    def test_03_sameFleetRoomNormalGsRate(self, des='家族房打赏普通公会gs场景'):
        """
        用例描述：
        tdr：家族房内普通公会成员礼物打赏到账42%公会魅力值+30%个人魅力值
         脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.42 = 420(money_cash) + 1000 * 0.3 = 300（money_cash_b）
        5.检查打赏者余额，预期为：1000 - 1000 = 0
        """
        mysql.updateMoneySql(config.payUid, money=1000)
        mysql.updateMoneySql(config.gsUid)
        data = encodeData(payType='package',
                          rid=self.fleet_rid,
                          uid=config.gsUid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(mysql.selectUserInfoSql('single_money', config.gsUid,
                                                money_type='money_cash'), 420)
        assert_equal(mysql.selectUserInfoSql('single_money', config.gsUid), 300)
        assert_equal(mysql.selectUserInfoSql('sum_money', config.gsUid), 720)
        assert_equal(mysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    def test_04_otherFleetRoomNormalGsRate(self, des='非本家族房打赏公会GS场景'):
        """
        用例描述：
        tdr：other家族房内GS收到箱子打赏拿62%公会魅力值
       脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏（打赏铜箱子）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为不小于：300 * 0.62 = 186(money_cash)
        5.检查打赏者余额，预期为：600 - 600 = 0
        """
        mysql.updateMoneySql(config.payUid, money=600)
        mysql.updateMoneySql(config.gsUid)
        data = encodeData(payType='package',
                          money=600,
                          rid=self.other_fleet_rid,
                          giftId=config.giftId['46'],
                          uid=config.gsUid,
                          star=1)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(mysql.selectUserInfoSql('sum_money', config.payUid), 0)
        assert_len(mysql.selectUserInfoSql('single_money', config.gsUid,
                                              money_type='money_cash'), 300 * config.rate)
        case_list_b[des] = result

    def test_05_sameFleetRoomPayNormalUser(self, des='家族房打赏一代用户场景'):
        """
        用例描述：
        tdr：家族房内一代宗师普通用户箱子打赏到账80%个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏（打赏铜箱子）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为不小于：300 * 0.8 = 240(money_cash_b)
        5.检查打赏者余额，预期为：600 - 600 = 0
        """
        mysql.updateMoneySql(config.payUid, money=600)
        mysql.updateMoneySql(config.masterUid)
        data = encodeData(payType='package',
                          money=600,
                          rid=self.fleet_rid,
                          giftId=config.giftId['46'],
                          uid=config.masterUid,
                          star=1)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(mysql.selectUserInfoSql('sum_money', config.payUid), 0)
        assert_len(mysql.selectUserInfoSql('single_money', config.masterUid), 300 * 0.8)
        case_list_b[des] = result

    def test_06_otherFleetRoomNormalGsRate(self, des='非本家族房打赏用户场景'):
        """
       用例描述：
        tdr：other家族房内普通用户礼物打赏到账62%个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.62 = 620(money_cash_b)
        5.检查打赏者余额，预期为：1000 - 1000 = 0
        """
        mysql.updateMoneySql(config.payUid, money=1000)
        mysql.updateMoneySql(config.rewardUid)
        data = encodeData(payType='package',
                          rid=self.other_fleet_rid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(mysql.selectUserInfoSql('single_money', config.rewardUid), 620)
        assert_equal(mysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result
