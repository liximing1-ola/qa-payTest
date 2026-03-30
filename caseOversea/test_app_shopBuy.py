# coding=utf-8
"""
APP 海外版支付测试 - 商城购买验证

验证商城使用金豆和钻石购买道具的流程。
"""
import unittest
from common.Config import config
from common.conPtMysql import conMysql
from common.Request import post_request_session
from common.Assert import assert_code, assert_equal, assert_body
from common.method import format_reason
from common.basicData import encodeAppData
from common.Consts import case_list, result


class TestPayCreate(unittest.TestCase):
    """APP 商城购买测试类"""

    def test_01_shopCoinPayChange(self, des: str = '商城购买金豆道具场景', cid: int = 694):
        """
        金豆购买道具验证
        
        用例描述：
        验证商城购买道具逻辑
        
        脚本步骤：
        1. 构造购买者数据（更新 xs_user_money 和 xs_user_commodity）
        2. 商城内购买礼物道具*1 (cid:694 是坐骑小摩托)
        3. 校验接口状态和返回值数据
        4. 检查购买者金豆余额：30000 - 21000 = 9000
        5. 检查背包内物品
        
        Args:
            des: 测试描述
            cid: 物品 ID，默认 694（小摩托）
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, gold_coin=30000)
        conMysql.deleteUserAccountSql('user_commodity', config.app_payUid)
        
        # 2. 商城购买
        data = encodeAppData(payType='coin-shop-buy', money=21000, cid=cid)
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查金豆余额
        assert_equal(conMysql.selectUserInfoSql('single_money', config.app_payUid, money_type='gold_coin'), 9000)
        
        # 5. 检查背包物品
        assert_equal(conMysql.selectUserInfoSql('sum_commodity', config.app_payUid), 1)
        
        case_list[des] = result

    def test_02_shopMoneyPayChange(self, des: str = '商城购买钻石道具场景', cid: int = 42671):
        """
        钻石购买道具验证
        
        用例描述：
        验证商城购买道具逻辑
        
        脚本步骤：
        1. 构造购买者数据（更新 xs_user_money 和 xs_user_commodity）
        2. 商城内购买礼物道具*1 (cid:42671 是小铃铛入场特效)
        3. 校验接口状态和返回值数据
        4. 检查购买者钻石余额：3000 - 3000 = 0
        5. 检查背包内物品
        
        Args:
            des: 测试描述
            cid: 物品 ID，默认 42671（小铃铛入场特效）
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, money=2000, money_cash=200, money_b=400, money_cash_b=400)
        conMysql.deleteUserAccountSql('user_commodity', config.app_payUid)
        
        # 2. 商城购买
        data = encodeAppData(payType='shop-buy', money=3000, cid=cid)
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查钻石余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 0)
        
        # 5. 检查背包物品
        assert_equal(conMysql.selectUserInfoSql('sum_commodity', config.app_payUid), 1)
        
        case_list[des] = result
