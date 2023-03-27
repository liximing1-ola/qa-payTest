#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @author: WuBingBing
from common.conPtMysql import conMysql
import unittest
from common.Config import config
from common.Greedy import Greedy
from common.Assert import assert_equal
from common.Consts import case_list_c, result
import time
from common.conRedis import conRedis


class TestPayCreate(unittest.TestCase):

    @classmethod
    def tearDownClass(cls) -> None:
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()))
        time.sleep(1)
        conRedis.delKey('User.Big.Area.Id', config.pt_user.values())
        conRedis.delKey('User.Big.Area', config.pt_user.values())

    def test_01_greedy_bet(self, des='摩天轮下注开奖场景--华语区金豆'):
        """
        用例描述：
        验证摩天轮下注开奖流程
        脚本步骤：
        1.构造用户数据
        2.用户下注金豆，等待开奖
        3.检查账户金豆消耗
        4.检查账户金豆余额：初始金豆-下注金豆+中奖金豆
        """
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()))
        conMysql.updateUserLanguage(tuple(i for i in config.pt_user.values()))
        conMysql.updateMoneySql(config.pt_payUid, gold_coin=10000)
        bet_data = Greedy.bet('gold_coin')
        # 数据库中金豆余额
        gold_coin_balance = conMysql.selectUserInfoSql('single_money', config.pt_payUid, money_type='gold_coin')
        # 计算的金豆余额
        gold_coin_calculation = 10000 - bet_data[0] + bet_data[1]
        assert_equal(gold_coin_balance, gold_coin_calculation)
        case_list_c[des] = result

    def test_02_greedy_bet(self, des='摩天轮下注开奖场景--阿语区钻石'):
        """
        用例描述：
        验证摩天轮下注开奖流程
        脚本步骤：
        1.构造用户数据
        2.用户下注钻石，等待开奖
        3.检查账户钻石消耗
        4.检查账户钻石余额：初始钻石-下注钻石+中奖钻石
        """
        conMysql.updateUserBigArea(tuple(i for i in config.pt_user.values()), bigArea_id=3)
        conMysql.updateUserLanguage(tuple(i for i in config.pt_user.values()), language='ar', area_code='AR')
        conMysql.updateMoneySql(config.pt_payUid, money=100000)
        bet_data = Greedy.bet('diamond')
        # 数据库中钻石余额
        money_balance = conMysql.selectUserInfoSql('sum_money', config.pt_payUid)
        # 计算的钻石余额
        diamond_calculation = 100000 - bet_data[0] + bet_data[1]
        assert_equal(money_balance, diamond_calculation)
        case_list_c[des] = result
