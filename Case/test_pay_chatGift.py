from Common.config import config
from Common import Request
from Common.params_Yaml import Yaml
from Common.sqlScript import mysqlScript
import unittest


class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_package_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

    def test_01_IMPayNoMoney(self):
        """
        用例描述：
        验证余额不足时，私聊一对一打赏
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.私聊一对一打赏
        3.校验【status code】和返回值【body】状态
        4.检查预期返回msg，预期：支付失败
        5.检查被打赏者余额,预期：0
        """
        mysqlScript.updateMoneySql(0, 0, 0, 0, config.payUid)
        mysqlScript.updateMoneySql(0, 0, 0, 0, config.testUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_chatGift')
        res = Request.post_request_session(url=TestPayCreate.pay_package_url, data=data)
        assert res['code'] == 200
        assert res['body']['success'] == 0
        assert res['body']['msg'] == '余额不足，无法支付'
        assert mysqlScript.selectMoneySql(config.testUid) == 0

    def test_02_ImPayChangeMoney(self):
        """
        用例描述：
        验证余额足够时，私聊一对一打赏,打赏分成满足师徒收益的基础上为：72:28
        步骤：
        1.清理打赏者和被打赏者数据 （更新xs_user_money）
        2.私聊一对一打赏(余额1400分，打赏1000分)
        3.校验【status code】和【body】状态
        4.检查被打赏者余额，预期为：720
        5.检查打赏者剩余余额，预期为：400
        """
        mysqlScript.updateMoneySql(1100, 100, 100, 100, config.payUid)
        mysqlScript.updateMoneySql(0, 0, 0, 0, config.testUid)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_chatGift')
        res = Request.post_request_session(url=TestPayCreate.pay_package_url, data=data)
        assert res['code'] == 200
        assert res['body']['success'] == 1
        assert len(res['body']['args']) > 1
        assert mysqlScript.selectMoneySql(config.testUid) == 720
        assert mysqlScript.selectAllMoneySql(config.payUid) == 400


if __name__ == '__main__':
    pay = TestPayCreate()
    pay.test_01_IMPayNoMoney()
    #pay.test_02_ImPayChangeMoney()