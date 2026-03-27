#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
摩天轮 API 封装

提供摩天轮的下注和查询功能
"""
import time
import random
from typing import Tuple, List, Optional
from common.Config import config
from common.Request import post_request_session
from common.conPtMysql import conMysql


# 配置常量
MAX_RETRY_COUNT: int = 10
RETRY_INTERVAL: int = 5
BET_COUNT: int = 6
VID_RANGE: Tuple[int, int] = (1, 8)


class Greedy:
    """摩天轮操作类"""

    @staticmethod
    def _build_url(endpoint: str, uid: int) -> str:
        """构建请求 URL
        
        Args:
            endpoint: API 端点
            uid: 用户 ID
            
        Returns:
            完整的 URL
        """
        return f"{config.app_host}{endpoint}?uid={uid}"

    @staticmethod
    def index(uid: int):
        """获取摩天轮玩法信息
        
        Args:
            uid: 用户 ID
            
        Returns:
            HTTP 响应对象
        """
        url = Greedy._build_url('greedy/index', uid)
        return post_request_session(url, None, token_name='app')

    @staticmethod
    def stake(uid: int, vid: int, counter: int, round_id: int, 
              money_type: str, notice: bool = False):
        """下注
        
        Args:
            uid: 用户 ID
            vid: 下注 ID
            counter: 计数器
            round_id: 回合 ID
            money_type: 货币类型
            notice: 是否通知
        """
        url = Greedy._build_url('greedy/stake', uid)
        params = {
            'vid': vid,
            'counter': counter,
            'round_id': round_id,
            'money_type': money_type,
            'notice': notice
        }
        return post_request_session(url, params, token_name='app')

    @staticmethod
    def _wait_for_state(uid: int, target_state: str = '1') -> Tuple[Optional[int], Optional[int]]:
        """等待摩天轮进入指定状态
        
        Args:
            uid: 用户 ID
            target_state: 目标状态
            
        Returns:
            (round_id, counter_range) 元组，失败返回 (None, None)
        """
        for _ in range(MAX_RETRY_COUNT):
            result = Greedy.index(uid)
            data = result.get('body', {}).get('data', {})
            if data.get('state') == target_state:
                return data.get('round_id'), data.get('counter_range')
            time.sleep(RETRY_INTERVAL)
        return None, None

    @staticmethod
    def _wait_for_prize(uid: int, round_id: int) -> Tuple[int, int]:
        """等待开奖结果
        
        Args:
            uid: 用户 ID
            round_id: 回合 ID
            
        Returns:
            (counter_all, prize) 元组
        """
        for _ in range(MAX_RETRY_COUNT):
            result = conMysql.select_greedy_prize(uid, round_id)
            if result != 0:
                return result[0], result[1]
            time.sleep(RETRY_INTERVAL)
        return 0, 0

    @staticmethod
    def bet(money_type: str) -> List[int]:
        """
        执行下注流程
        
        Args:
            money_type: 货币类型
            
        Returns:
            [下注次数，奖金]
        """
        try:
            # 等待可投注状态
            round_id, counter_range = Greedy._wait_for_state(config.app_payUid)
            if not round_id:
                return [0, 0]

            # 执行下注
            for _ in range(BET_COUNT):
                vid = random.randint(*VID_RANGE)
                Greedy.stake(config.app_payUid, vid, counter_range, round_id, money_type)

            # 等待开奖结果
            counter_all, prize = Greedy._wait_for_prize(config.app_payUid, round_id)
            return [counter_all, prize]

        except Exception as e:
            print(f"Bet error: {e}")
            return [0, 0]
