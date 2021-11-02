from common.Config import config
from common import Request
from common.conMysql import conMysql
import unittest
import pytest
from common import Consts, Assert, basicData
from common.runFailed import Retry
@Retry
class TestPayCreate(unittest.TestCase):

    # 内网支付接口
    pay_url = config.dev_host + 'pay/create?package=com.imbb.banban.android'

    @unittest.skip('已下线')
    @pytest.mark.run(order=1)
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
        des = '开通爵位场景'
        conMysql.deleteUserAccountSql('user_commodity', config.payUid)
        conMysql.deleteUserAccountSql('user_title', config.payUid)
        conMysql.deleteUserAccountSql('user_profile', config.payUid)
        conMysql.deleteUserAccountSql('user_title_new', config.payUid)
        conMysql.updateMoneySql(config.payUid, 200000)
        data = basicData.encodeData(payType='title', money=100000)
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(conMysql.selectUserMoneySql('single_money', config.payUid, money_type='money'), 160000)
        Consts.CASE_LIST[des] = Consts.result

    @unittest.skip('已下线')
    @pytest.mark.run(order=2)
    def test_02_TitlePayChangeRenew(self):
        """
        用例描述：
        续01步骤，验证爵位续费及返钱到余额（money）
        脚本步骤：
        1.清空背包内物品，模拟开通者数据（更新xs_user_money）
        2.续费子爵
        3.校验【status code】和返回值【body】状态
        4.检查剩余钱值,预期值：（200000 - 60000 + 36000 = 176000）
        """
        des = '爵位续费场景'
        conMysql.updateMoneySql(config.payUid, 200000)
        data = basicData.encodeData(payType='title', money=100000)
        res = Request.post_request_session(url=TestPayCreate.pay_url, data=data)
        reason = 'Depiction: {},  failReason: {}'.format(des, res['body'])
        Assert.assert_code(res['code'], 200)
        Assert.assert_body(res['body'], 'success', 1, reason)
        Assert.assert_equal(conMysql.selectUserMoneySql('single_money', config.payUid, money_type='money'), 176000)
        Consts.CASE_LIST[des] = Consts.result