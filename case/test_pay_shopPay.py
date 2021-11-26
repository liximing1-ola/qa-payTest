from common.Config import config
from common.conMysql import conMysql
from common.method import reason
import unittest
import pytest
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_equal
from common.Consts import case_list, result
from common import basicData
from common.runFailed import Retry
@Retry
class TestPayCreate(unittest.TestCase):
    pay_url = config.pay_url

    @pytest.mark.run(order=1)
    def test_01_shopPayChangeMoney(self):
        """
        用例描述：
        验证商城购买道具逻辑
        脚本步骤：
        1.构造购买者数据 （更新xs_user_money和xs_user_commodity）
        2.商城内购买礼物道具*1
        3.校验接口状态和返回值数据
        4.检查购买者余额 (200-100=100)
        5.检查背包内物品
        """
        cid=329  # 四叶草
        des = '商城购买单个道具场景'
        conMysql.updateMoneySql(config.payUid, money_cash=100, money_cash_b=100)
        conMysql.deleteUserAccountSql('user_commodity', config.payUid)
        data = basicData.encodeData(payType='shop-buy', money=100, cid=cid)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 100)
        assert_equal(conMysql.selectUserMoneySql('sum_commodity', config.payUid), 1)
        case_list[des] = result

    @pytest.mark.run(order=2)
    def test_02_shopPayChangeBuyMore(self):
        """
        用例描述：
        验证商城购买多个道具场景
        脚本步骤：
        1.构造购买者数据 （更新xs_user_money和xs_user_commodity）
        2.商城内购买礼物道具*10 9900*10=99000
        3.校验接口状态和返回值数据
        4.检查购买者余额：103000-99000=4000
        5.检查背包内物品：10
        """
        cid=340  # 小天使
        des = '商城购买n个道具场景'
        conMysql.updateMoneySql(config.payUid, money=1000, money_cash=100000, money_cash_b=1000, money_b=1000)
        data = basicData.encodeData(payType='shop-buy', cid=cid, money=9900, num=10)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.payUid), 4000)
        assert_equal(conMysql.selectUserMoneySql('num_commodity', config.payUid, cid=cid), 10)
        case_list[des] = result

    @pytest.mark.run(order=3)
    def test_03_shopGiftToUser(self):
        """
        用例描述：
        验证商城购买的道具在房间内赠送给其他人，他人收到的分成比在师徒收益上为 62：38
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.打赏背包道具 cid：340 * 1
        3.校验接口状态和返回值数据
        4.检查背包内物品：10 - 1 = 9
        5.检查被打赏者余额：990*0.62 = 6138
        """
        des = '打赏背包内物品场景'
        bag_gift_cid = 340
        conMysql.updateUserMoneyClearSql(config.payUid, config.testUid)
        cid = int(conMysql.selectUserMoneySql('id_commodity', config.payUid, cid=bag_gift_cid))
        data = basicData.encodeData(payType='package', rid=config.super_live_role['auto_rid'], uid=config.testUid,
                                    giftId=54, money=9900, package_cid=cid, ctype='gift')
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('num_commodity', config.payUid, cid=bag_gift_cid), 9)
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.testUid), 6138)
        case_list[des] = result

    @pytest.mark.run(order=4)
    def test_04_shopGiftToUserNoEnough(self):
        """
        用例描述：
        验证商城购买的道具赠送时不足的情况
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.打赏背包道具 cid：340 * 10
        3.校验接口状态和返回值数据
        4.检查背包内物品
        5.检查被打赏者余额 预期：0
        """
        des = '打赏背包物品但物品不足抵扣的场景'
        bag_gift_cid = 340
        conMysql.updateUserMoneyClearSql(config.payUid, config.testUid)
        cid = int(conMysql.selectUserMoneySql('id_commodity', config.payUid, cid=bag_gift_cid))
        data = basicData.encodeData(payType='package', rid=config.super_live_role['auto_rid'], uid=config.testUid,
                                    giftId=54, money=99000, package_cid=cid, ctype='gift', num=10)
        res = post_request_session(TestPayCreate.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, reason(des, res))
        assert_body(res['body'], 'msg', '余额不足，无法支付', reason(des, res))
        assert_equal(conMysql.selectUserMoneySql('num_commodity', config.payUid, cid=bag_gift_cid), 9)
        assert_equal(conMysql.selectUserMoneySql('sum_money', config.testUid), 0)
        case_list[des] = result