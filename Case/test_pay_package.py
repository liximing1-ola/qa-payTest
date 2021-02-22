from Common.config import config
from Common import Request
from Common.params_Yaml import Yaml
from Common.sqlScript import mysqlScript
import unittest


class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_package_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

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
        mysqlScript.updateMoneySql(0, 0, 0, 0, 103273407)
        mysqlScript.updateMoneySql(0, 0, 0, 0, 105002660)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_package_1')
        res = Request.post_request_session(url=TestPayCreate.pay_package_url, data=data)
        assert res['code'] == 200
        assert res['body']['success'] == 0
        assert res['body']['msg'] == '余额不足，无法支付'
        assert mysqlScript.selectMoneySql(105002660) == 1


    def test_02_RoomPayLiveMoney(self):
        """
        用例描述：
        验证余额足够时，直播类型房间（types=live）一对一打赏,打赏分成满足师徒收益的基础上为：52:48
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.直播类房间一对一打赏（打赏100分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额，预期为：52
        5.检查消费记录表消费money（xs_pay_change_new）
        6.检查消费记录表消费方式op
        """
        mysqlScript.updateMoneySql(30, 30, 30, 10, 103273407)
        mysqlScript.updateMoneySql(0, 0, 0, 0, 105002660)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_package_1')
        res = Request.post_request_session(url=TestPayCreate.pay_package_url, data=data)
        assert res['code'] == 200
        assert res['body']['success'] == 1
        assert res['body']['args']['money'] == 100
        assert mysqlScript.selectMoneySql(105002660) == 52
        assert mysqlScript.selectPayChangeSql(103273407) == 100
        assert mysqlScript.selectPayChangeOpSql(103273407) == 'consume'

    def test_03_RoomPayChangeMoney(self):
        """
        用例描述：
        验证余额足够时，非直播类型房间一对一打赏,打赏分成满足师徒收益的基础上为：62:38
        脚本步骤：
        1.构造打赏者和被打赏者数据 （更新xs_user_money）
        2.房间内一对一打赏（打赏100分）
        3.校验【status code】和返回值【body】状态
        4.检查被打赏者余额，预期为：62
        5.检查消费记录表消费money（xs_pay_change_new）
        6.检查消费记录表消费方式op
        """
        mysqlScript.updateMoneySql(30, 30, 30, 10, 103273407)
        mysqlScript.updateMoneySql(0, 0, 0, 0, 105002660)
        data = Yaml.read_yaml('Basic.yml', 'dev_pay_package_2')
        res = Request.post_request_session(url=TestPayCreate.pay_package_url, data=data)
        assert res['code'] == 200
        assert res['body']['success'] == 1
        assert len(res['body']['args']) > 1
        assert mysqlScript.selectMoneySql(105002660) == 62
        assert mysqlScript.selectPayChangeSql(103273407) == 100
        assert mysqlScript.selectPayChangeOpSql(103273407) == 'consume'


if __name__ == '__main__':
    pay = TestPayCreate()
    pay.test_01_RoomPayNoMoney()