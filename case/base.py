# coding=utf-8
"""
支付测试公共基类

提取 case/ 目录下各测试文件中重复的 _prepare_test_data / _validate_db_state
辅助方法，减少样板代码。
"""
import unittest

from common.Config import config
from common.Assert import assert_equal, assert_len
from common.conMysql import conMysql as mysql
from common.sqlScript import UserMoneyOperations, UserCommodityOperations


class PayTestBase(unittest.TestCase):
    """支付测试通用基类

    提供通用的数据准备和数据库验证方法，子类只需关注具体测试逻辑。
    """

    def _prepare_test_data(self, setup_steps):
        """准备测试数据（通用步骤分发器）

        支持的 action:
            update_money         → UserMoneyOperations.update(**params)
            clear_user_money     → mysql.updateUserMoneyClearSql(uid1, uid2?)
            clear_user_data      → mysql.updateUserMoneyClearSql(config.payUid, config.rewardUid)
            delete_user_account  → mysql.deleteUserAccountSql(table, uid)
            delete_account       → mysql.deleteUserAccountSql(table, uid)
            insert_commodity     → UserCommodityOperations.insert(**params)
            insert_user_box      → mysql.insertXsUserBox(uid, **params)
            check_user_broker    → mysql.checkUserBroker(uid, bid)
            check_uid_white      → mysql.check_uid_white(uid)
        """
        for step in setup_steps:
            action = step['action']
            params = step.get('params', {})
            if action == 'update_money':
                UserMoneyOperations.update(**params)
            elif action == 'clear_user_money':
                if 'uids' in step:
                    mysql.updateUserMoneyClearSql(*step['uids'])
                else:
                    mysql.updateUserMoneyClearSql(params['uid1'], params.get('uid2'))
            elif action == 'clear_user_data':
                if 'uids' in step:
                    mysql.updateUserMoneyClearSql(*step['uids'])
                else:
                    mysql.updateUserMoneyClearSql(config.payUid, config.rewardUid)
            elif action in ('delete_user_account', 'delete_account'):
                mysql.deleteUserAccountSql(
                    params.get('table', step.get('table')),
                    params.get('uid', step.get('uid')))
            elif action == 'delete_commodity':
                mysql.deleteUserAccountSql('user_commodity', step['uid'])
            elif action == 'insert_commodity':
                UserCommodityOperations.insert(**params)
            elif action == 'insert_user_box':
                uid = step.get('uid', config.payUid)
                mysql.insertXsUserBox(uid, **params)
            elif action == 'check_user_broker':
                mysql.checkUserBroker(**params) if params else mysql.checkUserBroker(step['uid'], bid=step['bid'])
            elif action == 'check_uid_white':
                mysql.check_uid_white(params['uid'])
            elif action == 'check_broker_rate':
                mysql.checkBrokerUserRate(**params)

    def _validate_db_state(self, checks):
        """验证数据库状态（通用检查分发器）

        每个 check 字典支持的 key:
            field      (必填) 查询字段
            uid        (可选) 用户 ID，默认 config.payUid
            expected   (可选) 期望值
            kwargs     (可选) 额外查询参数 dict
            money_type (可选) 货币类型
            cid        (可选) 渠道 ID
            min_value  (可选) 最小值断言（使用 assert_len）
            assert_func(可选) 自定义断言函数
        """
        for check in checks:
            field = check['field']
            uid = check.get('uid', config.payUid)
            expected = check.get('expected')

            kwargs = check.get('kwargs', {})
            if 'money_type' in check:
                kwargs.setdefault('money_type', check['money_type'])
            if 'cid' in check:
                kwargs.setdefault('cid', check['cid'])

            actual = mysql.selectUserInfoSql(field, uid, **kwargs)

            if 'min_value' in check:
                assert_len(actual, check['min_value'])
            elif 'assert_func' in check:
                check['assert_func'](actual, expected)
            else:
                assert_equal(actual, expected)
