import gevent
from gevent import monkey

monkey.patch_all()
from common.Config import config
from common.sqlScript import mysql
from common import Consts, Logs, method
from common.basicData import encodeData
from common.method import get_value
from common.Session import Session
from Robot import robot
from common.Request import post_request_session
from common.Assert import assert_equal, assert_code
from time import sleep


class TestPayConcurrent:
    URLS = {
        'pay': config.appInfo['bb_dev'] + 'pay/create?package=',
        'present': config.appInfo['bb_dev'] + 'commodity/present?package=',
        'use': config.appInfo['bb_dev'] + 'commodity/use?package=',
    }
    CID = {'gift': 340, 'frame': 264}
    Session().getSession('dev')

    def _run_concurrent(self, func, times):
        """执行并发测试"""
        gevent.joinall([gevent.spawn(func) for _ in range(times)])

    def _print(self, des, is_start=True):
        """打印测试信息"""
        sep = '-' * 40
        print(f"{sep}{des}{sep}" if is_start else sep * 3)

    def _exec(self, url, data, check_code=200):
        """执行请求并校验"""
        res = post_request_session(url=url, data=data)
        assert_code(res['code'], check_code)
        get_value(res)
        return res

    # ========== Test 1: 打赏背包礼物 ==========
    def test_01_payPackGift(self, times, des='打赏背包礼物的并发场景'):
        """验证商城购买的道具在房间内赠送给其他人"""
        self._print(des)

        # Ready
        UserMoneyOperations.update(config.payUid, 10000)
        UserCommodityOperations.delete_all(config.payUid)
        self._exec(self.URLS['pay'], encodeData(payType='shop-buy', cid=self.CID['gift'], money=9900, num=1))
        assert_equal(UserMoneyOperations.select_all(config.payUid), 100)
        assert_equal(UserCommodityOperations.check_all(config.payUid), 1)

        # Concurrent
        def concurrent():
            cid = int(UserCommodityOperations.get_id(self.CID['gift'], config.payUid))
            payload = encodeData(payType='package', rid=193185484, uid=config.rewardUid, giftId=54, money=9900, package_cid=cid, ctype='gift', num=1)
            self._exec(self.URLS['pay'], payload)

        self._run_concurrent(concurrent, times)

        # End
        sleep(1)
        assert_equal(UserCommodityOperations.check(config.payUid, self.CID['gift']), 0)
        assert_equal(Consts.success_num, 1)
        Consts.fail_num = 0
        Consts.case_list_c[des] = Consts.result
        self._print(des, False)

    # ========== Test 2: 使用背包物品 ==========
    def test_02_commodityUse(self, times, des='使用背包内物料的并发场景'):
        """验证使用商城购买的道具"""
        self._print(des)

        # Ready
        UserCommodityOperations.insert(config.payUid, self.CID['frame'], 1)
        assert_equal(UserCommodityOperations.check(config.payUid, self.CID['frame']), 1)

        # Concurrent
        def concurrent():
            cid = int(UserCommodityOperations.get_id(self.CID['frame'], config.payUid))
            self._exec(self.URLS['use'], f'id={cid}&num=1')
            assert_equal(UserCommodityOperations.check(config.payUid, self.CID['frame']), 0)

        self._run_concurrent(concurrent, times)

        # End
        assert_equal(Consts.fail_num, times - 1)
        Consts.success_num = 0
        Consts.case_list_c[des] = Consts.result
        self._print(des, False)

    # ========== Test 3: 赠送物品 ==========
    def test_03_commodityPresent(self, times, des='赠送物品时的并发场景'):
        """验证赠送商城购买的道具"""
        self._print(des)

        # Ready
        UserMoneyOperations.update(config.payUid)
        UserMoneyOperations.update(config.rewardUid)
        UserCommodityOperations.delete_all(config.payUid)
        UserCommodityOperations.delete_all(config.rewardUid)
        UserCommodityOperations.insert(config.payUid, self.CID['frame'], 2)
        assert_equal(UserCommodityOperations.check(config.payUid, self.CID['frame']), 2)

        # Concurrent
        def concurrent():
            cid = int(UserCommodityOperations.get_id(self.CID['frame'], config.payUid))
            self._exec(self.URLS['present'], f'id={cid}&num=1&targetId={config.rewardUid}')

        self._run_concurrent(concurrent, times)

        # End
        assert_equal(UserCommodityOperations.check(config.payUid, self.CID['frame']), 0)
        assert_equal(UserCommodityOperations.check(config.rewardUid, self.CID['frame']), 2)
        assert_equal(Consts.success_num, 2)
        Consts.case_list_c[des] = Consts.result
        self._print(des, False)

    # ========== Test 4: 打赏面板礼物 ==========
    def test_04_payGift(self, times, des='打赏面板礼物时的并发场景'):
        """验证房间内打赏礼物给其他人"""
        self._print(des)

        # Ready
        Consts.success_num = 0
        UserMoneyOperations.update(config.payUid, 400)
        UserMoneyOperations.update(config.masterUid)

        # Concurrent
        def concurrent():
            payload = encodeData(payType='package', money=100, uid=config.masterUid, giftId=config.giftId['5'])
            self._exec(self.URLS['pay'], payload)

        self._run_concurrent(concurrent, times)

        # End
        sleep(1)
        assert_equal(UserMoneyOperations.select_all(config.masterUid), 280)
        assert_equal(Consts.success_num, 4)
        Consts.fail_num = 0
        Consts.case_list_c[des] = Consts.result
        self._print(des, False)

    # ========== Test 5: 购买商城礼物 ==========
    def test_05_payShop(self, times, des='购买商城礼物时的并发场景'):
        """验证商城购买道具"""
        self._print(des)

        # Ready
        Consts.success_num = 0
        UserMoneyOperations.update(config.payUid, 40000)
        UserCommodityOperations.delete_all(config.payUid)

        # Concurrent
        def concurrent():
            data = encodeData(payType='shop-buy', cid=self.CID['gift'], money=9900, num=1)
            self._exec(self.URLS['pay'], data)

        self._run_concurrent(concurrent, times)

        # End
        assert_equal(UserMoneyOperations.select_all(config.payUid), 400)
        assert_equal(UserCommodityOperations.check_all(config.payUid), 4)
        sleep(1)
        assert_equal(Consts.success_num, 4)
        Consts.fail_num = 0
        Consts.case_list_c[des] = Consts.result
        self._print(des, False)

    def main(self, num):
        self.test_01_payPackGift(num)
        # self.test_02_commodityUse(num)
        # self.test_03_commodityPresent(num)
        # self.test_04_payGift(num)
        # self.test_05_payShop(num)
        case_list = method.dict_to_markdown(Consts.case_list_c)
        Logs.get_logger('concurrentCaseResult.log').info(f"{case_list}\n")
        robot('markdown', str(case_list))


if __name__ == '__main__':
    TestPayConcurrent().main(21)
