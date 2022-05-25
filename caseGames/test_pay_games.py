from common.Config import config
from common.method import reason
from common.conMysql import conMysql
import unittest
from common import Consts, Assert, Request, basicData
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
        pass

    def test_02_gamesChatPayDivide_55(self):
        """
        用例描述：
        验证桌游私聊打赏分成比5:5
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.私聊一对一打赏（打赏1000分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额，预期为：500
        """
        pass
