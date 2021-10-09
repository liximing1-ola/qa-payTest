from common.Config import config
from common.params_Yaml import Yaml
from common.sqlScript import Mysql
import unittest
from common import Consts, Assert, Request, basicData
from common.runFailed import Retry
@Retry
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

    # 角色配置BackUp
    super_live_role = {
        'testUid': 105002312,  # 非公会用户
        'auto_rid': 193185484,  # 商业8坑位房间
        'super_star_uid': 105002325,  # 指定工会艺人
        'super_agent_uid': 105002323,  # 指定工会经纪人
        'agent_star_uid': 105002331,  # 指定工会内有经纪人(105002323)的艺人
        'super_broker': 136594717,  # 指定工会bid
        'super-voice-fresh': 200000287,  # 网赚房间
        'pack_cal_uid': 105002313,  # 公会签约主播（打包结算）
    }

    @classmethod
    def setUpClass(cls) -> None:
        Mysql.updateXsFreshRoom()

    def test_01_starRoomNoBrokerPay_35(self):
        """
        用例描述：
        tdr：网赚房间内无公会无经纪人的艺人被打赏后收到35%的个人魅力值（此类房间不走师徒分成）
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.网赚房间一对一打赏（打赏1000分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额，预期为：350(个人魅力值)
        """
        des = '网赚房无公会无经纪人艺人收35%个人魅力值'
        Mysql.updateMoneySql(config.payUid, 1000)
        test_uid=config.super_live_role['testUid']
        Mysql.updateMoneySql(test_uid)
        data = basicData.encodeData(payType='package', rid=config.super_live_role['super-voice-fresh'], uid=test_uid)
        # data = Yaml.read_yaml('Basic.yml', 'dev_noBroker_35')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(test_uid, money_type='money_cash_b'), 350)
        Assert.assert_equal(Mysql.selectAllMoneySql(test_uid), 350)
        Consts.CASE_LIST_2[des] = Consts.result

    def test_02_starRoomSuperVoicePay_35(self):
        """
        用例描述：
        tdr：网赚房间内指定公会中无经纪人的艺人被打赏后收到35%的公会魅力值（此类房间内不走师徒分成）
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.网赚房间一对一打赏（打赏1000分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额，预期为：350（公会魅力值）
        """
        des = '网赚房指定工会无经纪人艺人收35%工会魅力值'
        Mysql.updateMoneySql(config.payUid, 1000)
        test_uid = config.super_live_role['super_star_uid']
        test_bid = config.super_live_role['super_broker']
        Mysql.updateMoneySql(test_uid)
        Mysql.updateSuperVoiceUser(test_bid, test_uid)
        data = basicData.encodeData(payType='package', rid=config.super_live_role['super-voice-fresh'], uid=test_uid)
        # data = Yaml.read_yaml('Basic.yml', 'dev_superVoice_35')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(test_uid, money_type='money_cash'), 350)
        Assert.assert_equal(Mysql.selectAllMoneySql(test_uid), 350)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0)
        Consts.CASE_LIST_2[des] = Consts.result

    def test_03_starRoomSuperVoicePay_5015(self):
        """
        用例描述：
        tdr：网赚房间内指定公会中有经纪人的艺人被打赏后收到50%的公会魅力值，经纪人收到15%工会魅力值（看经纪人身份到账哪个账户）
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.网赚房间一对一打赏（打赏1000分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额，预期为：500（工会魅力值）
        5.检查经纪人余额，预期为：150（工会魅力值）
        """
        des = '网赚房指定工会有经纪人(1j)艺人分成50:15'
        Mysql.updateMoneySql(config.payUid, 1000)
        test_uid = config.super_live_role['agent_star_uid']
        test_bid = config.super_live_role['super_broker']
        test_agent = config.super_live_role['super_agent_uid']
        Mysql.selectOnlineEarnAgent(test_agent)
        Mysql.selectOnlineEarnArtist(test_uid)
        Mysql.updateMoneySql(test_uid)
        Mysql.updateMoneySql(test_agent)
        Mysql.updateSuperVoiceUser(test_bid, test_uid, nid=98)
        Mysql.updateSuperVoiceUser(test_bid, test_agent)
        Mysql.updateOnlineEarnRelation(test_agent, test_uid)
        data = basicData.encodeData(payType='package', rid=config.super_live_role['super-voice-fresh'], uid=test_uid)
        # data = Yaml.read_yaml('Basic.yml', 'dev_superVoice_5015')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(test_uid, money_type='money_cash'), 500)
        Assert.assert_equal(Mysql.selectMoneySql(test_agent, money_type='money_cash'), 150)
        Assert.assert_equal(Mysql.selectAllMoneySql(test_uid), 500)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0)
        Consts.CASE_LIST_2[des] = Consts.result

    def test_04_starRoomAgent_5020(self):
        """
        用例描述：
        tdr：网赚房间内指定公会中有经纪人的艺人被打赏后收到50%的公会魅力值，6级及以上经纪人收到20%公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.网赚房间一对一打赏（打赏1000分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额，预期为：500
        5.检查经纪人余额，预期为：200
        """
        des = '网赚房指定工会有经纪人(7j)的艺人分成50:20'
        Mysql.updateMoneySql(config.payUid, 1000)
        test_uid = config.super_live_role['agent_star_uid']
        test_bid = config.super_live_role['super_broker']
        test_agent = config.super_live_role['super_agent_uid']
        Mysql.selectOnlineEarnAgent(test_agent, 100000)
        Mysql.selectOnlineEarnArtist(test_uid)
        Mysql.updateMoneySql(test_uid)
        Mysql.updateMoneySql(test_agent)
        Mysql.updateSuperVoiceUser(test_bid, test_uid, nid=98)
        Mysql.updateSuperVoiceUser(test_bid, test_agent)
        Mysql.updateOnlineEarnRelation(test_agent, test_uid)
        data = basicData.encodeData(payType='package', rid=config.super_live_role['super-voice-fresh'], uid=test_uid)
        # data = Yaml.read_yaml('Basic.yml', 'dev_superVoice_5020')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(test_uid, money_type='money_cash'), 500)
        Assert.assert_equal(Mysql.selectMoneySql(test_agent, money_type='money_cash'), 200)
        Assert.assert_equal(Mysql.selectAllMoneySql(test_uid), 500)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0)
        Consts.CASE_LIST_2[des] = Consts.result

    def test_05_starRoomNormalBroker_50(self):
        """
        用例描述：
        tdr：网赚房间内普通公会中有经纪人的艺人被打赏后收到50%的个人魅力值，6级及以上经纪人收到20%公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.网赚房间一对一打赏（打赏1000分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额，预期为：500
        """
        des = '网赚房普通工会有经纪人(7j)艺人分成50(个人):20(工会)'
        Mysql.updateMoneySql(config.payUid, 1000)
        test_uid = config.super_live_role['pack_cal_uid']
        test_bid = config.super_live_role['super_broker']
        test_agent = config.super_live_role['super_agent_uid']
        Mysql.selectOnlineEarnAgent(test_agent, 100000)
        Mysql.updateMoneySql(test_uid)
        Mysql.updateMoneySql(test_agent)
        Mysql.updateSuperVoiceUser(test_bid, test_agent)
        Mysql.updateOnlineEarnRelation(test_agent, test_uid)
        data = basicData.encodeData(payType='package', rid=config.super_live_role['super-voice-fresh'], uid=test_uid)
        # data = Yaml.read_yaml('Basic.yml', 'dev_normalBroker_5020')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(test_uid, money_type='money_cash_b'), 500)
        Assert.assert_equal(Mysql.selectMoneySql(test_agent, money_type='money_cash'), 200)
        Assert.assert_equal(Mysql.selectAllMoneySql(test_uid), 500)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0)
        Consts.CASE_LIST_2[des] = Consts.result

    def test_06_SuperStarNormalRoomPay_5015(self):
        """
        用例描述：
        tdr：普通房间内指定公会中有经纪人的艺人被打赏后收到62%的个人魅力值，经纪人无收入
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.网赚房间一对一打赏（打赏1000分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额，预期为：500（工会魅力值）
        5.检查经纪人余额，预期为：150（工会魅力值）
        """
        des = '普通房指定工会有经纪人(1j)只艺人收到62%'
        Mysql.updateMoneySql(config.payUid, 1000)
        test_uid = config.super_live_role['agent_star_uid']
        test_bid = config.super_live_role['super_broker']
        test_agent = config.super_live_role['super_agent_uid']
        Mysql.selectOnlineEarnAgent(test_agent)
        Mysql.selectOnlineEarnArtist(test_uid)
        Mysql.updateMoneySql(test_uid)
        Mysql.updateMoneySql(test_agent)
        Mysql.updateSuperVoiceUser(test_bid, test_uid, nid=98)
        Mysql.updateSuperVoiceUser(test_bid, test_agent)
        Mysql.updateOnlineEarnRelation(test_agent, test_uid)
        data = basicData.encodeData(payType='package')
        # data = Yaml.read_yaml('Basic.yml', 'dev_normalRoom_6215')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(test_uid, money_type='money_cash_b'), 620)
        Assert.assert_equal(Mysql.selectMoneySql(test_agent, money_type='money_cash_b'), 0)
        Assert.assert_equal(Mysql.selectAllMoneySql(test_uid), 620)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0)
        Consts.CASE_LIST_2[des] = Consts.result