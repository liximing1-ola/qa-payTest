# coding=utf-8
"""
APP 海外版支付测试 - 星球之旅验证

验证星球之旅玩法的钻石扣除和礼物获取流程。
"""
import unittest
from common.Config import config
from common.method import format_reason
from common.conPtMysql import conMysql
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_equal
from common.basicData import encodeAppData
from common.Consts import result, case_list


@unittest.skip('修复')
class TestPayCreate(unittest.TestCase):
    """APP 星球之旅测试类"""

    def test_01_journey_planet(self, des: str = '星球之旅扣钻石获取礼物玩法'):
        """
        星球之旅玩法验证
        
        用例描述：
        验证钻石扣除正常，调用星球之旅正常，背包正常得到对应礼物
        
        脚本步骤：
        1. 构造数据（更新 xs_user_money，清空 xs_user_commodity，清空 xs_user_journey_planet_draw_record，xs_user_journey_planet_record）
           * 清空用户 money 数据
           * 清空用户背包内所有物品
           * 清空用户星球之旅玩法数据
           * 修改用户钱包余额 2000
        2. 请求星球之旅接口，校验接口状态和返回值数据
        3. 检查账户余额，预期值为：2000 - 1500= 500，一轮一关扣款 150 钻石
        4. 检查背包内下发物品，预期值应为 1（cid 物品得到 1 个）
        
        Args:
            des: 测试描述
        """
        # 1. 构造数据
        conMysql.deleteUserAccountSql('user_commodity', config.app_payUid)
        conMysql.deleteUserAccountSql('user_journey_planet_record', config.app_payUid)
        conMysql.deleteUserAccountSql('user_journey_planet_draw_record', config.app_payUid)
        conMysql.updateMoneySql(config.app_payUid, money=2000)
        
        # 2. 请求星球之旅
        data = encodeAppData(payType='journey_planet_draw')
        res = post_request_session(url=config.app_pay_url, data=data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查账户余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 500)
        
        # 5. 检查背包物品
        assert_equal(conMysql.selectUserInfoSql('sum_commodity', config.app_payUid), 1)
        
        case_list[des] = result
