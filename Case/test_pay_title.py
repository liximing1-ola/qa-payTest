from Common.config import config
from Common import Request
from Common.params_Yaml import Yaml
from Common.sqlScript import mysqlScript
import unittest


class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_package_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

    def test_01_TitlePayChangeMoney(self):
        """
        用例描述：
        验证爵位开通及返钱到余额（money）
        脚本步骤：
        1.清空背包内物品，模拟开通者数据（更新xs_user_money）
        2.开通子爵
        3.校验【status code】和返回值【body】状态
        4.检查剩余钱值,预期值：（200000 - 100000 + 60000 = 160000）
        """
        mysqlScript.selectUserCommoditySql(103273407)
        mysqlScript.deleteUserTitleSql(103273407)
        mysqlScript.updateUserTitleSql(103273407)
        mysqlScript.updateMoneySql(200000, 0, 0, 0, 103273407)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_title')
        res = Request.post_request_session(url=TestPayCreate.pay_package_url, data=data)
        assert res['code'] == 200
        assert res['body']['success'] == 1
        assert len(res['body']['args']) > 1
        assert mysqlScript.selectMoneySql(105002660, 'money') == 160000


if __name__ == '__main__':
    pay = TestPayCreate()