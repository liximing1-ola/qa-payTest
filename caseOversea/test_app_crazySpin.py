# coding=utf-8
"""
APP 海外版支付测试 - 疯狂转盘验证

验证疯狂转盘的购买券和抽奖功能。
"""
import unittest
from common.Config import config
from common.method import format_reason
from common.conPtMysql import conMysql
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_equal
from common.basicData import encodeAppData
from common.Consts import result, case_list
from common.runFailed import Retry
from common.Crazyspin import CrazySpin


@Retry
class TestPayCreate(unittest.TestCase):
    """APP 疯狂转盘测试类"""

    def test_01_crazySpinExchange(self, des: str = '扣除钻石购买欢乐转盘欢乐券'):
        """
        购买欢乐券验证
        
        用例描述：
        验证购买欢乐券，钻石扣除正常，背包正常得到欢乐券
        
        脚本步骤：
        1. 构造数据（更新 xs_user_money，xs_user_commodity）
           * 清空用户 money 数据
           * 清空用户背包内所有物品
           * 修改用户钱包余额 2000
        2. exchange crazy spin
        3. 校验接口状态和返回值数据
        4. 检查账户余额，预期值为：2000 - 10*100= 1000，一个欢乐券 10 钻石
        5. 检查背包内下发物品，预期值应为 10（cid=32 的物品得到 10 个）
        
        Args:
            des: 测试描述
        """
        # 1. 构造数据
        conMysql.deleteUserAccountSql('user_commodity', config.app_payUid)
        conMysql.updateMoneySql(config.app_payUid, money=2000)
        
        # 2. 购买欢乐券
        data = encodeAppData(payType='shop-buy-crazyspin')
        res = post_request_session(
            url=CrazySpin.spin_buy_url(uid=config.app_payUid),
            data=data,
            token_name='app'
        )
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查账户余额
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 1000)
        
        # 5. 检查背包物品
        assert_equal(conMysql.selectUserInfoSql('sum_commodity_32', config.app_payUid), 10)
        
        case_list[des] = result

    @unittest.skip('待补充 go 的接口服务')
    def test_02_playCrazySpin(self, des: str = '开启大转盘抽奖场景', cid: int = 32):
        """
        大转盘抽奖验证
        
        用例描述：
        验证玩大转盘，背包先正常扣券。以及背包得到新增物品
        
        脚本步骤：
        1. 构造数据（更新 xs_user_money，xs_user_commodity）
           * 清空用户背包内所有物品
           * 用户背包内插入抽奖券 (cid=32 欢乐券，cid=33，惊喜券)
           * 修改用户背包券数 (xs_user_commodity)
           * 打开大转盘面板数据正常，达到重置奖池的目的 /go/party/turntable/list
           * 大转盘跑马灯功能服务正常 /go/party/turntable/horn
        2. 扣除背包券来进行 play
        3. 校验接口状态和返回值数据
        4. 检查账户背包惊喜券/欢乐券余额，预期值为：100 - 10 = 90
        5. 检查背包内开出物品，预期值应为：10（开出礼物个数*10）
        
        Args:
            des: 测试描述
            cid: 物品 ID，默认 32（欢乐券）
        """
        # 1. 构造数据
        conMysql.deleteUserAccountSql('user_commodity', config.app_payUid)
        conMysql.insertXsUserCommodity(config.app_payUid, cid=cid, num=100)  # 背包插入 100 个欢乐券
        
        # TODO: 待补充后续逻辑
        case_list[des] = result
