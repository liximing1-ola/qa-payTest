from common.Config import config
from common.params_Yaml import Yaml
from common.sqlScript import Mysql
import unittest
from common import Assert, Request, Consts, basicData
from common.runFailed import Retry
@Retry(max_n=2)
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

    def test_01_IMPayNoMoney(self):
        """
        用例描述：
        检查账户余额不足时，私聊一对一打赏
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.私聊一对一打赏流程
        3.校验【status code】和返回值【body】状态
        4.检查预期返回msg，预期：支付失败，提示Toast
        5.检查被打赏者余额,预期：0
        """
        des = '私聊打赏余额不足的场景'
        Mysql.updateMoneySql(config.payUid)
        Mysql.updateMoneySql(config.testUid)
        Mysql.deleteXsBrokerUser(config.testUid)  # 删除用户工会记录
        Mysql.deleteXsChatroom(config.testUid)  # 删除用户商业房
        data = basicData.encodeData(payType='chat-gift', uid=config.testUid, money=1000, num=10, giftId=5)
        # data = Yaml.read_yaml('Basic.yml', 'dev_pay_chatGift')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 0, reason)
        Assert.assert_body(res['body'], 'msg', '余额不足，无法支付', reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.testUid), 0)
        Consts.CASE_LIST[des] = Consts.result