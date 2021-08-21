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

    @unittest.skip('pass')
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
        pass