from common.Config import config
from common.conMysql import conMysql as mysql
import unittest
from common.Request import post_request_session
from common.method import reason
from common.Assert import assert_code, assert_body, assert_len, assert_equal
from common.basicData import encodeData
from common.Consts import result, case_list
from common.runFailed import Retry


@Retry(max_n=3)
class TestPayOpenBox(unittest.TestCase):

    def _prepare_test_data(self, setup_steps):
        """准备测试数据"""
        for step in setup_steps:
            action = step['action']
            params = step.get('params', {})
            if action == 'delete_user_account':
                mysql.deleteUserAccountSql(params['table'], config.payUid)
            elif action == 'insert_commodity':
                mysql.insertXsUserCommodity(config.payUid, **params)
            elif action == 'insert_user_box':
                mysql.insertXsUserBox(config.payUid, **params)
            elif action == 'update_money':
                mysql.updateMoneySql(**params)

    def _validate_db_state(self, checks):
        """验证数据库状态"""
        for check in checks:
            field = check['field']
            uid = check.get('uid', config.payUid)
            expected = check['expected']
            if 'min_value' in check:
                assert_len(mysql.selectUserInfoSql(field, uid), check['min_value'])
            else:
                assert_equal(mysql.selectUserInfoSql(field, uid), expected)

    def test_01_openBoxPayChange(self):
        """
        用例描述：
        验证背包内开箱子得到物品
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
         * 清空用户背包内所有物品
         * 用户背包内插入箱子(cid=2 铜箱子)
         * 修改用户指定箱子礼物刷新
         * 修改用户钱包余额
        2.openBox
        3.校验接口状态和返回值数据
        4.检查账户余额，预期值为：700 - 600 = 100
        5.检查背包内开出物品，预期值应为：2（赠送头像框*1 + 开出礼物个数*1）
        """
        des = '背包开箱子场景'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'delete_user_account', 'params': {'table': 'user_box'}},
            {'action': 'delete_user_account', 'params': {'table': 'user_commodity'}},
            {'action': 'insert_commodity', 'params': {'cid': 2, 'num': 1}},
            {'action': 'insert_user_box', 'params': {}},
            {'action': 'update_money', 'params': {'money': 400, 'money_cash': 100, 'money_cash_b': 100, 'money_b': 100}}
        ])

        # 发送请求
        data = encodeData(payType='shop-buy-box', money=600, boxType='copper')
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'expected': 100},
            {'field': 'sum_commodity', 'expected': 2}
        ])

        case_list[des] = result

    def test_02_openMoreBoxPayChange(self):
        """
        用例描述：
        验证背包内开箱子得到物品
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
            * 清空用户背包内所有物品
            * 用户背包内插入多个箱子*6 2100*6=12600
            * 修改用户指定箱子礼物刷新
            * 修改用户钱包余额
        2.openBox
        3.校验接口状态和返回值数据
        4.检查账户余额，预期值为：12600 - 2100*6 = 0
        5.检查背包内开出物品，预期值应为12（赠送头像框*6，开出礼物个数等于*6）
        """
        des = '背包箱子多开场景'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'delete_user_account', 'params': {'table': 'user_box'}},
            {'action': 'delete_user_account', 'params': {'table': 'user_commodity'}},
            {'action': 'insert_commodity', 'params': {'cid': 3, 'num': 6}},
            {'action': 'insert_user_box', 'params': {'box_type': 'silver'}},
            {'action': 'update_money', 'params': {'money': 12600}}
        ])

        # 发送请求
        data = encodeData(payType='shop-buy-box', money=2100, num=6, cid=6, boxType='silver')
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'expected': 0},
            {'field': 'sum_commodity', 'expected': 12}
        ])

        case_list[des] = result

    def test_03_giveBoxPayChange(self):
        """
        用例描述：
        验证房间内送箱子逻辑正常
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
        2.giveBox
        3.校验接口状态和返回值数据
        4.检查打赏者账户余额，预期值为：700 - 600 = 100
        5.检查收箱用户账户余额，预期值为：大于186
        """
        des = '房间送箱子场景'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'money': 400, 'money_cash': 100, 'money_cash_b': 100, 'money_b': 100}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ])

        # 发送请求
        data = encodeData(money=600, giftId=config.giftId['46'], star=1)
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'expected': 100},
            {'field': 'sum_money', 'uid': config.rewardUid, 'min_value': 300 * 0.62}
        ])

        case_list[des] = result

    def test_04_giveBoxMorePeople(self):
        """
        用例描述：
        验证房间内送箱子给多个人时逻辑正常
        脚本步骤：
        1.构造数据（更新xs_user_money，xs_user_commodity，xs_user_box）
        2.giveBox
        3.校验接口状态和返回值数据
        4.检查账户余额，预期值为：10000 - 2100*2*2 = 1600
        5.检查收箱用户账户余额，预期值为：大于1000
        """
        des = '房间送多人多个箱子场景'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'money': 10000}},
            {'action': 'update_money', 'params': {'uid': config.rewardUid}}
        ])

        # 发送请求
        data = encodeData(payType='package-more', num=2, star=2, money=2100, giftId=config.giftId['47'])
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'expected': 1600},
            {'field': 'sum_money', 'uid': config.rewardUid, 'min_value': 1000}
        ])

        case_list[des] = result
