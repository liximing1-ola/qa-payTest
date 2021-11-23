from common.Config import config
from common import Request
from common.params_Yaml import Yaml
from common.sqlScript import mysql
import unittest
from common import Consts
from common import Assert
from common.runFailed import Retry

@Retry(max_n=1)
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.pt_host + 'pay/create'

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
        des = '检查PT用户账户余额不足时，私聊一对一打赏场景'
        mysql.updateMoneySql(config.pt_payUid)
        mysql.updateMoneySql(config.pt_testUid)
        mysql.deleteXsBrokerUser(config.pt_testUid)  # 删除用户工会记录
        data = Yaml.read_yaml('Basic_pt.yml', 'pt_pay_chatGift')
        res = Request.pt_post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 0, reason)
        Assert.assert_body(res['body'], 'msg', '餘額不足，無法支付', reason)
        Assert.assert_equal(mysql.selectMoneySql(config.pt_testUid), 0)
        Consts.case_list[des] = 'pass'

    def test_02_ImPayChangeMoney(self):
        """
        用例描述：
        验证余额足够时，私聊一对一打赏,打赏分成满足师徒收益的基础上为：80:20
        步骤：
        1.清理打赏者和被打赏者数据 （更新xs_user_money）
        2.私聊一对一打赏(余额400分，打赏100分)
        3.校验【status code】和【body】状态
        4.检查被打赏者余额，预期为：80
        5.检查打赏者剩余余额，预期为：300
        """
        des = '检查PT用户账户余额足够时，一对一打赏的场景'
        mysql.updateMoneySql(config.pt_payUid, 100, 100, 100, 100)
        mysql.updateMoneySql(config.pt_testUid)
        data = Yaml.read_yaml('Basic_pt.yml', 'pt_pay_chatGift')
        res = Request.pt_post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(mysql.selectMoneySql(config.pt_testUid, 'money_cash'), 80)
        Assert.assert_equal(mysql.selectAllMoneySql(config.pt_payUid), 300)
        Consts.case_list[des] = 'pass'