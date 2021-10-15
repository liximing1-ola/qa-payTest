import gevent
from common.Config import config
from common.sqlScript import Mysql
from common import Assert, Request, basicData
from gevent import monkey
monkey.patch_all()
class TestPayConcurrent:

    # 内网支付接口
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'
    # 物品赠送接口
    commodity_present = config.dev_host + 'commodity/present?package=com.imbb.banban.android'
    # 物品使用接口
    commodity_use = config.dev_host + 'commodity/use?package=com.imbb.banban.android'

    @staticmethod
    def shopBuyGift():
        """
        用例描述：
        验证商城购买道具
        脚本步骤：
        1.构造购买者数据 （更新xs_user_money和xs_user_commodity）
        2.商城内购买礼物道具*10 9900*1=9900
        3.校验【status code】和返回值【body】状态
        4.检查购买者余额 (10000-9900=100)
        5.检查背包内物品
        """
        cid=340  # 小天使
        des = '商城购买n个道具场景'
        Mysql.updateMoneySql(config.payUid, 10000)
        data = basicData.encodeData(payType='shop-buy', cid=340, money=9900, num=1)
        res = Request.post_request_session(url=TestPayConcurrent.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.payUid), 100)
        Assert.assert_equal(Mysql.checkUserCommoditySql(cid, config.payUid), 1)

    @staticmethod
    def shopGiftToUser():
        """
        用例描述：
        验证商城购买的道具在房间内赠送给其他人，他人收到的分成比在师徒收益上为 62：38
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.打赏背包道具 cid：340 * 1
        3.校验【status code】和返回值【body】状态
        4.检查背包内物品
        5.检查被打赏者余额 990*0.62 = 6138
        """
        des = '打赏背包内物品场景'
        bag_gift_cid = 340
        Mysql.updateMoneySql(config.payUid)
        Mysql.updateMoneySql(config.testUid)
        cid = int(Mysql.getUserCommodityIdSql(bag_gift_cid, config.payUid))
        payload = 'platform=available&type=package&money=9900&params=%7B%22rid%22%3A193185484%2C%22uids%22%3A%22105002312%22%2C%22positions%22%3A%220%22%2C%22position%22%3A-1%2C%22giftId%22%3A54%2C%22giftNum%22%3A1%2C%22price%22%3A9900%2C%22cid%22%3A{}%2C%22ctype%22%3A%22gift%22%2C%22duction_money%22%3A0%2C%22version%22%3A2%2C%22num%22%3A1%2C%22gift_type%22%3A%22normal%22%2C%22star%22%3A0%2C%22refer%22%3A%22%E7%83%AD%E9%97%A8%3Aroom%22%2C%22useCoin%22%3A-1%7D'.format(cid)
        res = Request.post_request_session(url=TestPayConcurrent.pay_url, data=payload)
        print(res)
        Assert.assert_code(res['code'], 200)
        Assert.assert_equal(Mysql.checkUserCommoditySql(bag_gift_cid, config.payUid), 0)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.testUid), 6138)


if __name__=='__main__':
    TestPayConcurrent.shopBuyGift()
    threads = []
    for i in range(10):
        thread = gevent.spawn(TestPayConcurrent.shopGiftToUser)
        threads.append(thread)

    gevent.joinall(threads)


