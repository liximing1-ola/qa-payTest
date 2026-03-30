# coding=utf-8
"""
APP 海外版支付测试 - VIP 人气值验证

验证房间打赏和私聊打赏赠送礼物时的人气值和 VIP 等级变化。
"""
import time
import unittest
from typing import Dict, Any

from common.Config import config
from common.conPtMysql import conMysql
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_len, assert_equal
from common.method import format_reason
from common.basicData import encodeAppData
from common.Consts import case_list, result
from common.runFailed import Retry


@Retry(max_n=3, func_prefix='test_01_payRoomgiftVip')
class TestPayCreate(unittest.TestCase):
    """APP 支付创建测试类"""

    @classmethod
    def setUpClass(cls) -> None:
        """测试前准备：检查礼物配置"""
        conMysql.checkXsGiftConfig()

    def test_01_payRoomgiftVip(self, des: str = '房间打赏礼物校验人气值&自身的 vip 等级'):
        """
        房间打赏礼物验证
        
        用例描述：
        验证房间打赏赠送 600 分=60 钻
        
        脚本步骤：
        1. 构造用户数据
        2. 房间内 A 打赏 B 礼物，礼物价值 60 钻石
        3. 校验接口状态和返回值数据
        4. 检查 A 账户 VIP 等级数据：pay_room_money 数据需要新增 600 有显示逻辑，显示取 1%
        5. 检查 B 账户数据库人气增加值：人气值需要增加最少数值：600，涉及加速体系
        
        备注：A、B 需要无贵族爵位关系等加速升级逻辑，vip 值 xs_user_profile，人气值 xs_user_popularity
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, money=600)
        conMysql.updateXsUserprofile_pay_room_money(config.app_payUid)
        conMysql.updateXsUserpopularity(config.app_testUid)
        
        # 2. 房间内打赏
        data = encodeAppData(payType='package')
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查 VIP 数据
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 0)
        assert_equal(conMysql.sqlXsUserprofile_pay_room_money(config.app_payUid), 600)
        
        # 5. 检查人气值
        time.sleep(2)  # 人气值需要 task 更新处理
        assert_len(conMysql.sqlXsUserpopularity(config.app_testUid), 600)
        
        case_list[des] = result

    def test_02_payChatgiftVip(self, des: str = '私聊打赏礼物校验人气值&自身的 vip 等级'):
        """
        私聊打赏礼物验证
        
        用例描述：
        验证私聊打赏赠送 600 分=60 钻
        
        脚本步骤：
        1. 构造用户数据
        2. 私聊界面内 A 打赏 B 礼物，礼物价值 60 钻石
        3. 校验接口状态和返回值数据
        4. 检查 B 账户数据库人气增加值：人气值需要最少增加数值：600，涉及加速体系
        5. 检查 A 账户 VIP 等级数据：pay_room_money 数据需要新增 600 有显示逻辑，显示取 1%
        
        备注：A、B 需要无贵族爵位关系等加速升级逻辑，vip 值 xs_user_profile，人气值 xs_user_popularity
        
        Args:
            des: 测试描述
        """
        # 1. 构造用户数据
        conMysql.updateMoneySql(config.app_payUid, money=600)
        conMysql.updateXsUserprofile_pay_room_money(config.app_payUid)
        conMysql.updateXsUserpopularity(config.app_testUid)
        
        # 2. 私聊打赏
        data = encodeAppData(payType='chat-gift')
        res = post_request_session(config.app_pay_url, data, token_name='app')
        
        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', 1, format_reason(des, res))
        
        # 4. 检查 VIP 数据
        assert_equal(conMysql.selectUserInfoSql('sum_money', config.app_payUid), 0)
        assert_equal(conMysql.sqlXsUserprofile_pay_room_money(config.app_payUid), 600)
        
        # 5. 检查人气值
        time.sleep(2)  # 人气值需要 task 更新处理
        assert_len(conMysql.sqlXsUserpopularity(config.app_testUid), 600)
        
        case_list[des] = result
