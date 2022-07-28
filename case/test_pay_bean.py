from common.Config import config
from common.conMysql import conMysql
import unittest
from common.Request import post_request_session
from common.method import reason
from common.Assert import assert_code, assert_equal, assert_body
from common import basicData
from common.Consts import result, case_list
from common.runFailed import Retry
class TestPayCreate(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        conMysql.checkXsGiftConfig()

    def tearDown(self) -> None:
        conMysql.deleteUserBeanSql(config.payUid, config.rewardUid)   # 清理前置冗余数据

    @Retry
    def test_01_NoBeanPayBeanGift(self, des='打赏金豆礼物但金豆不足的场景'):
        """
        用例描述：
        验证账户内金豆不足时打赏金豆礼物的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内打赏金豆礼物流程(啵啵奶茶)
        3.校验接口状态和返回值数据
        4.检查Toast，预期提示'金豆不足'
        5.检查被打赏者金豆余额,预期：0
        """
        conMysql.deleteUserBeanSql(config.payUid, config.rewardUid)  # 执行前处理数据
        conMysql.updateMoneySql(config.payUid)
        data = basicData.encodeData(payType='package', uid=config.rewardUid, giftId=config.giftId['362'],
                                    giftType='bean')
        res = post_request_session(config.pay_url, data)
        print(res)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, reason(des, res))
        assert_body(res['body'], 'msg', '金豆不足', reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('bean', config.rewardUid), 0)
        case_list[des] = result

    def test_02_beanPayChangeGoldGift(self, des='打赏金豆礼物的场景'):
        """
        用例描述：
        验证金豆足够时打赏金豆礼物的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内打赏金豆礼物的流程（金豆足够）
        3.校验接口状态和返回值数据
        4.检查打赏者金豆余额，预期为：0
        5.检查被打赏者金豆余额，预期为：6000 * 0.5 = 3000
        """
        conMysql.insertBeanSql(config.payUid, money_coupon=6000)
        data = basicData.encodeData(payType='package-more', giftId=config.giftId['362'], giftType='bean', num=6,
                                    uids=('{}'.format(config.rewardUid), ))
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('bean', config.payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('bean', config.rewardUid), 3000)
        case_list[des] = result

    def test_03_MoneyConvertGoldPayGift(self, des='打赏金豆礼物不足用钻转换的场景'):
        """
        用例描述：
        验证打赏金豆礼物时金豆不足用钻转换的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内打赏金豆礼物流程
        3.校验接口状态和返回值数据
        4.检查打赏者金豆余额，预期为：500（不足抵扣）
        5.检查打赏者钻石余额，预期为：10000 - 1000（转换） = 9000
        6.检查被打赏者金豆余额，预期为：1000 * 0.5 = 500
        """
        conMysql.updateMoneySql(config.payUid, money=10000)
        conMysql.updateMoneySql(config.rewardUid)
        conMysql.insertBeanSql(config.payUid, money_coupon=500)
        data = basicData.encodeData(payType='package-exchange', uid=config.rewardUid, giftId=config.giftId['362'],
                                    giftType='bean')
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('bean', config.payUid), 500)
        assert_equal(conMysql.selectUserInfoSql('bean', config.rewardUid), 500)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 9000)
        case_list[des] = result

    def test_04_ImMoneyPayChangeBeanDeduct(self, des='私聊打赏钻石礼物时金豆抵扣平台手续费场景'):
        """
        用例描述：
        验证私聊场景打赏钻石礼物时金豆抵扣平台手续费的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.私聊页打赏钻石礼物的流程
        3.校验接口状态和返回值数据
        4.检查打赏者金豆余额，预期为：200 - 0 = 200（2022.2.24 金豆不再抵扣20%）
        5.检查打赏者钻石余额，预期为：1000 - 1000 = 0
        6.检查被打赏者钻石余额，预期为：1000 * 0.72 = 720
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateMoneySql(config.rewardUid)
        conMysql.insertBeanSql(config.payUid, money_coupon=200)
        data = basicData.encodeData(payType='chat-gift', uid=config.rewardUid)
        res = post_request_session(config.pay_url, data=data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('bean', config.payUid), 200)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.payUid, money_type='money'), 0)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.rewardUid), 720)
        case_list[des] = result

    def test_05_RoomMoneyConvertGoldPayGift(self, des='房间打赏钻石礼物时金豆抵扣平台手续费场景'):
        """
        用例描述：
        验证房间内打赏钻石礼物时金豆抵扣平台手续费的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内打赏金豆礼物的流程
        3.校验接口状态和返回值数据
        4.检查打赏者金豆余额，预期为：400 - 0 = 400
        5.检查打赏者钻石余额，预期为：1000 - 1000 = 0
        6.检查被打赏者账户余额，预期为：1000 * 0.62 = 620
        """
        conMysql.updateMoneySql(config.payUid, money=1000)
        conMysql.updateMoneySql(config.rewardUid)
        conMysql.insertBeanSql(config.payUid, money_coupon=400)
        data = basicData.encodeData(payType='package', uid=config.rewardUid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('bean', config.payUid), 400)
        assert_equal(conMysql.selectUserInfoSql('single_money', config.rewardUid), 620)
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list[des] = result

    @unittest.skip('金豆不再抵扣手续费')
    def test_06_MoneyConvertGoldPayGift(self, des='金豆抵扣手续费但钻石余额少于礼物价格的场景'):
        """
        用例描述：
        验证房间内打赏钻石礼物时金豆抵扣平台手续费的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.房间内打赏金豆礼物的流程
        3.校验接口状态和返回值数据
        4.检查预期：支付失败（钻石小于当前礼物价格时，打赏失败），提示Toast：‘余额不足，无法支付’
        5.检查打赏者钻石余额,预期：700
        6.检查打赏者金豆余额,预期：400
        """
        conMysql.updateMoneySql(config.payUid, money=700)
        conMysql.updateMoneySql(config.rewardUid)
        conMysql.insertBeanSql(config.payUid, money_coupon=400)
        data = basicData.encodeData(payType='package', uid=config.rewardUid)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, reason(des, res))
        assert_body(res['body'], 'msg', '余额不足，无法支付', reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 700)
        assert_equal(conMysql.selectUserInfoSql('bean', config.payUid), 400)
        case_list[des] = result

    @unittest.skip('卡座玩法已下线')
    def test_07_BeanPayChangeCombo(self, des='卡座内购买套餐场景'):
        """
        用例描述：
        验证卡座内购买套餐的场景（钻补）
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.卡座内购买酒桌套餐的流程
        3.校验接口状态和返回值数据
        4.检查购买者金豆余额，预期为：400
        5.检查购买者钻石余额，预期为：80000 - 79900 = 100
        """
        conMysql.deleteUserAccountSql('user_commodity', config.payUid)
        conMysql.updateMoneySql(config.payUid, money=80000)
        conMysql.insertBeanSql(config.payUid, money_coupon=400)
        data = basicData.encodeData(payType='pub-drink-buy', money=79900, rid=config.live_role['auto_rid'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('bean', config.payUid), 400)
        case_list[des] = result

    @unittest.skip('装扮改成钻石货币')
    def test_08_BeanPayChangePresentDeco(self, des='赠送金豆装扮的场景'):
        """
        用例描述：
        赠送金豆装扮的场景
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.礼物面板赠送金豆装扮的流程
        3.校验接口状态和返回值数据
        4.检查打赏者金豆余额，预期为：1000 - 1000 = 0
        5.检查被打赏者背包物品，预期为：1
        """
        conMysql.deleteUserAccountSql('user_commodity', config.rewardUid)
        conMysql.insertBeanSql(config.payUid, money_coupon=1000)
        data = basicData.encodeData(payType='deco-present', uid=config.rewardUid, cid=1629)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_commodity', config.rewardUid), 1)
        assert_equal(conMysql.selectUserInfoSql('bean', config.payUid), 0)
        case_list[des] = result