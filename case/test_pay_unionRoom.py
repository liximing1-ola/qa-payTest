from common.Config import config
from common.conMysql import conMysql
from common.method import reason
import unittest
import pytest
from common.Request import post_request_session
from common.Assert import assert_body, assert_code, assert_equal, assert_len
from common.basicData import encodeData
from common.runFailed import Retry
from common.Consts import case_list_b, result


@Retry
class TestPayCreate(unittest.TestCase):

    singer_rid = conMysql.selectUserInfoSql('union')  # 联盟房/歌友房
    pack_cal_uid = config.bb_user.copy()['pack_cal_uid']  # 直播公会gs

    @pytest.mark.run(order=1)
    def test_01_singerRoomLiveBrokerRate_60(self, des='歌友房直播工会收60%公会魅力值'):
        """
        用例描述：
        tdr：歌友房内，直播公会成员礼物打赏到账60%公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.歌友房打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.6 = 600(money_cash)
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateMoneySql(self.pack_cal_uid)
        data = encodeData(payType='package',
                          rid=self.singer_rid,
                          uid=self.pack_cal_uid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', self.pack_cal_uid, money_type='money_cash'), 600)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    @unittest.skip
    @pytest.mark.run(order=2)
    def test_02_singerRoomNormalBrokerRate_62(self, des='歌友房普通工会收62%公会魅力值'):
        """
        用例描述：
        tdr：歌友房内，普通公会成员礼物打赏到账62%公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.歌友房打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.62 = 620(money_cash)
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateMoneySql(config.gsUid)
        data = encodeData(payType='package',
                          rid=self.singer_rid,
                          uid=config.gsUid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.gsUid,
                                                money_type='money_cash'), 1000 * config.rate)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    @unittest.skip
    @pytest.mark.run(order=3)
    def test_03_singerPayBoxNormalBrokerRate_62(self, des='歌友房打赏箱子GS收62%（mc）'):
        """
        用例描述：
        tdr：歌友房内，普通公会成员箱子打赏到账62%公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.歌友房打赏（打赏铜箱子）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为不小于：300 * 0.62 = 620(money_cash)
        5.检查打赏者余额，预期为：600 - 600 = 0
        """
        conMysql.updateMoneySql(config.payUid, money=600)
        conMysql.updateMoneySql(config.gsUid)
        data = encodeData(payType='package',
                          money=600,
                          rid=self.singer_rid,
                          giftId=config.giftId['46'],
                          uid=config.gsUid,
                          star=4)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        assert_len(conMysql.selectUserInfoSql('single_money', config.gsUid,
                                              money_type='money_cash'), 300 * config.rate)
        case_list_b[des] = result

    @unittest.skip
    def test_04_singerRoomPayNormalUser(self, des='歌友房普通用户礼物打赏收个人魅力值'):
        """
        用例描述：
        tdr：歌友房内，非公会成员收到礼物打赏时收62%个人魅力值（师徒）
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.6 = 620(个人魅力值)
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateMoneySql(config.rewardUid)
        data = encodeData(payType='package',
                          rid=self.singer_rid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.rewardUid), 620)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result
