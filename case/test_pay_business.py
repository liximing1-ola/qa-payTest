from common.Config import config
from common.conMysql import conMysql
from common.Request import post_request_session
import unittest
from common.Assert import assert_code, assert_equal, assert_body, assert_len
from common.method import reason
from common.basicData import encodeData
from common.Consts import case_list, result
from common.runFailed import Retry


@Retry(max_n=2)
class TestPayCreate(unittest.TestCase):

    def test_01_businessPayGiftNormalUser(self, des='商业房礼物打赏普通用户到账62%(mcb)'):
        """
        用例描述：
        验证余额足够时，商业房打赏礼物给普通用户分成满足师徒收益(非一代宗师)的基础上为：62:38，且收入在个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间打赏礼物（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.62 =62 (money_cash_b)
        """
        conMysql.updateMoneySql(config.payUid, money=30, money_cash=30, money_cash_b=30, money_b=10)
        conMysql.updateMoneySql(config.rewardUid)
        conMysql.updateMoneySql(config.gsUid)
        data = encodeData(payType='package',
                          money=100,
                          giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.rewardUid), 62)
        print(conMysql.selectUserInfoSql('sum_money', config.gsUid))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
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
        conMysql.updateMoneySql(config.payUid, money=400, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(config.masterUid)
        data = encodeData(payType='package',
                          money=600,
                          uid=config.masterUid,
                          giftId=config.giftId['46'],
                          star=4)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 100)
        assert_len(conMysql.selectUserInfoSql('single_money', config.masterUid), 300 * 0.7)
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
        conMysql.updateMoneySql(config.payUid, money=30, money_cash=30, money_cash_b=30, money_b=10)
        conMysql.updateMoneySql(config.gsUid)
        data = encodeData(payType='package',
                          money=100,
                          uid=config.gsUid,
                          giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.gsUid,
                                                money_type='money_cash'), 100 * config.rate)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
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
        conMysql.updateMoneySql(config.payUid, money=10000)
        conMysql.updateMoneySql(config.rewardUid)
        data = encodeData(payType='package-more',
                          num=2,
                          star=8,
                          money=2100,
                          giftId=config.giftId['47'],
                          uids=('{}'.format(config.rewardUid), '{}'.format(config.gsUid)))
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 1600)
        assert_len(conMysql.selectUserInfoSql('single_money', config.rewardUid), 620)
        assert_len(conMysql.selectUserInfoSql('single_money', config.gsUid,
                                              money_type='money_cash'), 2000 * config.rate)
        case_list[des] = result

    @unittest.skip('点歌消费')
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


