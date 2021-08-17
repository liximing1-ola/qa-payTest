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

    # 角色配置
    live_role = {
        'pack_ceo': 105002314,  # 直播公会公会长
        'pack_master_NoPack': 105002319,  # 非公会一代宗师主播
        'pack_noMaster': 105002316,  # 非一代宗师主播
        'pack_cal_uid': 105002313,  # 公会签约主播（打包结算），宗师等级可设置为一代和非一代
        'testUid': 105002312,  # 非公会非一代宗师主播
    }

    def test_01_liveRoomPay_6238(self):
        """
        用例描述：
        tdr:直播间内非公会非一代宗师主播打赏后分成比：62:38
        验证余额足够时，直播类型房间（types=live）一对一打赏,打赏分成满足师徒收益(非一代宗师)的基础上为：62:38
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.直播类房间一对一打赏（打赏100分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额，预期为：62
        5.检查消费记录表消费money（xs_pay_change_new）
        6.检查消费记录表消费方式op
        """
        des = '房间打赏非公非宗师主播分成62:38'
        Mysql.updateMoneySql(config.payUid, 30, 30, 30, 10)
        Mysql.updateMoneySql(config.testUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_package_1')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.testUid, money_type='money_cash_b'), 62)
        Assert.assert_equal(Mysql.selectPayChangeSql(config.payUid), 100)
        Assert.assert_equal(Mysql.selectPayChangeOpSql(config.payUid), 'consume')
        Consts.CASE_LIST[des] = 'pass'

    def test_02_ImPay_7228(self):
        """
        用例描述：
        tdr：私聊非公会非一代宗师主播：72:28
        验证余额足够时，私聊一对一打赏,打赏分成满足师徒收益（非公会非一代宗师）的基础上为：72:28
        步骤：
        1.清理打赏者和被打赏者数据 （更新xs_user_money）
        2.私聊一对一打赏(余额1400分，打赏1000分)
        3.校验【status code】和【body】状态
        4.检查被打赏者余额，预期为：720
        5.检查打赏者剩余余额，预期为：400
        """
        des = '私聊打赏非公非宗师主播分成72:28'
        Mysql.updateMoneySql(config.payUid, 1100, 100, 100, 100)
        Mysql.updateMoneySql(config.testUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_chatGift')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        # 商业房房主 or （工会会长 or 工会成员）|| 同意大神协议
        Assert.assert_equal(Mysql.selectMoneySql(config.testUid, money_type='money_cash_b'), 720)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 400)
        Consts.CASE_LIST[des] = 'pass'

    def test_03_liveRoomPay_7030(self):
        """
        用例描述：
        tdr:直播间内非公会一代宗师主播打赏后分成比：70:30
        验证余额足够时，直播类型房间（types=live）一对一打赏,打赏分成满足师徒收益（一代宗师）的基础上为：70:30
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money,xs_mentor_exp）
        2.直播类房间一对一打赏（打赏1000分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额，预期为：700(账户：money_cash，商业房房主进工会魅力值)
        5.检查打赏者余额，预期为：1000 - 1000 = 0
        """
        des = '房间打赏非公宗师主播分成7:3'
        test_uid=config.live_role['pack_master_NoPack']  # 非公会一代宗师主播
        Mysql.updateMoneySql(config.payUid, 900, 30, 30, 40)
        Mysql.updateMoneySql(test_uid)
        Mysql.selectUserXsMentorLevel(test_uid, 4)  # 更新成一代宗师
        Mysql.updateChatroomUid(test_uid)  # 更新成商业房主播
        data = Yaml.read_yaml('Basic.yml', 'dev_livePay_7030')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0)
        Assert.assert_equal(Mysql.selectMoneySql(test_uid, money_type='money_cash'), 700)
        Consts.CASE_LIST[des] = 'pass'

    def test_04_IMPay_8020(self):
        """
        用例描述：
        tdr:私聊非公会一代宗师主播：80:20,50%进工会魅力值，30%进个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.私聊打赏（打赏1100分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额，预期为：money_cash=500, money_cash_b=30
        5.检查打赏者余额，预期为：1100 - 1000 = 100
        """
        des = '私聊打赏非公宗师主播分成8:2'
        test_uid = config.live_role['pack_master_NoPack']  # 非公会一代宗师主播
        Mysql.updateMoneySql(config.payUid, 900, 100, 100, 100)
        Mysql.updateMoneySql(config.testUid)
        Mysql.selectUserXsMentorLevel(test_uid, 4)  # 更新成一代宗师
        Mysql.updateChatroomUid(test_uid)  # 更新成商业房主播
        data = Yaml.read_yaml('Basic.yml', 'dev_IMPay_8020')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(test_uid, 'money_cash_b'), 30)
        Assert.assert_equal(Mysql.selectMoneySql(test_uid, 'money_cash'), 50)
        Assert.assert_equal(Mysql.selectPayChangeSql(config.payUid), 100)
        Consts.CASE_LIST[des] = 'pass'

    @unittest.skip
    def test_05_liveRoomPay_602515(self):
        """
        用例描述：
        tdr:直播间内工会一代宗师主播-公会长-官方抽成：60:25:15
        验证直播间打赏一代宗师主播（打包结算主播pack_cal=1），打赏分成满足：60:25:15，且收入在money_cash账户
        脚本步骤：
        1.构造打赏者和主播数据 （更新xs_user_money和xs_broker_user）
        2.房间内一对一打赏（打赏1000分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额和账户，预期为：money_cash=600
        5.检查公会长余额，预期为：250
        6.检查打赏者余额.预期为：0
        """
        des = '房间打赏宗师公会主播-会长-官方分成：60:25:15'
        Mysql.updateChatroomUid(config.pack_cal_uid)
        Mysql.updateBrokerUser(config.pack_cal_uid)
        Mysql.updateMoneySql(config.payUid, 100)
        Mysql.updateMoneySql(config.pack_cal_uid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pack_cal')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res)
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.pack_cal_uid, 'money_cash'), 60)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0)
        Consts.CASE_LIST[des] = 'pass'

    @unittest.skip
    def test_06_IMPay_602020(self):
        """
        用例描述：
        tdr:私聊公会一代宗师主播-公会长-官方抽成：60:20:20
        脚本步骤：
        1.构造打赏者和主播数据 （更新xs_user_money和xs_broker_user）
        2.私聊打赏（打赏100分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额和账户，预期为：money_cash=60
        5.检查公会长余额，预期为：20
        6.检查打赏者余额.预期为：
        """
        des = '私聊打赏宗师公会主播-会长-官方抽成6:2:2'
        Mysql.updateChatroomUid(config.pack_cal_uid)
        Mysql.updateBrokerUser(config.pack_cal_uid)
        Mysql.updateMoneySql(config.payUid, 100)
        Mysql.updateMoneySql(config.pack_cal_uid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pack_cal')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res)
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.pack_cal_uid, 'money_cash'), 60)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0)
        Consts.CASE_LIST[des] = 'pass'

    @unittest.skip
    def test_07_liveRoomPay_522523(self):
        """
        用例描述：
        tdr:直播间内工会非一代宗师主播-公会长-官方：52:25:23
        脚本步骤：
        1.构造打赏者和主播数据 （更新xs_user_money和xs_broker_user）
        2.房间内一对一打赏（打赏1000分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额和账户，预期为：money_cash=520
        5.检查公会长余额，预期为：250
        6.检查打赏者余额.预期为：0
        """
        des = '房间打赏非宗师公会主播-会长-官方分成：52:25:23'
        Mysql.updateChatroomUid(config.pack_cal_uid)
        Mysql.updateBrokerUser(config.pack_cal_uid)
        Mysql.updateMoneySql(config.payUid, 100)
        Mysql.updateMoneySql(config.pack_cal_uid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pack_cal')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res)
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.pack_cal_uid, 'money_cash'), 60)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0)
        Consts.CASE_LIST[des] = 'pass'

    @unittest.skip
    def test_08_IMPay_522028(self):
        """
        用例描述：
        tdr:私聊工会非一代宗师主播-公会长-官方：52:20:28
        脚本步骤：
        1.构造打赏者和主播数据 （更新xs_user_money和xs_broker_user）
        2.房间内一对一打赏（打赏100分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额和账户，预期为：money_cash=52
        5.检查公会长余额，预期为：20
        6.检查打赏者余额.预期为：0
        """
        des = '私聊打赏非宗师公会主播-会长-官方分成：52:20:28'
        Mysql.updateChatroomUid(config.pack_cal_uid)
        Mysql.updateBrokerUser(config.pack_cal_uid)
        Mysql.updateMoneySql(config.payUid, 100)
        Mysql.updateMoneySql(config.pack_cal_uid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pack_cal')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res)
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.pack_cal_uid, 'money_cash'), 60)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0)
        Consts.CASE_LIST[des] = 'pass'

    @unittest.skip
    def test_09_mentorPayChange(self):
        """
        用例描述：
        验证直播间内打赏麦下用户，在师徒收益基础上，分成比例应为62:38
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money和xs_mentor_exp）
        2.房间内一对一打赏（打赏1000分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额和账户，预期为：620
        5.检查打赏者余额,预期为：0
        """
        des = '直播间打赏麦下用户的场景'
        Mysql.updateMoneySql(config.payUid, 100)
        Mysql.updateMoneySql(config.testUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_mentor_pay')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.testUid), 62)
        Assert.assert_equal(Mysql.selectPayChangeSql(config.payUid), 100)
        Consts.CASE_LIST[des] = 'pass'

    @unittest.skip
    def test_10_NoLiveRoomPayAnchor(self):
        """
        用例描述：
        tdr:非直播频道主播被打赏金额70进个人魅力值（money_cash_b）
        脚本步骤：
        1.构造打赏者和主播数据 （更新xs_user_money和xs_broker_user）
        2.非直播房间内一对一打赏（打赏1000分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额和账户，预期为：money_cash_b=700
        6.检查打赏者余额.预期为：0
        """
        des = '主播在非直播房间内被打赏70进个人魅力值'
        Mysql.updateChatroomUid(config.pack_cal_uid)
        Mysql.updateBrokerUser(config.pack_cal_uid)
        Mysql.updateMoneySql(config.payUid, 100)
        Mysql.updateMoneySql(config.pack_cal_uid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pack_cal')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res)
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.pack_cal_uid, 'money_cash'), 60)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 0)
        Consts.CASE_LIST[des] = 'pass'