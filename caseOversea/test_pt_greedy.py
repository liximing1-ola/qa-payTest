#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @author: WuBingBing
from common.conPtMysql import conMysql
import unittest
from common.Config import config
from common.Greedy import Greedy
from common.Assert import assert_equal
from common.Consts import case_list, result
class TestPayCreate(unittest.TestCase):

    def test_01_greedy_bet(self, des='摩天轮下注开奖场景'):
        """
        用例描述：
        验证摩天轮下注开奖流程
        脚本步骤：
        1.构造用户数据
        2.用户下注，等待开奖
        3.检查账户金豆消耗
        4.检查账户金豆余额：初始金豆-下注金豆+中奖金豆
        """
        conMysql.updateMoneySql(config.pt_payUid, gold_coin=10000)
        bet_data = Greedy.bet()
        # 数据库中金豆余额
        gold_coin_balance = conMysql.selectUserInfoSql('single_money', config.pt_payUid, money_type='gold_coin')
        # 计算的金豆余额
        gold_coin_calculation = 10000 - bet_data[0] + bet_data[1]
        assert_equal(gold_coin_balance, gold_coin_calculation)
        case_list[des] = result

