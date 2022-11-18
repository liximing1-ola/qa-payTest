from common.Config import config
from common.method import reason
from common.conMysql import conMysql
import unittest
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_len, assert_equal
from common.basicData import encodeData
from common.Consts import result, case_list
from common.runFailed import Retry


@Retry
class TestPayCreate(unittest.TestCase):

    def test_01_openBoxPayChange(self, des='背包开箱子场景'):
        """
        用例描述：
        验证背包内开箱子得到物品
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
         * 清空用户背包内所有物品
         * 用户背包内插入箱子(cid=2 铜箱子)
         * 修改用户指定箱子礼物刷新
         * 修改用户钱包余额
        2.openBox
        3.校验接口状态和返回值数据
        4.检查账户余额，预期值为：700 - 600 = 100
        5.检查背包内开出物品，预期值应为：2（赠送头像框*1 + 开出礼物个数*1）
        """
        conMysql.deleteUserAccountSql('user_box', config.payUid)
        conMysql.deleteUserAccountSql('user_commodity', config.payUid)
        conMysql.insertXsUserCommodity(config.payUid, cid=2, num=1)  # 背包插入1个铜箱子
        conMysql.insertXsUserBox(config.payUid)
        conMysql.updateMoneySql(config.payUid, money=400, money_cash=100, money_cash_b=100, money_b=100)
        data = encodeData(payType='shop-buy-box',
                          money=600,
                          boxType='copper')
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 100)
        assert_equal(conMysql.selectUserInfoSql('sum_commodity', config.payUid), 2)
        case_list[des] = result

    def test_02_openMoreBoxPayChange(self, des='背包箱子多开场景'):
        """
        用例描述：
        验证背包内开箱子得到物品
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
            * 清空用户背包内所有物品
            * 用户背包内插入多个箱子*6 2100*6=12600
            * 修改用户指定箱子礼物刷新
            * 修改用户钱包余额
        2.openBox
        3.校验接口状态和返回值数据
        4.检查账户余额，预期值为：12600 - 2100*6 = 0
        5.检查背包内开出物品，预期值应为12（赠送头像框*6，开出礼物个数等于*6）
        """
        conMysql.deleteUserAccountSql('user_box', config.payUid)
        conMysql.deleteUserAccountSql('user_commodity', config.payUid)
        conMysql.insertXsUserCommodity(config.payUid, cid=3, num=6)  # 背包插入6个银箱子
        conMysql.insertXsUserBox(config.payUid, box_type='silver')
        conMysql.updateMoneySql(config.payUid, money=12600)
        data = encodeData(payType='shop-buy-box',
                          money=2100,
                          num=6,
                          cid=6,
                          boxType='silver')
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 0)
        assert_equal(conMysql.selectUserInfoSql('sum_commodity', config.payUid), 12)
        case_list[des] = result

    def test_03_giveBoxPayChange(self, des='房间送箱子场景'):
        """
        用例描述：
        验证房间内送箱子逻辑正常
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
        2.giveBox
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：700 - 600 = 100
        5.检查收箱用户账户余额，预期值为：大于100
        """
        conMysql.updateMoneySql(config.payUid, money=400, money_cash=100, money_cash_b=100, money_b=100)
        conMysql.updateMoneySql(config.rewardUid)
        data = encodeData(payType='package',
                          money=600,
                          rid=config.live_role['cp_link_rid'],  # 这个房间走的55分成,
                          giftId=config.giftId['46'],
                          star=4)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 100)
        assert_len(conMysql.selectUserInfoSql('sum_money', config.rewardUid), 300 * 0.42)
        case_list[des] = result

    def test_04_giveBoxMorePeople(self, des='房间送多人多个箱子场景'):
        """
        用例描述：
        验证房间内送箱子给多个人时逻辑正常
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
        2.giveBox
        3.校验接口状态和返回值数据
        4.检查账户余额，预期值为：10000 - 2100*2*2 = 1600
        5.检查收箱用户账户余额，预期值为：大于1000
        """
        conMysql.updateMoneySql(config.payUid, money=10000)
        conMysql.updateMoneySql(config.rewardUid)
        data = encodeData(payType='package-more',
                          num=2,
                          star=8,
                          money=2100,
                          giftId=config.giftId['47'])
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.payUid), 1600)
        assert_len(conMysql.selectUserInfoSql('sum_money', config.rewardUid), 1000)
        case_list[des] = result
