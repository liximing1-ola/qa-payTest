from common.Config import config
from common import Request
from common.params_Yaml import Yaml
from common.sqlScript import Mysql
import unittest
from common import Consts, Assert
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
        'super-voice-fresh': 200000287  # 网赚房间
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
        des = '网赚无公会35'
        Mysql.updateMoneySql(config.payUid, 1000)
        test_uid=config.super_live_role['testUid']
        Mysql.updateMoneySql(test_uid)
        data = Yaml.read_yaml('Basic.yml', 'dev_noBroker_35')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(test_uid, money_type='money_cash_b'), 350)
        Assert.assert_equal(Mysql.selectAllMoneySql(test_uid), 350)
        Consts.CASE_LIST[des] = Consts.result

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
        des = '网赚公会无经纪人35'
        Mysql.updateMoneySql(config.payUid, 1000)
        test_uid = config.super_live_role['super_star_uid']
        test_bid = config.super_live_role['super_broker']
        Mysql.updateMoneySql(test_uid)
        Mysql.updateSuperVoiceUser(test_bid, test_uid)
        data = Yaml.read_yaml('Basic.yml', 'dev_superVoice_35')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(test_uid, money_type='money_cash'), 350)
        Assert.assert_equal(Mysql.selectAllMoneySql(test_uid), 350)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0)
        Consts.CASE_LIST[des] = Consts.result

    def test_03_starRoomSuperVoicePay_50(self):
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
        des = '网赚公会无经纪人50'
        Mysql.updateMoneySql(config.payUid, 1000)
        test_uid = config.super_live_role['agent_star_uid']
        test_bid = config.super_live_role['super_broker']
        test_agent = config.super_live_role['super_agent_uid']
        Mysql.selectOnlineEarnAgent(test_agent, 100)
        Mysql.selectOnlineEarnArtist(test_uid, 100)
        Mysql.updateMoneySql(test_uid)
        Mysql.updateMoneySql(test_agent)
        Mysql.updateSuperVoiceUser(test_bid, test_uid)
        Mysql.updateSuperVoiceUser(test_bid, test_agent)
        Mysql.updateOnlineEarnRelation(test_agent, test_uid)
        data = Yaml.read_yaml('Basic.yml', 'dev_superVoice_5015')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(test_uid, money_type='money_cash'), 500)
        Assert.assert_equal(Mysql.selectAllMoneySql(test_uid), 350)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0)
        Consts.CASE_LIST[des] = Consts.result

    def test_04_starRoomAgent_20(self):
        """
        用例描述：
        tdr：网赚房间内指定公会中有经纪人的艺人被打赏后收到50%的公会魅力值，6级及以上经纪人收到20%公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.网赚房间一对一打赏（打赏1000分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额，预期为：500
        """

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