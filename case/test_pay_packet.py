from common.Config import config
from common import Request
from common.params_Yaml import Yaml
from common.sqlScript import Mysql
import unittest
from common import Consts, Assert
from common.runFailed import Retry
@Retry(max_n=2)
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

    def test_01_RoomPayRedPacket(self):
        """
        用例描述：
        验证房间发红包
        脚本步骤：
        1.构造发送者数据 （更新xs_user_money）
        2.红包类房间发送红包（发送520红包）
        3.校验【status code】和返回值【body】状态
        4.检查发送者余额，预期为：0
        """
        des = '检查房间红包发送红包的场景'
        Mysql.updateMoneySql(config.payUid, 52000)
        data = Yaml.read_yaml('Basic.yml', 'dev_red_packet')
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(Mysql.selectMoneySql(config.testUid), 0)
        Consts.CASE_LIST[des] = 'pass'