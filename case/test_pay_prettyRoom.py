from common.Config import config
from common.method import reason
from common.conMysql import conMysql
import unittest
from common.Request import post_request_session
from common.Assert import assert_body, assert_code, assert_equal, assert_len
from common.basicData import encodeData
from common.Consts import case_list_b, result
from common.runFailed import Retry


@Retry
class TestPayCreate(unittest.TestCase):

    prettyRid = config.bb_user['prettyRid']  # config.xsst_room_pretty

    def test_01_prettyRoomPayGiftToBrokerUser(self, des='靓号房打赏礼物GS分62%进公会魅力值'):
        """
        用例描述：
        验证靓号房打赏礼物给公会成员分成为62%且收入进公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.靓号房打赏礼物（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.62 = 62 (money_cash)
        """
        conMysql.updateMoneySql(config.payUid, money_cash_b=250)
        conMysql.updateMoneySql(config.gsUid)
        data = encodeData(payType='package',
                          money=100,
                          rid=self.prettyRid,
                          uid=config.gsUid,
                          giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.gsUid, money_type='money_cash'),
                     100 * config.rate)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 150)
        case_list_b[des] = result

    def test_02_prettyRoomPayBox(self, des='靓号房打赏礼盒GS分62%进公会魅力值'):
        """
        用例描述：
        验证靓号房打赏礼物给公会成员分成为62%且收入进公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.靓号房打赏礼盒（打赏铜箱子600分）
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：700 - 600 = 100
        5.检查收箱用户账户余额，预期值为：不小于186,(300*0.62=186)
        """
        conMysql.updateMoneySql(config.payUid, money=400, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(config.gsUid)
        data = encodeData(payType='package',
                          money=600,
                          uid=config.gsUid,
                          rid=self.prettyRid,
                          giftId=config.giftId['46'],
                          star=1)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 100)
        assert_len(conMysql.selectUserInfoSql('single_money', config.gsUid, money_type='money_cash'),
                   300 * config.rate)
        case_list_b[des] = result

    def test_03_prettyRoomPayGiftToNormalUser(self, des='靓号房打赏普通用户进个人魅力值'):
        """
        用例描述：
        验证靓号房打赏礼物给普通用户（非一代宗师）分成为62%且收入进个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.靓号房打赏礼物
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：100 - 100 = 0
        5.检查被打赏者账户余额，预期值为：100 * 0.62 = 62
        """
        conMysql.updateMoneySql(config.payUid, money_cash=100)
        conMysql.updateMoneySql(config.rewardUid)
        data = encodeData(payType='package',
                          money=100,
                          rid=self.prettyRid,
                          uid=config.rewardUid,
                          giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.rewardUid), 62)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result
