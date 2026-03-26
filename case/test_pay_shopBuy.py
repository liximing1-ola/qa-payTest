from common.Config import config
from common.conMysql import conMysql as mysql
from common.method import reason
import unittest
import pytest
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_equal
from common.Consts import case_list, result
from common.basicData import encodeData
from common.runFailed import Retry


@Retry(max_n=3)
class TestPayShopBuy(unittest.TestCase):
    gift_cid = {
        'gift_329': 329,  # 礼物四叶草
        'gift_340': 340,  # 礼物小天使
    }

    def _prepare_test_data(self, setup_steps):
        """准备测试数据"""
        for step in setup_steps:
            action = step['action']
            params = step.get('params', {})
            if action == 'update_money':
                UserMoneyOperations.update(**params)
            elif action == 'delete_user_account':
                mysql.deleteUserAccountSql(params['table'], params['uid'])
            elif action == 'clear_user_money':
                mysql.updateUserMoneyClearSql(params['uid1'], params.get('uid2'))

    def _validate_db_state(self, checks):
        """验证数据库状态"""
        for check in checks:
            field = check['field']
            uid = check.get('uid', config.payUid)
            expected = check['expected']
            cid = check.get('cid')
            if cid:
                assert_equal(mysql.selectUserInfoSql(field, uid, cid=cid), expected)
            else:
                assert_equal(mysql.selectUserInfoSql(field, uid), expected)

    @pytest.mark.run(order=1)
    def test_01_shopPayChangeMoney(self):
        """
        用例描述：
        验证商城购买道具逻辑
        脚本步骤：
        1.构造购买者数据 （更新xs_user_money和xs_user_commodity）
        2.商城内购买礼物道具*1
        3.校验接口状态和返回值数据
        4.检查购买者余额 (200-100=100)
        5.检查背包内物品
        """
        des = '商城购买单个道具场景'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money_cash': 100, 'money_cash_b': 100}},
            {'action': 'delete_user_account', 'params': {'table': 'user_commodity', 'uid': config.payUid}}
        ])

        # 发送请求
        data = encodeData(payType='shop-buy', money=100, cid=self.gift_cid['gift_329'])
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'expected': 100},
            {'field': 'sum_commodity', 'expected': 1}
        ])

        case_list[des] = result

    @pytest.mark.run(order=2)
    def test_02_shopPayChangeBuyMore(self):
        """
        用例描述：
        验证商城购买多个道具场景
        脚本步骤：
        1.构造购买者数据 （更新xs_user_money和xs_user_commodity）
        2.商城内购买礼物道具*10 9900*10=99000 (cid:340是礼物小天使)
        3.校验接口状态和返回值数据
        4.检查购买者余额：103000-99000=4000
        5.检查背包内物品：10
        """
        des = '商城购买n个道具场景'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_money', 'params': {'uid': config.payUid, 'money': 1000, 'money_cash': 100000, 'money_cash_b': 1000, 'money_b': 1000}}
        ])

        # 发送请求
        data = encodeData(payType='shop-buy', cid=self.gift_cid['gift_340'], money=9900, num=10)
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'sum_money', 'expected': 4000},
            {'field': 'num_commodity', 'expected': 10, 'cid': self.gift_cid['gift_340']}
        ])

        case_list[des] = result

    @pytest.mark.run(order=3)
    def test_03_shopGiftToUser(self):
        """
        用例描述：
        验证商城购买的道具在房间内赠送给其他人，他人收到的分成比在师徒收益上为 62：38
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.打赏背包道具 cid：340 * 1
        3.校验接口状态和返回值数据
        4.检查背包内物品：10 - 1 = 9
        5.检查被打赏者余额：9900 * 0.62 = 6138
        """
        des = '打赏背包内物品场景'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'clear_user_money', 'params': {'uid1': config.payUid, 'uid2': config.rewardUid}}
        ])

        # 获取商品ID
        cid = int(mysql.selectUserInfoSql('id_commodity', config.payUid, cid=self.gift_cid['gift_340']))

        # 发送请求
        data = encodeData(rid=config.live_role['auto_rid'], giftId=config.giftId['54'], money=9900, package_cid=cid, ctype='gift')
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'num_commodity', 'expected': 9, 'cid': self.gift_cid['gift_340']},
            {'field': 'sum_money', 'uid': config.rewardUid, 'expected': 6138}
        ])

        case_list[des] = result

    @pytest.mark.run(order=4)
    def test_04_shopGiftToUserNoEnough(self):
        """
        用例描述：
        验证商城购买的道具赠送时不足的情况
        脚本步骤：
        1.构造打赏者和被打赏者数据
        2.打赏背包道具 cid：340 * 10
        3.校验接口状态和返回值数据
        4.检查背包内物品
        5.检查被打赏者余额 预期：0
        """
        des = '打赏背包物品但物品不足抵扣的场景'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'clear_user_money', 'params': {'uid1': config.payUid, 'uid2': config.rewardUid}}
        ])

        # 获取商品ID
        cid = int(mysql.selectUserInfoSql('id_commodity', config.payUid, cid=self.gift_cid['gift_340']))

        # 发送请求
        data = encodeData(rid=config.live_role['auto_rid'], giftId=config.giftId['54'], money=99000, package_cid=cid, ctype='gift', num=10)
        res = post_request_session(config.pay_url, data)

        # 验证响应
        assert_code(res['code'])
        assert_body(res['body'], 'success', 0, format_reason(des, res))
        assert_body(res['body'], 'msg', '余额不足，无法支付', format_reason(des, res))

        # 验证数据库
        self._validate_db_state([
            {'field': 'num_commodity', 'expected': 9, 'cid': self.gift_cid['gift_340']},
            {'field': 'sum_money', 'uid': config.rewardUid, 'expected': 0}
        ])

        case_list[des] = result
