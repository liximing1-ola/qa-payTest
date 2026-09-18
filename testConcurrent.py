import logging
from time import sleep

import gevent
from gevent import monkey

monkey.patch_all()

from common import Consts, Logs, method
from common.Assert import assert_equal, assert_code
from common.basicData import encodeData
from common.Config import config
from common.method import get_value
from common.Request import post_request_session
from common.Session import Session
from common.sqlScript import UserCommodityOperations, UserMoneyOperations
from Robot import robot

logger = logging.getLogger(__name__)

# 并发请求后等待数据落库的时长（秒），用于最终断言 success_num 前
CONCURRENT_SETTLE_WAIT = 1


class TestPayConcurrent:
    URLS = {
        'pay': config.appInfo.bb_dev + 'pay/create?package=',
        'present': config.appInfo.bb_dev + 'commodity/present?package=',
        'use': config.appInfo.bb_dev + 'commodity/use?package=',
    }
    CID = {'gift': 340, 'frame': 264}

    def __init__(self):
        Session.getSession('dev')

    def _run_concurrent(self, func, times):
        """执行并发测试"""
        gevent.joinall([gevent.spawn(func) for _ in range(times)])

    def _print(self, des, is_start=True):
        """打印测试信息"""
        sep = '-' * 40
        if is_start:
            logger.info(f"{sep}{des}{sep}")
        else:
            logger.info(sep * 3)

    def _finalize(self, des):
        """记录结果、重置计数器、打印结束分隔线"""
        Consts.case_list_c[des] = Consts.result
        Consts.success_num = 0
        Consts.fail_num = 0
        self._print(des, False)

    def _exec(self, url, data, check_code=200):
        """执行请求并校验"""
        res = post_request_session(url=url, data=data)
        assert_code(res['code'], check_code)
        get_value(res)
        return res

    def _run_test(self, des, times, setup, concurrent_fn, end, sleep_end=0):
        """并发测试通用模板：setup → concurrent → end → finalize

        使用 try-finally 确保 _finalize 始终执行（即使断言失败也重置计数器）。
        """
        self._print(des)
        try:
            setup()
            self._run_concurrent(concurrent_fn, times)
            if sleep_end:
                sleep(sleep_end)
            end()
        finally:
            self._finalize(des)

    # ========== Test 1: 打赏背包礼物 ==========
    def test_01_payPackGift(self, times, des='打赏背包礼物的并发场景'):
        """验证商城购买的道具在房间内赠送给其他人"""
        def setup():
            UserMoneyOperations.update(config.payUid, 10000)
            UserCommodityOperations.delete_all(config.payUid)
            self._exec(self.URLS['pay'], encodeData(payType='shop-buy', cid=self.CID['gift'], money=9900, num=1))
            assert_equal(UserMoneyOperations.select_all(config.payUid), 100)
            assert_equal(UserCommodityOperations.check_all(config.payUid), 1)

        def concurrent():
            cid = int(UserCommodityOperations.get_id(self.CID['gift'], config.payUid))
            payload = encodeData(payType='package', rid=193185484, uid=config.rewardUid, giftId=54, money=9900, package_cid=cid, ctype='gift', num=1)
            self._exec(self.URLS['pay'], payload)

        def end():
            assert_equal(UserCommodityOperations.check(config.payUid, self.CID['gift']), 0)
            assert_equal(Consts.success_num, 1)

        self._run_test(des, times, setup, concurrent, end, sleep_end=1)

    # ========== Test 2: 使用背包物品 ==========
    def test_02_commodityUse(self, times, des='使用背包内物料的并发场景'):
        """验证使用商城购买的道具"""
        def setup():
            UserCommodityOperations.insert(config.payUid, self.CID['frame'], 1)
            assert_equal(UserCommodityOperations.check(config.payUid, self.CID['frame']), 1)

        def concurrent():
            cid = int(UserCommodityOperations.get_id(self.CID['frame'], config.payUid))
            self._exec(self.URLS['use'], f'id={cid}&num=1')
            assert_equal(UserCommodityOperations.check(config.payUid, self.CID['frame']), 0)

        def end():
            assert_equal(Consts.fail_num, times - 1)

        self._run_test(des, times, setup, concurrent, end)

    # ========== Test 3: 赠送物品 ==========
    def test_03_commodityPresent(self, times, des='赠送物品时的并发场景'):
        """验证赠送商城购买的道具"""
        def setup():
            UserMoneyOperations.update(config.payUid)
            UserMoneyOperations.update(config.rewardUid)
            UserCommodityOperations.delete_all(config.payUid)
            UserCommodityOperations.delete_all(config.rewardUid)
            UserCommodityOperations.insert(config.payUid, self.CID['frame'], 2)
            assert_equal(UserCommodityOperations.check(config.payUid, self.CID['frame']), 2)

        def concurrent():
            cid = int(UserCommodityOperations.get_id(self.CID['frame'], config.payUid))
            self._exec(self.URLS['present'], f'id={cid}&num=1&targetId={config.rewardUid}')

        def end():
            assert_equal(UserCommodityOperations.check(config.payUid, self.CID['frame']), 0)
            assert_equal(UserCommodityOperations.check(config.rewardUid, self.CID['frame']), 2)
            assert_equal(Consts.success_num, 2)

        self._run_test(des, times, setup, concurrent, end)

    # ========== Test 4: 打赏面板礼物 ==========
    def test_04_payGift(self, times, des='打赏面板礼物时的并发场景'):
        """验证房间内打赏礼物给其他人"""
        def setup():
            UserMoneyOperations.update(config.payUid, 400)
            UserMoneyOperations.update(config.masterUid)

        def concurrent():
            payload = encodeData(payType='package', money=100, uid=config.masterUid, giftId=config.giftId['5'])
            self._exec(self.URLS['pay'], payload)

        def end():
            assert_equal(UserMoneyOperations.select_all(config.masterUid), 280)
            assert_equal(Consts.success_num, 4)

        self._run_test(des, times, setup, concurrent, end, sleep_end=1)

    # ========== Test 5: 购买商城礼物 ==========
    def test_05_payShop(self, times, des='购买商城礼物时的并发场景'):
        """验证商城购买道具"""
        def setup():
            UserMoneyOperations.update(config.payUid, 40000)
            UserCommodityOperations.delete_all(config.payUid)

        def concurrent():
            data = encodeData(payType='shop-buy', cid=self.CID['gift'], money=9900, num=1)
            self._exec(self.URLS['pay'], data)

        def end():
            assert_equal(UserMoneyOperations.select_all(config.payUid), 400)
            assert_equal(UserCommodityOperations.check_all(config.payUid), 4)
            sleep(CONCURRENT_SETTLE_WAIT)
            assert_equal(Consts.success_num, 4)

        self._run_test(des, times, setup, concurrent, end)

    def main(self, num):
        tests = [
            self.test_01_payPackGift,
            self.test_02_commodityUse,
            self.test_03_commodityPresent,
            self.test_04_payGift,
            self.test_05_payShop,
        ]
        for test in tests:
            test(num)
        case_list = method.dict_to_markdown(Consts.case_list_c)
        Logs.get_logger('concurrentCaseResult.log').info(f"{case_list}\n")
        robot('markdown', case_list)


if __name__ == '__main__':
    TestPayConcurrent().main(21)
