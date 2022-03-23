import gevent
from gevent import monkey
monkey.patch_all()
from common.Config import config
from common.sqlScript import mysql
from Robot import robot
from common import Assert, Request, basicData, Consts, Logs, method, Session
from common.method import getValue
class TestPayConcurrent:
    # 内网支付接口
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'
    # 物品赠送接口
    commodity_present = config.dev_host + 'commodity/present?package=com.imbb.banban.android'
    # 物品使用接口
    commodity_use = config.dev_host + 'commodity/use?package=com.imbb.banban.android'

    @staticmethod
    def startPayCreateReady():
        """
        用例描述：
        构造背包内购买礼物场景
        脚本步骤：
        1.构造购买者数据 （更新xs_user_money和xs_user_commodity）
        2.商城内购买礼物道具*10（9900*1=9900）
        3.校验【status code】和返回值【body】状态
        4.检查购买者余额 (10000-9900=100)
        5.检查背包内物品
        """
        cid=340  # 小天使
        Session.Session().getSession('dev')
        mysql.updateMoneySql(config.payUid, 10000)
        mysql.deleteUserCommoditySql(config.payUid)
        data = basicData.encodeData(payType='shop-buy', cid=cid, money=9900, num=1)
        res = Request.post_request_session(url=TestPayConcurrent.pay_url, data=data)
        Assert.assert_code(res['code'], 200)
        Assert.assert_equal(mysql.selectAllMoneySql(config.payUid), 100)
        Assert.assert_equal(mysql.checkUserAllCommoditySql(config.payUid), 1)

    @staticmethod
    def payCreateConcurrent():
        """
        用例描述：
        验证商城购买的道具在房间内赠送给其他人
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.打赏背包道具 cid：340 * 1
        3.校验【status code】和返回值【body】状态
        4.检查背包内物品
        5.检查被打赏者余额 990*0.62 = 6138
        """
        bag_gift_cid = 340
        mysql.updateMoneySql(config.payUid)
        mysql.updateMoneySql(config.rewardUid)
        cid = int(mysql.getUserCommodityIdSql(bag_gift_cid, config.payUid))
        payload = 'platform=available&type=package&money=9900&params=%7B%22rid%22%3A193185484%2C%22uids%22%3A%22105002312%22%2C%22positions%22%3A%220%22%2C%22position%22%3A-1%2C%22giftId%22%3A54%2C%22giftNum%22%3A1%2C%22price%22%3A9900%2C%22cid%22%3A{}%2C%22ctype%22%3A%22gift%22%2C%22duction_money%22%3A0%2C%22version%22%3A2%2C%22num%22%3A1%2C%22gift_type%22%3A%22normal%22%2C%22star%22%3A0%2C%22refer%22%3A%22%E7%83%AD%E9%97%A8%3Aroom%22%2C%22useCoin%22%3A-1%7D'.format(cid)
        res = Request.post_request_session(url=TestPayConcurrent.pay_url, data=payload)
        Assert.assert_code(res['code'], 200)
        getValue(res)

    @staticmethod
    def endPayCreate():
        Assert.assert_equal(mysql.checkUserCommoditySql(config.payUid, 340), 0)
        Assert.assert_equal(mysql.selectAllMoneySql(config.rewardUid), 6138)
        Assert.assert_equal(Consts.success_num, 1)
        Consts.fail_num=0

    @staticmethod
    def test_01_payCreate(num_times):
        d = '并发打赏背包礼物的场景'
        TestPayConcurrent.startPayCreateReady()
        threads = []
        for i in range(num_times):
            thread = gevent.spawn(TestPayConcurrent.payCreateConcurrent)
            threads.append(thread)
        gevent.joinall(threads)
        TestPayConcurrent.endPayCreate()
        Consts.case_list_c[d] = Consts.result

    @staticmethod
    def startCommodityUseReady():
        """
        用例描述：
        使用商城购买的道具
        脚本步骤：
        1.构造使用者数据
        2.校验【status code】和返回值【body】状态
        3.检查背包内物品
        """
        mysql.updateMoneySql(config.payUid)
        mysql.deleteUserCommoditySql(config.payUid)
        mysql.insertXsUserCommodity(config.payUid, 264, 1)
        Assert.assert_equal(mysql.checkUserCommoditySql(config.payUid, 264), 1)

    @staticmethod
    def commodityUseConcurrent():
        cid = int(mysql.getUserCommodityIdSql(264, config.payUid))
        payload = 'id={}&num=1'.format(cid)
        res = Request.post_request_session(url=TestPayConcurrent.commodity_use, data=payload)
        Assert.assert_code(res['code'], 200)
        getValue(res)
        Assert.assert_equal(mysql.checkUserCommoditySql(config.payUid, 264), 0)

    @staticmethod
    def endCommodityUse(num_times):
        Assert.assert_equal(mysql.checkUserCommoditySql(config.payUid, 264), 0)
        Assert.assert_equal(Consts.fail_num, num_times - 1)
        Consts.success_num=0

    @staticmethod
    def test_02_commodityUse(num_times):
        d = '并发使用背包物品的场景'
        TestPayConcurrent.startCommodityUseReady()
        threads = []
        for i in range(num_times):
            thread = gevent.spawn(TestPayConcurrent.commodityUseConcurrent)
            threads.append(thread)
        gevent.joinall(threads)
        TestPayConcurrent.endCommodityUse(num_times)
        Consts.case_list_c[d] = Consts.result

    @staticmethod
    def startCommodityPresentReady():
        """
        用例描述：
        赠送商城购买的道具
        脚本步骤：
        1.构造使用者数据
        2.校验【status code】和返回值【body】状态
        3.检查背包内物品
        """
        mysql.updateMoneySql(config.payUid)
        mysql.updateMoneySql(config.rewardUid)
        mysql.deleteUserCommoditySql(config.payUid)
        mysql.deleteUserCommoditySql(config.rewardUid)
        mysql.insertXsUserCommodity(config.payUid, 263, 2)
        Assert.assert_equal(mysql.checkUserCommoditySql(config.payUid, 263), 2)

    @staticmethod
    def commodityPresentConcurrent():
        cid = int(mysql.getUserCommodityIdSql(263, config.payUid))
        payload = 'id={}&num=1&targetId={}'.format(cid, config.rewardUid)
        res = Request.post_request_session(url=TestPayConcurrent.commodity_present, data=payload)
        Assert.assert_code(res['code'], 200)
        getValue(res)

    @staticmethod
    def endCommodityPresent():
        Assert.assert_equal(mysql.checkUserCommoditySql(config.payUid, 263), 0)
        Assert.assert_equal(mysql.checkUserCommoditySql(config.rewardUid, 263), 2)
        Assert.assert_equal(Consts.success_num, 2)

    @staticmethod
    def test_03_commodityPresent(num_times):
        d = '并发赠送用户物品的场景'
        TestPayConcurrent.startCommodityPresentReady()
        threads = []
        for i in range(num_times):
            thread = gevent.spawn(TestPayConcurrent.commodityPresentConcurrent)
            threads.append(thread)
        gevent.joinall(threads)
        TestPayConcurrent.endCommodityPresent()
        Consts.case_list_c[d] = Consts.result

    @staticmethod
    def main(num):
        TestPayConcurrent.test_01_payCreate(num)
        # TestPayConcurrent.test_02_commodityUse(num)
        TestPayConcurrent.test_03_commodityPresent(num)
        case_list = method.dictToList(Consts.case_list_c)
        des = "{}\n".format(case_list)
        Logs.get_log('concurrentCaseResult.log').info(des)
        robot('markdown', des, bot='test')


if __name__=='__main__':
    TestPayConcurrent.main(10)