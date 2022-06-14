from common.Config import config
from common.conPtMysql import conMysql
from common.Request import post_request_session
import unittest
from common.Assert import assert_code, assert_equal, assert_body
from common.method import reason
from common.basicData import encodePtData
from common.Consts import case_list, result
class TestPayCreate(unittest.TestCase):

    def test_01_shopCoinPayChange(self, des='商城购买金豆道具场景', cid=694):
        """
        用例描述：
        验证商城购买道具逻辑
        脚本步骤：
        1.构造购买者数据 （更新xs_user_money和xs_user_commodity）
        2.商城内购买礼物道具*1 (cid:694是坐骑小摩托)
        3.校验接口状态和返回值数据
        4.检查购买者金豆余额：30000 - 21000 = 9000
        5.检查背包内物品
        """
        conMysql.updateMoneySql(config.pt_payUid, gold_coin=30000)
        conMysql.deleteUserAccountSql('user_commodity', config.pt_payUid)
        data = encodePtData(payType='coin-shop-buy', money=21000, cid=cid)
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.pt_payUid, money_type='gold_coin'), 9000)
        assert_equal(conMysql.selectUserInfoSql('sum_commodity', config.pt_payUid), 1)
        case_list[des] = result

    def test_02_shopMoneyPayChange(self, des='商城购买钻石道具场景', cid=2158):
        """
        用例描述：
        验证商城购买道具逻辑
        脚本步骤：
        1.构造购买者数据 （更新xs_user_money和xs_user_commodity）
        2.商城内购买礼物道具*1 (cid:2158是30天男爵道具)
        3.校验接口状态和返回值数据
        4.检查购买者钻石余额：18000 - 18000 = 0
        5.检查背包内物品
        """
        conMysql.updateMoneySql(config.pt_payUid, money=10000, money_cash=2000, money_b=2000, money_cash_b=4000)
        conMysql.deleteUserAccountSql('user_commodity', config.pt_payUid)
        data = encodePtData(payType='shop-buy', money=18000, cid=cid)
        res = post_request_session(config.pt_pay_url, data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('sum_commodity', config.pt_payUid), 1)
        case_list[des] = result





