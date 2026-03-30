# coding=utf-8
"""
APP 海外版支付测试 - 背包开箱验证

验证背包内开箱子得到物品的流程。
"""
import unittest
from common.Config import config
from common.method import format_reason
from common.conPtMysql import conMysql
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_len, assert_equal
from common.basicData import encodeAppData
from common.Consts import result, case_list
from common.runFailed import Retry


@Retry
class TestPayCreate(unittest.TestCase):
    """APP 背包开箱测试类"""

    @classmethod
    def setUpClass(cls) -> None:
        """测试前准备：设置用户大区"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()), bigarea_id=2)

    @classmethod
    def tearDownClass(cls) -> None:
        """测试后清理：恢复用户大区"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()))

    def test_01_openBoxPayChange(self, des: str = '背包开铜箱子场景', cid: int = 2):
        """
        铜箱子开启验证
        
        用例描述：
        验证背包内开箱子得到物品
        
        脚本步骤：
        1. 构造数据（更新 xs_user_money，xs_user_commodity，xs_user_box）
           * 清空用户背包内所有物品
           * 用户背包内插入箱子 (cid=2 铜箱子)
           * 修改用户指定箱子礼物刷新
           * 修改用户钱包余额
        2. openBox
        3. 校验接口状态和返回值数据
        4. 检查账户余额，预期值为：700 - 600 = 100
        5. 检查背包内开出物品，预期值应为：1（开出礼物个数*1 + 赠送头框*1）# 头像框被取消了
        
        Args:
            des: 测试描述
            cid: 物品 ID，默认 2（铜箱子）
        """
        # 1. 构造数据
        conMysql.deleteUserAccountSql('user_box', config.app_payUid)
        conMysql.deleteUserAccountSql('user_commodity', config.app_payUid)
        conMysql.insertXsUserCommodity(config.app_payUid, cid=cid, num=1)  # 背包插入 1 个铜箱子
        conMysql.insertXsUserBox(config.app_payUid)
        conMysql.updateMoneySql(config.app_payUid, money=400, money_cash=100, money_cash_b=100, money_b=100)
        
        # 2. 开箱
        data = encodeAppData(payType='shop-buy-box')
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查账户余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 100)
        
        # 5. 检查背包物品
        assert_equal(conMysql.selectUserInfoSql('sum_commodity', config.app_payUid), 1)
        
        case_list[des] = result

    def test_02_openMoreBoxPayChange(self, des: str = '背包箱子多开场景', cid: int = 3):
        """
        多箱子开启验证
        
        用例描述：
        验证背包内开箱子得到物品
        
        脚本步骤：
        1. 构造数据（更新 xs_user_money，xs_user_commodity，xs_user_box）
           * 清空用户背包内所有物品
           * 用户背包内插入多个箱子*6 2100*6=12600
           * 修改用户指定箱子礼物刷新
           * 修改用户钱包余额
        2. openBox
        3. 校验接口状态和返回值数据
        4. 检查账户余额，预期值为：13300 - 12600 = 700
        5. 检查背包内开出物品，预期值应为：6（开出礼物个数*6）
        
        Args:
            des: 测试描述
            cid: 物品 ID，默认 3（银箱子）
        """
        # 1. 构造数据
        conMysql.deleteUserAccountSql('user_box', config.app_payUid)
        conMysql.deleteUserAccountSql('user_commodity', config.app_payUid)
        conMysql.insertXsUserCommodity(config.app_payUid, cid=cid, num=6)  # 背包插入 6 个银箱子
        conMysql.insertXsUserBox(config.app_payUid)
        conMysql.updateMoneySql(config.app_payUid, money=700, money_cash=2000, money_cash_b=2000, money_b=2000)
        
        # 2. 多开箱子
        data = encodeAppData(payType='shop-buy-box-more')
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查账户余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 700)
        
        # 5. 检查背包物品
        assert_len(conMysql.selectUserInfoSql('sum_commodity', config.app_payUid), 6)
        
        case_list[des] = result
