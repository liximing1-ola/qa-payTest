from common.Config import config
from common.Request import post_request_session
from common.method import reason
from common.conMysql import conMysql
import unittest
import pytest
from common.Assert import assert_equal, assert_code, assert_body
from common.Consts import case_list, result
from common import basicData
@unittest.skip('购买爵位场景已下线')
class TestPayCreate(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_01_TitlePayChangeMoney(self, des='开通爵位场景'):
        """
        用例描述：
        验证爵位开通及返钱到余额（money）
        脚本步骤：
        1.清空背包内物品，模拟开通者数据
        2.开通子爵
        3.校验接口和返回值数据
        4.检查剩余钱值,预期值：（200000 - 100000 + 60000 = 160000）
        """
        conMysql.deleteUserAccountSql('user_commodity', config.payUid)
        conMysql.deleteUserAccountSql('user_title', config.payUid)
        conMysql.deleteUserAccountSql('user_profile', config.payUid)
        conMysql.deleteUserAccountSql('user_title_new', config.payUid)
        conMysql.updateMoneySql(config.payUid, money=200000)
        data = basicData.encodeData(payType='title', money=100000)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.payUid, money_type='money'), 160000)
        case_list[des] = result

    @pytest.mark.run(order=2)
    def test_02_TitlePayChangeRenew(self, des='爵位续费场景'):
        """
        用例描述：
        续01步骤，验证爵位续费及返钱到余额（money）
        脚本步骤：
        1.清空背包内物品，模拟开通者数据
        2.续费子爵
        3.校验接口状态和返回值数据
        4.检查剩余钱值,预期值：（200000 - 60000 + 36000 = 176000）
        """
        conMysql.updateMoneySql(config.payUid, money=200000)
        data = basicData.encodeData(payType='title', money=100000)
        res = post_request_session(config.pay_url, data)
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))
        assert_equal(conMysql.selectUserInfoSql('single_money', config.payUid, money_type='money'), 176000)
        case_list[des] = result