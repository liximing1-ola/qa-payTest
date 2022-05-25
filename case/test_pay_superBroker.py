from common.Config import config
from common.conMysql import conMysql
from common.method import reason
import unittest
import pytest
from common.Request import post_request_session
from common.Assert import assert_body, assert_code, assert_equal
from common import basicData
from common.runFailed import Retry
from common.Consts import case_list_b, result
from common.conRedis import conRedis
@Retry
class TestPayCreate(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        conMysql.updateUserInfoSql('super_chatroom', config.star_role['super-voice-fresh'])

    @pytest.mark.run(order=1)
    def test_01_starRoomNoBrokerArtistPay_35(self, des='网赚房无公会无经纪人初级艺人收35%个人魅力值'):
        """
        用例描述：
        tdr：网赚频道非公会无经纪人的初级艺人（0-3500）被打赏后收到35%的个人魅力值（此类房间不走师徒分成）
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.35 = 350(个人魅力值)
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        test_uid = config.star_role['testUid']  # 105002312
        conMysql.updateMoneySql(test_uid)
        conMysql.checkOnlineEarnArtist(test_uid, worth=700)  # 设置用户为初级艺人
        data = basicData.encodeData(payType='package', rid=config.star_role['super-voice-fresh'],
                                    uid=test_uid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', test_uid), 350)
        assert_equal(conMysql.selectUserInfoSql('sum_money', test_uid), 350)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    @pytest.mark.run(order=2)
    def test_02_starRoomNoBrokerArtistPay_45(self, des='网赚房无公会无经纪人中级艺人收45%个人魅力值'):
        """
        用例描述：
        tdr：网赚频道非公会无经纪人的中级艺人（3501-10000）被打赏后收到45%的个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.45 = 450(个人魅力值)
        """
        conMysql.updateMoneySql(config.payUid, money=1200)
        test_uid = config.star_role['testUid']
        conMysql.updateMoneySql(test_uid)
        conMysql.checkOnlineEarnArtist(test_uid, worth=3501)  # 设置一个中级艺人
        data = basicData.encodeData(payType='package', rid=config.star_role['super-voice-fresh'],
                                    uid=test_uid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', test_uid), 450)
        assert_equal(conMysql.selectUserInfoSql('sum_money', test_uid), 450)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 200)
        case_list_b[des] = result

    @pytest.mark.run(order=3)
    def test_03_starRoomNoBrokerArtistPay_55(self, des='网赚房无公会无经纪人高级艺人收55%个人魅力值'):
        """
        用例描述：
        tdr：网赚频道非公会无经纪人的高级艺人（>10001）被打赏后收到55%的个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.55 = 550(个人魅力值)
        """
        conMysql.updateMoneySql(config.payUid, money=1300)
        test_uid = config.star_role['testUid']
        conMysql.updateMoneySql(test_uid)
        conMysql.checkOnlineEarnArtist(test_uid, worth=10001)
        data = basicData.encodeData(payType='package', rid=config.star_role['super-voice-fresh'],
                                    uid=test_uid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', test_uid), 550)
        assert_equal(conMysql.selectUserInfoSql('sum_money', test_uid), 550)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 300)
        case_list_b[des] = result

    @pytest.mark.run(order=4)
    def test_05_starRoomNoAgentPay_45(self, des='网赚指定工会无经纪人中级艺人收45%公会魅力值'):
        """
        用例描述：
        tdr：网赚频道有公会无经纪人的中级艺人（3501-10000）被打赏后收到45%的公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.45 = 450（公会魅力值）
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        test_uid = config.star_role['super_star_uid']  # 105002325
        test_bid = config.star_role['super_broker']
        conMysql.updateMoneySql(test_uid)  # 清空账户
        conMysql.updateSuperVoiceUser(test_uid, test_bid, nid=200)  # 修改用户为网赚工会用户
        conMysql.checkOnlineEarnArtist(test_uid, worth=5000)  # 设置为中级艺人
        data = basicData.encodeData(payType='package', rid=config.star_role['super-voice-fresh'],
                                    uid=test_uid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', test_uid, money_type='money_cash'), 450)
        assert_equal(conMysql.selectUserInfoSql('sum_money', test_uid), 450)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    @pytest.mark.run(order=5)
    def test_05_starRoomSuperVoicePay_508(self, des='网赚无工会有经纪人(1j)初级艺人分成50:8'):
        """
        用例描述：
        tdr：网赚频道无公会有经纪人的初级艺人（0-3500）被打赏后收到50%的个人魅力值，初级经纪人（公会）收到8%公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.5 = 500（个人魅力值）
        5.检查经纪人余额，预期为：1000 * 0.8 = 80（个人魅力值）
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        test_uid = config.star_role['agent_star_uid']  # 105002331
        test_agent = config.star_role['super_agent_uid']  # 105002323
        conMysql.checkOnlineEarnAgent(test_agent)  # 检查用户经纪人身份
        conMysql.checkOnlineEarnArtist(test_uid, worth=700)   # 设置艺人为初级艺人
        conMysql.updateUserMoneyClearSql(test_agent, test_uid)  # 清空用户账户
        conMysql.checkOnlineEarnRelation(test_agent, test_uid)  # 检查艺人经纪人关联关系
        conMysql.deleteUserAccountSql('broker_user', test_uid)  # 删除用户工会数据
        conMysql.checkUserBroker(test_agent)
        data = basicData.encodeData(payType='package', rid=config.star_role['super-voice-fresh'],
                                    uid=test_uid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', test_uid, money_type='money_cash_b'), 500)
        assert_equal(conMysql.selectUserInfoSql('single_money', test_agent, money_type='money_cash'), 80)
        assert_equal(conMysql.selectUserInfoSql('sum_money', test_uid), 500)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    @pytest.mark.run(order=6)
    def test_06_starRoomArtistAgent_608(self, des='网赚指定工会有经纪人(1j)的中级艺人分成60:8'):
        """
        用例描述：
        tdr：网赚频道有公会有经纪人的中级艺人（3501-10000）被打赏后收到60%的公会魅力值，初级经纪人（公会）收到8%公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.6 = 600
        5.检查经纪人余额，预期为：1000 * 0.08 = 80
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        test_uid = config.star_role['agent_star_uid']  # 105002331
        test_agent = config.star_role['super_agent_uid']  # 105002323
        test_bid = config.star_role['super_broker']  # 136594717
        conMysql.checkOnlineEarnArtist(test_uid, worth=4200)
        conMysql.checkOnlineEarnRelation(test_agent, test_uid)  # 检查经纪人艺人关系
        conMysql.updateUserMoneyClearSql(test_agent, test_uid)  # 清空用户账户
        conMysql.insertSuperVoiceUser(test_uid, test_bid)  # 加入指定公会
        data = basicData.encodeData(payType='package', rid=config.star_role['super-voice-fresh'],
                                    uid=test_uid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', test_uid, money_type='money_cash'), 600)
        assert_equal(conMysql.selectUserInfoSql('single_money', test_agent, money_type='money_cash'), 80)
        assert_equal(conMysql.selectUserInfoSql('sum_money', test_uid), 600)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    @pytest.mark.run(order=7)
    def test_07_starRoomArtistAgent_7012(self, des='网赚有工会有经纪人(7j)高级艺人分成70:12'):
        """
        用例描述：
        tdr：网赚频道有公会有经纪人的高级艺人（>10001）被打赏后收到70%的公会魅力值，高级经纪人（公会）收到12%公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.7 = 700（money_cash）
        5.检查经纪人余额，预期为： 1000 * 0.12 = 120(money_cash)
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        test_uid = config.star_role['pack_cal_uid']  # 105002313
        test_bid = config.star_role['super_broker']  # 136594717
        test_agent = config.star_role['super_agent_uid']  # 105002323
        conMysql.checkOnlineEarnArtist(test_uid, worth=10001)  # 设置用户为高级艺人
        conMysql.checkOnlineEarnAgent(test_agent, point=100000)  # 更新经纪人等级
        conMysql.updateUserMoneyClearSql(test_agent, test_uid)  # 更新余额
        conMysql.checkOnlineEarnRelation(test_agent, test_uid)  # 更新经纪人和艺人身份
        conMysql.checkSuperVoiceUser(test_uid, test_bid)  # 加入公会
        data = basicData.encodeData(payType='package', rid=config.star_role['super-voice-fresh'],
                                    uid=test_uid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', test_uid, money_type='money_cash'), 700)
        assert_equal(conMysql.selectUserInfoSql('single_money', test_agent, money_type='money_cash'), 120)
        assert_equal(conMysql.selectUserInfoSql('sum_money', test_uid), 700)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    @pytest.mark.run(order=8)
    def test_08_NormalRoomPayArtist_620(self, des='普通房指定工会有经纪人(1j)只艺人收到62%'):
        """
        用例描述：
        tdr：非网赚频道王牌公会中有经纪人的艺人被打赏后收到62%的个人魅力值，经纪人无收入
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.62 = 620（个人魅力值）
        5.检查经纪人余额，预期为：0
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        test_uid = config.star_role['agent_star_uid']  # 105002331
        # test_bid = config.super_live_role['super_broker']  # 136594717
        test_agent = config.star_role['super_agent_uid']  # 105002323
        conMysql.checkOnlineEarnAgent(test_agent)
        conMysql.checkOnlineEarnArtist(test_uid, worth=4200)
        conMysql.updateUserMoneyClearSql(test_agent, test_uid)
        # conMysql.updateSuperVoiceUser(test_uid, test_bid, nid=200)  # 更新用户到指定工会,上面case已加入
        conMysql.checkOnlineEarnRelation(test_agent, test_uid)
        data = basicData.encodeData(payType='package')
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', test_uid), 620)
        assert_equal(conMysql.selectUserInfoSql('single_money', test_agent), 0)
        assert_equal(conMysql.selectUserInfoSql('sum_money', test_uid), 620)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    @pytest.mark.run(order=9)
    def test_09_starRoomWhiteUserPay_70(self, des='网赚房无公会无经纪人白名单艺人收70%个人魅力值'):
        """
        用例描述：
        tdr：网赚频道非公会无经纪人的白名单初级艺人（0-3500）被打赏后收到70%的个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.7 = 700(个人魅力值)
        """
        conMysql.updateMoneySql(config.payUid, money=2000)
        test_uid = config.star_role['white_uid']  # Redis-cli SADD Xs.WhiteList.SuperVoice.White 105002338
        conRedis.checkSetKey('Xs.WhiteList.SuperVoice.White', test_uid)
        conMysql.updateMoneySql(test_uid)
        conMysql.checkOnlineEarnArtist(test_uid, worth=700)  # 设置用户为初级艺人
        conMysql.checkWhiteUid(test_uid, white_type=105)  # type=105是网赚白名单用户
        data = basicData.encodeData(payType='package', rid=config.star_role['super-voice-fresh'],
                                    uid=test_uid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', test_uid), 700)
        assert_equal(conMysql.selectUserInfoSql('sum_money', test_uid), 700)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 1000)
        case_list_b[des] = result