from common.Config import config
from common.method import reason
from common.conPtMysql import conMysql
import unittest
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_equal
from common.basicData import encodePtData
from common.Consts import result, case_list
from common.Crazyspin import crazySpin
class TestPayCreate(unittest.TestCase):

    def test_01_crazySpinExchange(self, des='扣除钻石购买大转盘欢乐券'):
        """
        用例描述：
        验证购买欢乐券，钻石扣除正常，背包正常得到欢乐券
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity）
            * 清空用户money数据
            * 清空用户背包内所有物品
            * 修改用户钱包余额 2000
        2.exchange crazy spin
        3.校验接口状态和返回值数据
        4.检查账户余额，预期值为：2000 - 10*100= 1000,一个欢乐券10钻石
        5.检查背包内下发物品，预期值应为10（cid=32的物品得到10个）
        """
        conMysql.deleteUserAccountSql('user_commodity', config.pt_payUid)
        conMysql.updateMoneySql(config.pt_payUid, money=2000)
        data = encodePtData(payType='shop-buy-crazyspin')
        res = post_request_session(url=crazySpin.spinBuy(uid=config.pt_payUid), data=data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.pt_payUid), 1000)
        assert_equal(conMysql.selectUserInfoSql('sum_commodity_32', config.pt_payUid), 10)
        case_list[des] = result

    def test_02_playCrazySpin(self, des='开启大转盘抽奖场景'):
        """
        用例描述：
        验证玩大转盘，背包先正常扣券。以及背包得到新增物品
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity）
         * 清空用户背包内所有物品
         * 用户背包内插入抽奖券(cid=32 欢乐券，cid=33，惊喜券)
         * 修改用户背包券数(xs_user_commodity)
        2.play crazy spin
        3.校验接口状态和返回值数据
        4.检查账户背包惊喜券/欢乐券余额，预期值为：100 - 10 = 90
        5.检查背包内开出物品，预期值应为：10（开出礼物个数*10）
        """
        conMysql.deleteUserAccountSql('user_commodity', config.pt_payUid)
        conMysql.insertXsUserCommodity(config.pt_payUid, cid=32, num=100)  # 背包插入100个欢乐券
        data = encodePtData(payType='play-crazyspin')
        res = post_request_session(url=crazySpin.spinPlay(uid=config.pt_payUid), data=data, tokenName='pt')
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_commodity', config.pt_payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('sum_commodity_32', config.pt_payUid), 90)
        case_list[des] = result