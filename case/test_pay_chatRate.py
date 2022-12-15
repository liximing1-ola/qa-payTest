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

    def test_01_chatPayNoMoney(self, des='私聊打赏余额不足的场景'):
        """
        用例描述：
        检查账户余额不足时，私聊一对一打赏
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊一对一打赏流程(礼物:棒棒糖)
        3.校验接口和返回值数据
        4.检查预期返回msg，预期：支付失败，提示Toast
        5.检查被打赏者余额,预期：0
        """
        conMysql.updateUserMoneyClearSql(config.payUid, config.rewardUid)
        conMysql.deleteUserAccountSql('broker_user', config.rewardUid)
        conMysql.deleteUserAccountSql('chatroom', config.rewardUid)
        data = encodeData(payType='chat-gift',
                          num=10,
                          giftId=config.giftId['5'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, reason(des, res))
        assert_body(res['body'], 'msg', '余额不足，无法支付', reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.rewardUid), 0)
        case_list[des] = result

    def test_02_chatPayGiftNormalBroker(self, des='私聊打赏礼物GS收72%'):
        """
        用例描述：
        验证私聊打赏礼物给GS时，到账为42%公会魅力值+30%个人魅力值
        脚本步骤：
        1.构造打赏者和主播数据
        2.私聊打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为：1000 * 0.42 = 420(money_cash) + 1000 * 0.3 = 300（money_cash_b）
        6.检查打赏者余额.预期为：1000 - 1000 = 0
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateMoneySql(config.gsUid)
        data = encodeData(payType='chat-gift', uid=config.gsUid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.gsUid,
                                                money_type='money_cash'), 1000 * (config.rate - 0.2))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.gsUid, money_type='money_cash_b'), 300)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list[des] = result

    def test_03_chatPayBoxNormalBroker(self, des='私聊打赏箱子GS收72%'):
        """
        用例描述：
        验证私聊打赏箱子给GS时，到账为42%公会魅力值+30%个人魅力值
        脚本步骤：
        1.构造打赏者和主播数据
        2.私聊打赏（打赏铜箱子600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为不小于： 300 * 0.42 = 126(money_cash) + 300 * 0.3 = 90（money_cash_b）
        5.检查打赏者余额.预期为：1000 - 600 = 400
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateMoneySql(config.gsUid)
        data = encodeData(payType='chat-gift',
                          uid=config.gsUid,
                          money=600,
                          giftId=config.giftId['46'],
                          star=4)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_len(conMysql.selectUserInfoSql('single_money', config.gsUid), 300 * 0.3)
        assert_len(conMysql.selectUserInfoSql('single_money', config.gsUid,
                                              money_type='money_cash'), 300 * (config.rate - 0.2))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 400)
        case_list[des] = result

    def test_04_chatPayGiftNormalUser(self, des='私聊打赏非一代宗师用户分成72%（mcb）'):
        """
        用例描述：
        验证消费打赏礼物时，非一代宗师用户收72%个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为：1000 * 0.72 = 720(money_cash_b)
        5.检查打赏者余额.预期为：1000 - 1000 = 0
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateMoneySql(config.rewardUid)
        data = encodeData(payType='chat-gift')
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.rewardUid), 720)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list[des] = result

    def test_05_chatPayBoxNormalUser(self, des='私聊打赏一代宗师用户分成80%（mcb）'):
        """
        用例描述：
        验证消费打赏箱子时，一代宗师用户收80%个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊打赏（打赏600分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为不小于：300 * 0.8 = 240(money_cash_b)
        5.检查打赏者余额.预期为：1000 - 600 = 400
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateMoneySql(config.masterUid)
        data = encodeData(payType='chat-gift',
                          uid=config.masterUid,
                          money=600,
                          giftId=config.giftId['46'],
                          star=4)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_len(conMysql.selectUserInfoSql('single_money', config.masterUid), 300 * 0.8)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 400)
        case_list[des] = result


