from Common.config import config
from Common import Request
from Common.params_Yaml import Yaml
from Common.sqlScript import Mysql
import unittest
from Common import consts
from Common import Assert
from Common.runfailed import Retry

class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_package_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

    def test_01_centerMissionPayChange(self):
        """
        用例描述：
        验证任务中心购买豪华战令支持场景
        脚本步骤：
        1.构造购买者数据 （更新xs_user_money，xs_user_mission_credit）
        2.购买支付
        3.校验【status code】和返回值【body】状态
        4.检查账户余额
        5.检查开通状态
        """
        pass