from common.Config import config
from common.conMysql import conMysql as mysql
from common.method import reason
import unittest
import pytest
from common.Request import post_request_session
from common.Assert import assert_body, assert_code, assert_equal, assert_len
from common.basicData import encodeData
from common.runFailed import Retry
from common.Consts import case_list_b, result


@Retry(max_n=3)
class TestPayUnionRoom(unittest.TestCase):

    singer_rid = mysql.selectUserInfoSql('union')
    pack_cal_uid = config.bb_user['pack_cal_uid']
    pack_ceo_uid = config.live_role['pack_ceo']

    def _prepare_test_data(self, setup_steps):
        """准备测试数据"""
        for step in setup_steps:
            action = step['action']
            params = step.get('params', {})
            if action == 'update_money':
                UserMoneyOperations.update(**params)
            elif action == 'clear_user_money':
                mysql.updateUserMoneyClearSql(params['uid1'], params.get('uid2'))

    def _validate_db_state(self, checks):
        """验证数据库状态"""
        for check in checks:
            field = check['field']
            uid = check.get('uid', config.payUid)
            expected = check['expected']
            money_type = check.get('money_type')
            if 'min_value' in check:
                assert_len(mysql.selectUserInfoSql(field, uid, money_type=money_type), check['min_value'])
            else:
                assert_equal(mysql.selectUserInfoSql(field, uid, money_type=money_type), expected)

    @pytest.mark.run(order=1)
    def test_01_singerRoomLiveBrokerRate_60(self):
        """
        用例描述：
        tdr：歌友房内，直播公会成员礼物打赏到账60%公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.歌友房打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.6 = 600(money_cash)
        5.检查公会长余额，预期：0
        """
        des = '歌友房直播工会收60%公会魅力值'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'clear_user_money', 'params': {'uid1': self.pack_cal_uid, 'uid2': self.pack_ceo_uid}}
        ])

        # 发送请求
        data = encodeData(payType='package', rid=self.singer_rid, uid=self.pack_cal_uid)
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': self.pack_cal_uid, 'money_type': 'money_cash', 'expected': 600},
            {'field': 'sum_money', 'uid': self.pack_cal_uid, 'expected': 600},
            {'field': 'sum_money', 'uid': self.pack_ceo_uid, 'expected': 0},
            {'field': 'sum_money', 'expected': 0}
        ])

        case_list_b[des] = result

    def test_02_singerRoomNormalBrokerRate_62(self):
        """
        用例描述：
        tdr：歌友房内，普通公会成员礼物打赏到账62%公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.歌友房打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.62 = 620(money_cash)
        """
        des = '歌友房普通工会收62%公会魅力值'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': config.gsUid}}
        ])

        # 发送请求
        data = encodeData(payType='package', rid=self.singer_rid, uid=config.gsUid)
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': config.gsUid, 'money_type': 'money_cash', 'expected': 1000 * config.rate},
            {'field': 'sum_money', 'uid': config.gsUid, 'expected': 1000 * config.rate},
            {'field': 'sum_money', 'expected': 0}
        ])

        case_list_b[des] = result

    def test_03_singerPayBoxNormalBrokerRate_62(self):
        """
        用例描述：
        tdr：歌友房内，普通公会成员箱子打赏到账62%公会魅力值
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.歌友房打赏（打赏铜箱子）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为不小于：300 * 0.62 = 620(money_cash)
        5.检查打赏者余额，预期为：600 - 600 = 0
        """
        des = '歌友房打赏箱子GS收62%（mc）'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 600}},
            {'action': 'update_money', 'params': {'uid': config.gsUid}}
        ])

        # 发送请求
        data = encodeData(payType='package', money=600, rid=self.singer_rid, giftId=config.giftId['46'], uid=config.gsUid, star=1)
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'expected': 0},
            {'field': 'single_money', 'uid': config.gsUid, 'money_type': 'money_cash', 'min_value': 300 * config.rate},
            {'field': 'sum_money', 'uid': config.gsUid, 'min_value': 300 * config.rate}
        ])

        case_list_b[des] = result

    def test_04_singerRoomPayNormalUser(self):
        """
        用例描述：
        tdr：歌友房内，非公会成员收到礼物打赏时收62%个人魅力值（师徒）
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.网赚房间一对一打赏（打赏1000分）
        3.校验接口状态和返回值数据
        4.检查被打赏者余额，预期为：1000 * 0.6 = 620(个人魅力值)
        """
        des = '歌友房普通用户礼物打赏收个人魅力值'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ])

        # 发送请求
        data = encodeData(rid=self.singer_rid)
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'single_money', 'uid': config.rewardUid, 'expected': 620},
            {'field': 'sum_money', 'uid': config.rewardUid, 'expected': 620},
            {'field': 'sum_money', 'expected': 0}
        ])

        case_list_b[des] = result
