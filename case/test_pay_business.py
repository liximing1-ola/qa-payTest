from common.Config import config
from common.conMysql import conMysql as mysql
from common.Request import post_request_session
from common.method import checkUserVipExp
import unittest
from common.Assert import assert_code, assert_equal, assert_body, assert_len
from common.method import reason
from common.basicData import encodeData
from common.Consts import case_list, result
from common.runFailed import Retry


@Retry(max_n=3)
class TestPayCreate(unittest.TestCase):
    business_uid = 105002103  # 商业房auto_rid房主（一代宗师）
    ceo_uid = config.live_role['pack_ceo']  # 直播公会公会长

    def test_01_businessPayGiftNormalUser(self, des='商业房礼物打赏普通用户到账62%(mcb)'):
        """
        用例描述：
        验证余额足够时，商业房打赏礼物给普通用户分成满足师徒收益(非一代宗师)的基础上为：62:38，且收入在个人魅力值
        师父为公会成员，收到的师徒分成进个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏礼物（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.62 =62 (money_cash_b)
        5.检查被打赏者师徒账户，预期为：100 * 0.05 = 5（money_cash_b）
        6.检查打赏者VIP经验值变动
        """
        mysql.updateMoneySql(config.payUid, money=30, money_cash=30, money_cash_b=30, money_b=10)
        mysql.updateMoneySql(config.rewardUid)
        vip_level = int(mysql.selectUserInfoSql('pay_room_money', config.payUid))
        mysql.updateMoneySql(config.gsUid)
        data = encodeData(payType='package',
                          money=100,
                          giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(mysql.selectUserInfoSql('single_money', config.rewardUid), 62)
        assert_equal(mysql.selectUserInfoSql('single_money', config.gsUid), 5)
        assert_equal(mysql.selectUserInfoSql('sum_money', config.gsUid), 5)
        assert_equal(mysql.selectUserInfoSql('sum_money', config.payUid), 0)
        assert_equal(mysql.selectUserInfoSql('pay_room_money', config.payUid),
                     vip_level + checkUserVipExp())
        case_list[des] = result

    def test_02_businessPayBoxNormalUser(self, des='商业房打赏箱子一代用户到账70%(mcb)'):
        """
        用例描述：
        验证余额足够时，商业房打赏礼盒分成满足师徒收益(一代宗师)的基础上为：70:30，且收入在个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏礼盒（打赏铜箱子）
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：700 - 600 = 100
        5.检查收箱用户账户余额，预期值为不小于：210
        """
        mysql.updateMoneySql(config.payUid, money=400, money_cash=100, money_cash_b=100, money_b=100)
        mysql.updateMoneySql(config.masterUid)
        vip_level = int(mysql.selectUserInfoSql('pay_room_money', config.payUid))
        data = encodeData(payType='package',
                          money=600,
                          uid=config.masterUid,
                          giftId=config.giftId['46'],
                          star=4)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(mysql.selectUserInfoSql('sum_money', config.payUid), 100)
        income = mysql.selectUserInfoSql('pay_change', uid=config.masterUid, money_type='_in_c_b')
        assert_equal(mysql.selectUserInfoSql('single_money', config.masterUid), income)
        assert_equal(mysql.selectUserInfoSql('pay_room_money', config.payUid),
                     vip_level + checkUserVipExp(pay_off=600))
        case_list[des] = result

    def test_03_businessPayGiftToGs(self, des='商业房礼物打赏GS到账62%(mc)'):
        """
        用例描述：
        验证余额足够时，商业房打赏礼物给GS分成为：62:38，且收入在公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏礼物（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.62 =62 (money_cash)
        """
        mysql.updateMoneySql(config.payUid, money=30, money_cash=30, money_cash_b=30, money_b=10)
        mysql.updateMoneySql(config.gsUid)
        data = encodeData(payType='package',
                          money=100,
                          uid=config.gsUid,
                          giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(mysql.selectUserInfoSql('single_money', config.gsUid,
                                                money_type='money_cash'), 100 * config.rate)
        assert_equal(mysql.selectUserInfoSql('sum_money', config.gsUid), 100 * config.rate)
        assert_equal(mysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list[des] = result

    def test_04_businessPayBoxToGs(self, des='商业房打赏箱子GS到账62%（mc）'):
        """
        用例描述：
        验证商业房内送箱子给多个人时逻辑正常且GS分成为：62:38，且收入在公会魅力值
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
        2.giveBox
        3.校验接口状态和返回值数据
        4.检查账户余额，预期值为：10000 - 2100*2*2 = 1600
        5.检查收箱用户账户余额，预期值为不小于：2000 * 0.62 = 1240（money_cash）
        """
        mysql.updateMoneySql(config.payUid, money=10000)
        mysql.updateMoneySql(config.rewardUid)
        data = encodeData(payType='package-more',
                          num=2,
                          star=2,
                          money=2100,
                          giftId=config.giftId['47'],
                          uids=('{}'.format(config.rewardUid), '{}'.format(config.gsUid)))
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(mysql.selectUserInfoSql('sum_money', config.payUid), 1600)
        assert_len(mysql.selectUserInfoSql('single_money', config.rewardUid), 620)
        assert_len(mysql.selectUserInfoSql('single_money', config.gsUid,
                                              money_type='money_cash'), 2000 * config.rate)
        assert_len(mysql.selectUserInfoSql('sum_money', config.gsUid), 2000 * config.rate)
        case_list[des] = result

    def test_05_musicOrderPayGiftToGs(self, des='点歌消费GS到账62%(mc)'):
        """
        用例描述：
        验证余额足够时，business-music内点歌给GS分成为：62:38，且收入在公会魅力值
        限制：房型限定为business-music
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间选中GS点歌（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：3000 * 0.62 = 1860 (money_cash)
        """
        pass

    def test_06_businessPayGiftToBusinessCreator(self, des='礼物打赏商业房房主到账70%(mc)'):
        """
        用例描述：
        验证余额足够时，打赏礼物给商业房房主分成为：70:30，且收入在公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏礼物（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.7 =70 (money_cash)
        """
        mysql.updateMoneySql(config.payUid, money=30, money_cash=30, money_cash_b=30, money_b=10)
        mysql.updateMoneySql(self.business_uid)
        data = encodeData(payType='package',
                          money=100,
                          uid=self.business_uid,
                          giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(mysql.selectUserInfoSql('single_money', self.business_uid,
                                                money_type='money_cash'), 70)
        assert_equal(mysql.selectUserInfoSql('sum_money', self.business_uid), 70)
        assert_equal(mysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list[des] = result

    def test_07_businessPayGiftToBrokerCreator(self, des='礼物打赏公会会长到账70%(mc)'):
        """
        用例描述：
        验证余额足够时，打赏礼物给公会会长分成为：70:30，且收入在公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏礼物（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.7 =70 (money_cash)
        """
        mysql.updateMoneySql(config.payUid, money=30, money_cash=30, money_cash_b=30, money_b=10)
        mysql.updateMoneySql(self.ceo_uid)
        data = encodeData(payType='package',
                          money=100,
                          uid=self.ceo_uid,
                          giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(mysql.selectUserInfoSql('single_money', self.ceo_uid,
                                                money_type='money_cash'), 70)
        assert_equal(mysql.selectUserInfoSql('sum_money', self.ceo_uid), 70)
        assert_equal(mysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list[des] = result
