from common.Config import config
from common import Request
from common.params_Yaml import Yaml
from common.conMysql import conMysql
import unittest
from common import Consts, Assert
from common.runFailed import Retry
@Retry
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.dev_host + 'pay/create?package=com.who.android'

    def test_01_gamesRoomPayDivide_55(self):
        """
        用例描述：
        验证桌游房间一对一打赏分成比5:5
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.房间内一对一打赏
        3.校验【status code】和返回值【body】状态
        4.检查打赏者余额，预期：0
        5.检查被打赏者余额,预期：50
        """
        des = '房间1V1打赏分成比5:5'
        conMysql.updateMoneySql(config.games_payUid, 1000)
        conMysql.updateMoneySql(config.games_testUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_package_1')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 0, reason)
        Assert.assert_body(res['body'], 'msg', '余额不足，无法支付', reason)
        Assert.assert_equal(conMysql.selectUserMoneySql('sum_money', config.testUid), 0)
        Consts.GAME_LIST[des] = Consts.result

    def test_02_gamesChatPayDivide_55(self):
        """
        用例描述：
        验证余额足够时，非直播类型房间一对一打赏,打赏分成满足师徒收益的基础上为：62:38
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.房间内一对一打赏（打赏100分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额，预期为：62
        """
        des = '非直播1V1打赏场景'
        conMysql.updateMoneySql(config.payUid, 30, 30, 30, 10)
        conMysql.updateMoneySql(config.testUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_package_2')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data, tokenName='games')
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(conMysql.selectUserMoneySql('single_money', config.testUid), 62)
        Consts.CASE_LIST[des] = Consts.result