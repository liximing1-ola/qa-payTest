import gevent
from gevent import monkey

monkey.patch_all()
from common.Config import config
from common.sqlScript import mysql
from common import Consts
from common.basicData import encodeData
from common.method import getValue
from common.Session import Session
from common.Request import post_request_session
from common.Assert import assert_equal, assert_code
from time import sleep


class TestPayConcurrent:
    php_urL = {
        'pay_url': config.appInfo['bb_dev'] + 'pay/create?package=com.imbb.banban.android',  # 内网支付接口
        'commodity_present': config.appInfo['bb_dev'] + 'commodity/present?package=com.imbb.banban.android',  # 物品赠送接口
        'commodity_use': config.appInfo['bb_dev'] + 'commodity/use?package=com.imbb.banban.android',  # 物品使用接口
    }
    commodity_id = {
        'cid_340': 340,  # 小天使
        'cid_264': 264,  # 头像框（5h）
    }
    Session().getSession('dev')

    def startPayCreateReady(self):
        """
        用例描述：
        构造背包内购买礼物场景
        脚本步骤：
        1.构造购买者数据 （更新xs_user_money和xs_user_commodity）
        2.商城内购买礼物道具*1（9900*1=9900）
        3.校验【status code】和返回值【body】状态
        4.检查购买者余额 (10000-9900=100)
        5.检查背包内物品
        """
        mysql.updateMoneySql(config.payUid, 10000)
        mysql.deleteUserCommoditySql(config.payUid)
        data = encodeData(payType='shop-buy',
                          cid=self.commodity_id['cid_340'],
                          money=9900,
                          num=1)
        res = post_request_session(url=self.php_urL['pay_url'], data=data)
        assert_code(res['code'], 200)
        assert_equal(mysql.selectAllMoneySql(config.payUid), 100)
        assert_equal(mysql.checkUserAllCommoditySql(config.payUid), 1)

    def payCreateConcurrent(self):
        """
        用例描述：
        验证商城购买的道具在房间内赠送给其他人
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.打赏背包道具
        3.校验【status code】和返回值【body】状态
        4.检查背包内物品
        5.检查被打赏者余额 9900*0.62 = 6138
        """
        cid = int(mysql.getUserCommodityIdSql(self.commodity_id['cid_340'], config.payUid))
        payload = encodeData(payType='package',
                             rid=193185484,
                             uid=config.rewardUid,
                             giftId=54,  # 小天使礼物
                             money=9900,
                             package_cid=cid,
                             ctype='gift',
                             num=1)
        res = post_request_session(url=self.php_urL['pay_url'], data=payload)
        assert_code(res['code'], 200)
        getValue(res)

    def endPayCreate(self):
        assert_equal(mysql.checkUserCommoditySql(config.payUid, self.commodity_id['cid_340']), 0)
        sleep(1)
        assert_equal(Consts.success_num, 1)
        Consts.fail_num = 0

    def test_01_payCreate(self, num_times, des='并发打赏背包礼物的场景'):
        print('----------------------------------------{}----------------------------------'.format(des))
        self.startPayCreateReady()
        threads = []
        for i in range(num_times):
            thread = gevent.spawn(self.payCreateConcurrent)
            threads.append(thread)
        gevent.joinall(threads)
        self.endPayCreate()
        Consts.case_list_c[des] = Consts.result
        print('-----------------------------------------------------------------------------------------')