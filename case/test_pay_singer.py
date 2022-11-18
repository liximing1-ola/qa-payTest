from common.Config import config
from common.conMysql import conMysql
from common.method import reason
import unittest
import pytest
from common.Request import post_request_session
from common.Assert import assert_body, assert_code, assert_equal
from common.basicData import encodeData
from common.runFailed import Retry
from common.Consts import case_list_b, result


@Retry
class TestPayCreate(unittest.TestCase):
    singer_rid = conMysql.selectUserInfoSql('union')

    @pytest.mark.run(order=1)
    def test_01_singerRoomLiveBroker_60(self, des='歌友房直播工会收60%公会魅力值'):
        """
        用例描述：
        tdr：歌友房内，直播公会成员收60%公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.6 = 600(公会魅力值)
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateMoneySql(config.pack_cal_uid)
        data = encodeData(payType='package',
                          rid=self.singer_rid,
                          uid=config.pack_cal_uid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pack_cal_uid, money_type='money_cash'), 600)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    @pytest.mark.run(order=2)
    def test_02_singerRoomNoBrokerUser_62(self, des='歌友房非公会收62%个人魅力值'):
        """
        用例描述：
        tdr：歌友房内，非公会成员收62%个人魅力值（师徒）
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.6 = 620(个人魅力值)
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateMoneySql(config.rewardUid)
        data = encodeData(payType='package', rid=self.singer_rid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.rewardUid, money_type='money_cash_b'), 620)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result
