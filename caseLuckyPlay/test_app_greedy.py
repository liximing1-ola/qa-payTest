#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APP 幸运玩法支付测试 - 摩天轮验证

验证摩天轮下注开奖流程。
"""
from common.conPtMysql import conMysql
import unittest
from common.Config import config
from common.Greedy import Greedy
from common.Assert import assert_equal
from common.Consts import case_list_c, result
import time
from common.conRedis import conRedis


class TestPayGreedy(unittest.TestCase):
    """APP 摩天轮测试类"""

    @classmethod
    def tearDownClass(cls) -> None:
        """测试后清理：恢复用户大区，清理 Redis 缓存"""
        conMysql.updateUserBigArea(tuple(i for i in config.app_user.values()))
        time.sleep(1)
        conRedis.delKey('User.Big.Area.Id', config.app_user.values())
        conRedis.delKey('User.Big.Area', config.app_user.values())

    def _prepare_test_data(self, setup_steps):
        """
        准备测试数据
        
        Args:
            setup_steps: 准备步骤列表
        """
        for step in setup_steps:
            action = step['action']
            params = step.get('params', {})
            if action == 'update_user_big_area':
                conMysql.updateUserBigArea(params['uids'], **{k: v for k, v in params.items() if k != 'uids'})
            elif action == 'update_user_language':
                conMysql.updateUserLanguage(params['uids'], **{k: v for k, v in params.items() if k != 'uids'})
            elif action == 'update_money':
                conMysql.updateMoneySql(**params)

    def _validate_calculation(self, check):
        """
        验证计算结果
        
        Args:
            check: 检查项字典
        """
        field = check['field']
        uid = check['uid']
        money_type = check.get('money_type')
        expected_calc = check['expected_calc']
        actual = conMysql.selectUserInfoSql(field, uid, money_type=money_type)
        assert_equal(actual, expected_calc)

    def test_01_greedy_bet(self):
        """
        华语区金豆下注验证
        
        用例描述：
        验证摩天轮下注开奖流程
        
        脚本步骤：
        1. 构造用户数据
        2. 用户下注金豆，等待开奖
        3. 检查账户金豆消耗
        4. 检查账户金豆余额：初始金豆 - 下注金豆 + 中奖金豆
        """
        des = '摩天轮下注开奖场景--华语区金豆'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_user_big_area', 'params': {'uids': tuple(i for i in config.app_user.values())}},
            {'action': 'update_user_language', 'params': {'uids': tuple(i for i in config.app_user.values())}},
            {'action': 'update_money', 'params': {'uid': config.app_payUid, 'gold_coin': 10000}}
        ])

        # 执行下注
        bet_data = Greedy.bet('gold_coin')

        # 验证数据库
        self._validate_calculation({
            'field': 'single_money',
            'uid': config.app_payUid,
            'money_type': 'gold_coin',
            'expected_calc': 10000 - bet_data[0] + bet_data[1]
        })

        case_list_c[des] = result

    def test_02_greedy_bet(self):
        """
        阿语区钻石下注验证
        
        用例描述：
        验证摩天轮下注开奖流程
        
        脚本步骤：
        1. 构造用户数据
        2. 用户下注钻石，等待开奖
        3. 检查账户钻石消耗
        4. 检查账户钻石余额：初始钻石 - 下注钻石 + 中奖钻石
        
        """
        des = '摩天轮下注开奖场景--阿语区钻石'

        # 准备测试数据
        self._prepare_test_data([
            {'action': 'update_user_big_area', 'params': {'uids': tuple(i for i in config.app_user.values()), 'bigArea_id': 3}},
            {'action': 'update_user_language', 'params': {'uids': tuple(i for i in config.app_user.values()), 'language': 'ar', 'area_code': 'AR'}},
            {'action': 'update_money', 'params': {'uid': config.app_payUid, 'money': 100000}}
        ])

        # 执行下注
        bet_data = Greedy.bet('diamond')

        # 验证数据库
        self._validate_calculation({
            'field': 'sum_money',
            'uid': config.app_payUid,
            'expected_calc': 100000 - bet_data[0] + bet_data[1]
        })

        case_list_c[des] = result
