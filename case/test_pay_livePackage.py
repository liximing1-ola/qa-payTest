from common.Config import config
from common.method import reason
from common.conMysql import conMysql
import unittest
from common.Request import post_request_session
from common.Assert import assert_body, assert_code, assert_equal
from common import basicData
from common.Consts import case_list_b, result
from common.runFailed import Retry
@Retry
class TestPayCreate(unittest.TestCase):
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'  # 内网支付接口

    # 角色配置BackUp
    live_role = {
        'pack_ceo': 105002314,  # 直播公会公会长
        'pack_master_NoPack': 105002319,  # 非公会一代宗师主播
        'pack_cal_uid': 105002313,  # 公会签约主播（打包结算），宗师等级可设置为一代和非一代
        'testUid': 105002312,  # 非公会非一代宗师主播
        'live_rid': 193185577,  # 直播间
        'auto_rid': 193185484,  # 商业8坑位房间
        'cp_link_rid': 193185538  # 商业连连看房间
    }

    def test_01_liveRoomPay_6238(self):
        """
        用例描述：
        tdr:直播间内非公会非一代宗师主播打赏后分成比：62:38
        验证余额足够时，直播类型房间（types=live）一对一打赏,打赏分成满足师徒收益(非一代宗师)的基础上为：62:38
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.直播类房间一对一打赏（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：62
        5.检查消费记录表消费money（xs_pay_change_new）
        6.检查消费记录表消费方式op（xs_pay_change_new）
        """
        des = '直播间非公会主播(非宗师)打赏分成62:38'
        conMysql.updateMoneySql(config.payUid, money=30, money_cash=30, money_cash_b=30, money_b=10)
        conMysql.updateMoneySql(config.testUid)
        data = basicData.encodeData(payType='package', money=100, rid=193185408, uid=config.testUid, giftId=5)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('single_money', config.testUid), 62)
        assert_equal(conMysql.selectUserMoneySql('pay_change', config.payUid), 100)
        assert_equal(conMysql.selectUserMoneySql('pay_change', config.payUid, op='op'), 'consume')
        case_list_b[des] = result

    def test_02_ImPay_7228(self):
        """
        用例描述：
        tdr：私聊非公会非一代宗师主播：72:28
        验证余额足够时，私聊一对一打赏,打赏分成满足师徒收益（非公会非一代宗师）的基础上为：72:28
        步骤：
        1.清理打赏者和被打赏者数据
        2.私聊一对一打赏(余额1400分，打赏1000分)
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.72 = 720
        5.检查打赏者剩余余额，预期为：1400 - 1000 = 400
        """
        des = '非公会主播(非宗师)私聊打赏分成72:28'
        conMysql.updateMoneySql(config.payUid, money=1100, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(config.testUid)
        data = basicData.encodeData(payType='chat-gift', uid=config.testUid, num=10, giftId=5)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        # 商业房房主 or （工会会长 or 工会成员）|| 同意大神协议
        assert_equal(conMysql.selectUserMoneySql('single_money', config.testUid), 720)
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 400)
        case_list_b[des] = result

    def test_03_liveRoomPay_7030(self):
        """
        用例描述：
        tdr:直播间内非公会一代宗师主播打赏后分成比：70:30
        验证余额足够时，直播类型房间（types=live）一对一打赏,打赏分成满足师徒收益（一代宗师）的基础上为：70:30
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.直播类房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.7 = 700(账户：money_cash，商业房房主进工会魅力值)
        5.检查打赏者余额，预期为：1000 - 1000 = 0
        """
        des = '直播间非公会主播(宗师)打赏分成7:3'
        test_uid=config.live_role['pack_master_NoPack']  # 非公会一代宗师主播
        conMysql.updateMoneySql(config.payUid, money=900, money_cash=30, money_cash_b=30, money_b=40)
        conMysql.updateMoneySql(test_uid)
        conMysql.checkUserXsMentorLevel(test_uid, 4)  # 更新成一代宗师
        conMysql.updateUserInfoSql('chatroom', test_uid)  # 更新成商业房主播
        data = basicData.encodeData(payType='package', rid=config.live_role['live_rid'], uid=test_uid, giftId=20)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 0)
        assert_equal(conMysql.selectUserMoneySql('single_money', test_uid, money_type='money_cash'), 700)
        case_list_b[des] = result

    def test_04_IMPay_8020(self):
        """
        用例描述：
        tdr:私聊非公会一代宗师主播：80:20, 50%进工会魅力值，30%进个人魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊打赏（打赏1100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：money_cash=500, money_cash_b=30
        5.检查打赏者余额，预期为：1100 - 1000 = 100
        """
        des = '非公会的主播(宗师)私聊打赏分成8:2'
        test_uid = config.live_role['pack_master_NoPack']  # 非公会一代宗师主播
        conMysql.updateMoneySql(config.payUid, money=900, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(test_uid)
        conMysql.checkUserXsMentorLevel(test_uid, 4)  # 更新成一代宗师
        conMysql.updateUserInfoSql('chatroom', test_uid)  # 更新成商业房主播&&直播结算频道
        data = basicData.encodeData(payType='chat-gift', uid=test_uid, giftId=20)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('single_money', test_uid), 300)
        assert_equal(conMysql.selectUserMoneySql('single_money', test_uid, money_type='money_cash'), 500)
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 200)
        case_list_b[des] = result

    def test_05_liveRoomPay_602515(self):
        """
        用例描述：
        tdr:直播间内工会一代宗师主播-公会长-官方抽成：60:25:15,且打包结算频道是直播
        验证直播间打赏一代宗师主播（打包结算主播pack_cal=1），打赏分成满足：60:25:15，且收入在money_cash账户
        脚本步骤：
        1.构造打赏者和主播数据
        2.房间内一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为：1000 * 0.6 = 600(money_cash)
        5.检查公会长余额，预期为：1000 * 0.25 = 250
        6.检查打赏者余额.预期为：1000 - 1000 = 0
        """
        des = '直播间公会主播(宗师)/公会长分成60:25:15'
        test_uid = config.live_role['pack_cal_uid']
        ceo_uid = config.live_role['pack_ceo']
        conMysql.updateUserInfoSql('chatroom', test_uid)  # 商业房房主
        conMysql.updateUserInfoSql('broker_user', test_uid, ceo_uid)  # 打包结算
        conMysql.checkUserXsBroker(ceo_uid)  # 工会公会长
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateUserMoneyClearSql(test_uid, ceo_uid)
        conMysql.checkUserXsMentorLevel(test_uid, 4)  # 师父等级改为一代宗师
        data = basicData.encodeData(payType='package', giftId=20, rid=config.live_role['live_rid'], uid=test_uid)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('single_money', test_uid, money_type='money_cash'), 600)
        assert_equal(conMysql.selectUserMoneySql('sum_money', ceo_uid), 250)
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    def test_06_IMPay_602020(self):
        """
        用例描述：
        tdr:私聊打赏公会一代宗师主播-公会长-官方抽成：60:20:20
        脚本步骤：
        1.构造打赏者和主播数据
        2.私聊打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为：1000 * 0.6 = 600(money_cash)
        5.检查公会长余额，预期为：1000 * 0.2 = 200
        6.检查打赏者余额.预期为：1000 - 1000 = 0
        """
        des = '公会主播(宗师)/公会长私聊分成6:2:2'
        test_uid = config.live_role['pack_cal_uid']
        ceo_uid = config.live_role['pack_ceo']
        conMysql.updateUserInfoSql('chatroom', test_uid)  # 商业房房主
        conMysql.updateUserInfoSql('broker_user', test_uid, ceo_uid)  # 打包结算
        conMysql.checkUserXsBroker(ceo_uid)  # 工会公会长
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateUserMoneyClearSql(test_uid, ceo_uid)
        conMysql.checkUserXsMentorLevel(test_uid, 4)  # 师父等级改为一代宗师
        data = basicData.encodeData(payType='chat-gift', uid=test_uid, giftId=20)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('single_money', test_uid, money_type='money_cash'), 600)
        assert_equal(conMysql.selectUserMoneySql('sum_money', ceo_uid), 200)
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    def test_07_liveRoomPay_602515(self):
        """
        用例描述：
        tdr:直播间内工会非一代宗师主播-公会长-官方：60:25:15
        脚本步骤：
        1.构造打赏者和主播数据
        2.房间内一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为：1000 * 0.6 = 600（money_cash）
        5.检查公会长余额，预期为：1000 * 0.25 = 250
        6.检查打赏者余额.预期为：1000 - 1000 = 0
        """
        des = '直播公会主播(非宗师)/公会长打赏分成60:25:15'
        test_uid = config.live_role['pack_cal_uid']
        ceo_uid = config.live_role['pack_ceo']
        conMysql.updateUserInfoSql('chatroom', test_uid)  # 商业房房主
        conMysql.updateUserInfoSql('broker_user', test_uid, ceo_uid)  # 打包结算
        conMysql.checkUserXsBroker(ceo_uid)  # 工会公会长
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateUserMoneyClearSql(test_uid, ceo_uid)
        conMysql.checkUserXsMentorLevel(test_uid, 1)  # 师父等级改为非一代宗师
        data = basicData.encodeData(payType='package', giftId=20, rid=config.live_role['live_rid'], uid=test_uid)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('single_money', test_uid, money_type='money_cash'), 600)
        assert_equal(conMysql.selectUserMoneySql('sum_money', ceo_uid), 250)
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    def test_08_IMPay_602020(self):
        """
        用例描述：
        tdr:私聊工会非一代宗师主播-公会长-官方：60:20:20
        脚本步骤：
        1.构造打赏者和主播数据
        2.房间内一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为：1000 * 0.6 = 600(money_cash)
        5.检查公会长余额，预期为：1000 * 0.2 = 200
        6.检查打赏者余额.预期为：1000 - 1000 = 0
        """
        des = '公会主播(非宗师)/公会长私聊分成60:20:20'
        test_uid = config.live_role['pack_cal_uid']
        ceo_uid = config.live_role['pack_ceo']
        conMysql.updateUserInfoSql('chatroom', test_uid)  # 商业房房主
        conMysql.updateUserInfoSql('broker_user', test_uid, ceo_uid)  # 打包结算
        conMysql.checkUserXsBroker(ceo_uid)  # 工会公会长
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateUserMoneyClearSql(test_uid, ceo_uid)
        conMysql.checkUserXsMentorLevel(test_uid, 1)  # 师父等级改为非一代宗师
        data = basicData.encodeData(payType='chat-gift', uid=test_uid, giftId=20)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('single_money', test_uid, money_type='money_cash'), 600)
        assert_equal(conMysql.selectUserMoneySql('sum_money', ceo_uid), 200)
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    def test_09_underRolePay_6238(self):
        """
        用例描述：
        验证直播间内打赏麦下用户，在师徒收益基础上，分成比例应为62:38
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内一对一打赏（打赏100分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额和账户，预期为：100 * 0.62 = 62
        5.检查打赏者余额,预期为：100 - 100 = 0
        """
        des = '直播间打赏麦下用户分成62:38'
        conMysql.updateMoneySql(config.payUid, money=100)
        conMysql.updateMoneySql(config.testUid)
        data = basicData.encodeData(payType='package', giftId=5, rid=config.live_role['live_rid'], money=100, uid=config.testUid)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('single_money', config.testUid, money_type='money_cash_b'), 62)
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 0)
        case_list_b[des] = result

    def test_10_NotLiveRoomPayAnchor(self):
        """
        用例描述：
        tdr:非直播频道主播被打赏金额70进个人魅力值（money_cash_b）
        脚本步骤：
        1.构造打赏者和主播数据
        2.非直播房间内一对一打赏（打赏1000分）
        3.校验接口状态和返回值数值
        4.检查被打赏者余额和账户，预期为：1000 * 0.7 = 700(money_cash_b)
        6.检查打赏者余额.预期为：1000 - 1000 = 0
        """
        des = '主播在非直播间被打赏70%进个人魅力'
        test_uid = config.live_role['pack_cal_uid']
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateMoneySql(test_uid)
        conMysql.checkUserXsMentorLevel(test_uid, 4)  # 师父等级改为一代宗师
        data = basicData.encodeData(payType='package', uid=test_uid, giftId=20)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('single_money', test_uid), 700)
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 0)
        case_list_b[des] = result