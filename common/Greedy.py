#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
摩天轮API封装

提供摩天轮的下注和查询功能
"""
import time
import random
from common.Config import config
from common.Request import post_request_session
from common.conPtMysql import conMysql


# 配置常量
MAX_RETRY_COUNT = 10
RETRY_INTERVAL = 5
BET_COUNT = 6
VID_RANGE = (1, 8)


class Greedy:
    """摩天轮操作类"""

    @staticmethod
    def _build_url(endpoint, uid):
        """构建请求URL"""
        return f"{config.pt_host}{endpoint}?uid={uid}"

    @staticmethod
    def index(uid):
        """获取摩天轮玩法信息"""
        url = Greedy._build_url('greedy/index', uid)
        return post_request_session(url, None, token_name='pt')

    @staticmethod
    def stake(uid, vid, counter, round_id, money_type, notice=False):
        """下注"""
        url = Greedy._build_url('greedy/stake', uid)
        params = {
            'vid': vid,
            'counter': counter,
            'round_id': round_id,
            'money_type': money_type,
            'notice': notice
        }
        return post_request_session(url, params, token_name='pt')

    @staticmethod
    def _wait_for_state(uid, target_state='1'):
        """等待摩天轮进入指定状态"""
        for _ in range(MAX_RETRY_COUNT):
            result = Greedy.index(uid)
            data = result.get('body', {}).get('data', {})
            if data.get('state') == target_state:
                return data.get('round_id'), data.get('counter_range')
            time.sleep(RETRY_INTERVAL)
        return None, None

    @staticmethod
    def _wait_for_prize(uid, round_id):
        """等待开奖结果"""
        for _ in range(MAX_RETRY_COUNT):
            result = conMysql.select_greedy_prize(uid, round_id)
            if result != 0:
                return result[0], result[1]
            time.sleep(RETRY_INTERVAL)
        return 0, 0

    @staticmethod
    def bet(money_type):
        """
        执行下注流程
        
        Args:
            money_type: 货币类型
            
        Returns:
            list: [下注次数, 奖金]
        """
        try:
            # 等待可投注状态
            round_id, counter_range = Greedy._wait_for_state(config.pt_payUid)
            if not round_id:
                return [0, 0]

            # 执行下注
            for _ in range(BET_COUNT):
                vid = random.randint(*VID_RANGE)
                Greedy.stake(config.pt_payUid, vid, counter_range, round_id, money_type)

            # 等待开奖结果
            counter_all, prize = Greedy._wait_for_prize(config.pt_payUid, round_id)
            return [counter_all, prize]

        except Exception as e:
            print(f"Bet error: {e}")
            return [0, 0]
