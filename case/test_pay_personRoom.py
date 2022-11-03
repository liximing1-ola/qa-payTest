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

    # select rid from xs_chatroom where uid=103273407 and property='vip'  个人房，＞5级不回收
    # select * from config.xsst_room_pretty;
    vipRoomRid = config.bb_user.copy()['vipRoomRid']
    prettyRid = config.bb_user.copy()['prettyRid']

    def test_01_personRoomPayGift(self, des='个人房打赏钻石礼物场景'):
        """
        用例描述：
        验证余额足够时，个人房打赏礼物分成满足师徒收益(非一代宗师)的基础上为：62:38，且收入在个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.个人房房间打赏礼物（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.62 =62 (money_cash_b)
        """
        conMysql.updateMoneySql(config.payUid, money=30, money_cash=30, money_cash_b=30, money_b=10)
        conMysql.updateMoneySql(config.rewardUid)
        data = encodeData(payType='package',
                          money=100,
                          rid=self.vipRoomRid,
                          uid=config.rewardUid,
                          giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.rewardUid), 62)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    def test_02_personRoomPayBox(self, des='个人房打赏礼盒场景'):
        """
        用例描述：
        验证余额足够时，个人房打赏礼盒分成满足师徒收益(非一代宗师)的基础上为：62:38，且收入在个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.个人房房间打赏礼盒（打赏100分）
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：700 - 600 = 100
        5.检查收箱用户账户余额，预期值为：大于186,(300*0.62=186)
        """
        conMysql.updateMoneySql(config.payUid, money=400, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(config.rewardUid)
        data = encodeData(payType='package',
                          money=600,
                          rid=self.vipRoomRid,
                          uid=config.rewardUid,
                          giftId=config.giftId['46'],
                          star=4)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 100)
        assert_len(conMysql.selectUserInfoSql('single_money', config.rewardUid), 186)
        case_list_b[des] = result

    def test_03_personRoomPayGiftToBrokerUser(self, des='个人房打赏钻石礼物给工会成员'):
        """
        用例描述：
        验证余额足够时，个人房打赏礼物给工会成员分成为：70:30，且收入在个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.个人房房间打赏礼物（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.7 =70 (money_cash_b)
        """
        conMysql.updateMoneySql(config.payUid, money_cash_b=100)
        conMysql.updateMoneySql(config.pack_cal_uid)
        data = encodeData(payType='package',
                          money=100,
                          rid=self.vipRoomRid,
                          uid=config.pack_cal_uid,
                          giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pack_cal_uid), 70)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    def test_04_prettyRoomPayGiftToBrokerUser(self, des='靓号房打赏礼物给GS进moneyCash'):
        """
        用例描述：
        验证余额足够时，靓号房打赏礼物给工会成员分成为：70:30，且收入在工会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.个人房房间打赏礼物（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：100 * 0.7 =70 (money_cash)
        """
        conMysql.updateMoneySql(config.payUid, money_cash_b=250)
        conMysql.updateMoneySql(config.pack_cal_uid)
        data = encodeData(payType='package',
                          money=100,
                          rid=self.prettyRid,
                          uid=config.pack_cal_uid,
                          giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pack_cal_uid, money_type='money_cash'), 70)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 150)
        case_list_b[des] = result

    def test_05_personRoomPayBox(self, des='靓号房打赏礼盒场景'):
        """
        用例描述：
        验证余额足够时，靓号房打赏礼盒分成满足师徒收益(非一代宗师)的基础上为：70:30，且收入在公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.个人房房间打赏礼盒（打赏100分）
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：700 - 600 = 100
        5.检查收箱用户账户余额，预期值为：大于210,(300*0.7=210)
        """
        conMysql.updateMoneySql(config.payUid, money=400, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(config.pack_cal_uid)
        data = encodeData(payType='package',
                          money=600,
                          rid=self.prettyRid,
                          uid=config.pack_cal_uid,
                          giftId=config.giftId['46'],
                          star=4)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 100)
        assert_len(conMysql.selectUserInfoSql('single_money', config.pack_cal_uid, money_type='money_cash'), 210)
        case_list_b[des] = result