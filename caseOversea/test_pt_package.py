from common.Config import config
from common import Request
from common.params_Yaml import Yaml
from common.sqlScriptOversea import Mysql
import unittest
from common import Consts, Assert
from common.runFailed import Retry

@Retry(max_n=2)
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.pt_host + 'pay/create'

    def test_01_RoomPayNoMoney(self):
        """
        用例描述：
        验证余额不足时，房间一对一打赏
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.房间内一对一打赏
        3.校验【status code】和返回值【body】状态
        4.检查预期返回msg，预期：支付失败
        5.检查被打赏者余额,预期：0
        """
        des = '检查账户余额不足时，房间内一对一打赏场景'
        Mysql.updateMoneySql(config.pt_payUid)
        Mysql.updateMoneySql(config.pt_testUid)
        data = Yaml.read_yaml('Basic_pt.yml', 'pt_package_room')
        res = Request.pt_post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 0, reason)
        Assert.assert_body(res['body'], 'msg', '餘額不足，無法支付', reason)
        Assert.assert_equal(Mysql.selectAllMoneySql(config.pt_testUid), 0)
        Consts.CASE_LIST[des] = 'pass'


    def test_02_RoomPayChangeMoney(self):
        """
        用例描述：
        验证余额足够时，非直播类型房间一对一打赏,打赏分成满足师徒收益的基础上为：70:30
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.房间内一对一打赏（打赏100分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额，预期为：62
        5.检查消费记录表消费money（xs_pay_change_new）
        6.检查消费记录表消费方式op
        """
        des = '检查非直播类型房间一对一打赏的场景'
        Mysql.updateMoneySql(config.pt_payUid, 30, 30, 30, 10)
        Mysql.updateMoneySql(config.pt_testUid)
        data = Yaml.read_yaml('Basic_pt.yml', 'pt_package_room')
        res = Request.pt_post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.pt_testUid), 70)
        Assert.assert_equal(Mysql.selectPayChangeSql(config.pt_payUid), 100)
        Assert.assert_equal(Mysql.selectPayChangeOpSql(config.pt_payUid), 'consume')
        Consts.CASE_LIST[des] = 'pass'