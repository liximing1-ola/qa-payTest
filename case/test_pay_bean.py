from common.Config import config
from common.conMysql import conMysql as mysql
import unittest
from common.Request import post_request_session
from common.method import reason
from common.method import checkUserVipExp
from common.Assert import assert_code, assert_equal, assert_body
from common.basicData import encodeData
from common.Consts import result, case_list
from common.runFailed import Retry


@Retry(max_n=3)
class TestPayCreate(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        mysql.checkXsGiftConfig()

    def tearDown(self) -> None:
        mysql.deleteUserBeanSql(config.payUid, config.rewardUid)  # 清理前置冗余数据

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
        mysql.deleteUserBeanSql(config.payUid, config.rewardUid)  # 执行前处理数据
        mysql.updateMoneySql(config.payUid)
        data = encodeData(payType='package',
                          giftId=config.giftId['362'],
                          giftType='bean')
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, reason(des, res))
        assert_body(res['body'], 'msg', '金豆不足', reason(des, res))
        assert_equal(mysql.selectUserInfoSql('bean', config.rewardUid), 0)
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
        mysql.insertBeanSql(config.payUid, money_coupon=6000)
        data = encodeData(payType='package-more',
                          giftId=config.giftId['362'],
                          giftType='bean',
                          num=6,
                          uids=('{}'.format(config.rewardUid),))
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(mysql.selectUserInfoSql('bean', config.payUid), 0)
        assert_equal(mysql.selectUserInfoSql('bean', config.rewardUid), 3000)
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
        mysql.updateMoneySql(config.payUid, money=10000)
        mysql.updateMoneySql(config.rewardUid)
        mysql.insertBeanSql(config.payUid, money_coupon=500)
        vip_level = int(mysql.selectUserInfoSql('pay_room_money', config.payUid))
        print(vip_level)
        data = encodeData(payType='package-exchange',
                          giftId=config.giftId['362'],
                          giftType='bean')
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(mysql.selectUserInfoSql('bean', config.payUid), 500)
        assert_equal(mysql.selectUserInfoSql('bean', config.rewardUid), 500)
        assert_equal(mysql.selectUserInfoSql('sum_money', config.payUid), 9000)
        print(vip_level + checkUserVipExp(money_type='bean', pay_off=1000))
        print(mysql.selectUserInfoSql('pay_room_money', config.payUid))
        assert_equal(mysql.selectUserInfoSql('pay_room_money', config.payUid),
                     vip_level + checkUserVipExp(money_type='bean', pay_off=1000))
        case_list[des] = result

    def test_04_ImMoneyPayChangeBeanDeduct(self, des='私聊打赏钻石礼物时金豆不再抵扣平台手续费'):
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
        mysql.updateMoneySql(config.payUid, money=1000)
        mysql.updateMoneySql(config.rewardUid)
        mysql.insertBeanSql(config.payUid, money_coupon=200)
        data = encodeData(payType='chat-gift')
        res = post_request_session(config.pay_url, data=data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(mysql.selectUserInfoSql('bean', config.payUid), 200)
        assert_equal(mysql.selectUserInfoSql('single_money', config.payUid, money_type='money'), 0)
        assert_equal(mysql.selectUserInfoSql('sum_money', config.rewardUid), 720)
        case_list[des] = result

    def test_05_RoomMoneyConvertGoldPayGift(self, des='房间打赏钻石礼物时金豆不再抵扣平台手续费'):
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
        mysql.updateMoneySql(config.payUid, money=1000)
        mysql.updateMoneySql(config.rewardUid)
        mysql.insertBeanSql(config.payUid, money_coupon=400)
        data = encodeData(payType='package')
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(mysql.selectUserInfoSql('bean', config.payUid), 400)
        assert_equal(mysql.selectUserInfoSql('single_money', config.rewardUid), 620)
        assert_equal(mysql.selectUserInfoSql('sum_money', config.payUid), 0)
        case_list[des] = result

    @unittest.skip('2022/5/12 金豆不再抵扣手续费')
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
        pass

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
        pass
