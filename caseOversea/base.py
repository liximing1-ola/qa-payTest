# coding=utf-8
"""
海外版区域测试公共基类

提取 caseOversea/test_app_*.py 中重复的 setUpClass/tearDownClass
和通用导入；并通过 PayScene + run_scene 提供数据驱动的
区域消费差异化场景执行模板（构造余额 -> 发起打赏 -> 接口校验
-> 余额/对账校验 -> 记录结果）。
"""
import time
import unittest
from dataclasses import dataclass
from typing import Any, Dict, Optional

from common.Config import config
from common.conPtMysql import conMysql
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_len, assert_equal
from common.basicData import encodeOverseaData
from common.Consts import result, case_list

# 哨兵：房间 ID 取 setUpClass 中查询的 cls.area_rid（None 表示用 encodeOverseaData 默认房）
AREA_RID = object()

# 收礼人类型：非主播 / 公会主播
RECEIVER_NORMAL = 'normal'
RECEIVER_BROKER = 'broker'


@dataclass(frozen=True)
class PayScene:
    """海外版区域消费场景参数

    一个场景完整描述一次差异化分成验证的全部差异点，
    由 OverseaAreaTestBase.run_scene 统一执行。
    """

    # 用例描述（同时作为 case_list 报告键）
    des: str
    # 收礼人：RECEIVER_NORMAL 非主播(testUid) / RECEIVER_BROKER 公会主播(brokerUid)
    receiver: str = RECEIVER_NORMAL
    # 通道：'package' 房间打赏 / 'chat-gift' 私聊打赏
    pay_type: str = 'package'
    # 是否箱子打赏（幸运星 giftId['46']）
    is_box: bool = False
    # 房间 ID：AREA_RID 取 setUpClass 查询值；None 用 encodeOverseaData 默认房
    rid: Any = None
    # 打赏者初始 money
    payer_money: int = 700
    # 箱子场景：打赏者附加 money_cash/money_cash_b/money_b 各 100
    payer_box_extra: bool = False
    # 是否清空被打赏者钱包附加表（money_cash_personal）
    clear_extend: bool = False
    # 是否直接清空双方全部余额（余额不足场景）
    clear_all: bool = False
    # 响应 success 预期值
    success: int = 1
    # 响应 msg 预期值（None 跳过断言）
    msg: Optional[str] = None
    # 打赏者 sum_money 预期值（None 跳过断言）
    payer_expect: Optional[int] = 100
    # 被打赏者到账查询字段
    income_account: str = 'money_cash_personal'
    # 到账查询 money_type（None 不传该参数）
    income_money_type: Optional[str] = None
    # 到账预期值
    income_expect: int = 0
    # True 断言到账 >= income_expect（箱子开出物品最小值）；False 断言相等
    income_min: bool = False
    # 是否对账：到账字段 == pay_change 流水
    check_pay_change: bool = False
    # 对账查询字段（None 时同 income_account）
    reconcile_account: Optional[str] = None
    # 对账查询 money_type（None 时同 income_money_type）
    reconcile_money_type: Optional[str] = None


class OverseaAreaTestBase(unittest.TestCase):
    """海外版分区域测试基类

    子类通过类属性声明各自的差异：
        bigarea_id:               大区 ID（1=英语, 3=阿拉伯, 4=韩语, ...）
        room_type/room_rid/room_area:
                                  若 room_rid 非 None，setUpClass 中额外设置房间大区信息
        clear_redis_on_setup:     setUpClass 后清理大区 Redis 缓存
        clear_redis_on_teardown:  tearDownClass 时清理大区 Redis 缓存（含 0.3s 延迟）

    测试方法调用 self.run_scene(SCENES[n]) 执行模块级 SCENES 表中声明的场景。
    """

    bigarea_id: int = 1
    room_type: str = None
    room_rid = None
    room_area: str = None
    clear_redis_on_setup: bool = False
    clear_redis_on_teardown: bool = False

    @classmethod
    def _clear_area_redis(cls) -> None:
        """清理大区相关的 Redis 缓存（按需导入 conRedis，避免非 Redis 场景引入依赖）"""
        from common.conRedis import conRedis
        conRedis.delKey('User.Big.Area.Id', config.oversea_user.values(), host=config.redis_host_ali)
        conRedis.delKey('User.Big.Area', config.oversea_user.values(), host=config.redis_host_ali)

    @classmethod
    def setUpClass(cls) -> None:
        """测试前准备：设置用户大区（及可选的房间大区 / Redis 清理）"""
        conMysql.updateUserBigArea(*config.oversea_user.values(), bigarea_id=cls.bigarea_id)
        if cls.room_rid is not None:
            conMysql.updateUserRidInfoSql(cls.room_type, cls.room_rid, area=cls.room_area)
        if cls.clear_redis_on_setup:
            cls._clear_area_redis()

    @classmethod
    def tearDownClass(cls) -> None:
        """测试后清理：恢复用户大区（及可选的 Redis 清理）"""
        conMysql.updateUserBigArea(*config.oversea_user.values())
        if cls.clear_redis_on_teardown:
            time.sleep(0.3)
            cls._clear_area_redis()

    def run_scene(self, scene: PayScene) -> None:
        """执行单个区域消费差异化场景

        Args:
            scene: 场景参数
        """
        receiver_uid = (config.oversea_brokerUid if scene.receiver == RECEIVER_BROKER
                        else config.oversea_testUid)

        # 1. 构造用户数据
        if scene.clear_all:
            conMysql.updateUserMoneyClearSql(config.oversea_payUid, receiver_uid)
        else:
            if scene.payer_box_extra:
                conMysql.updateMoneySql(config.oversea_payUid, scene.payer_money,
                                        money_cash=100, money_cash_b=100, money_b=100)
            else:
                conMysql.updateMoneySql(config.oversea_payUid, scene.payer_money)
            conMysql.updateMoneySql(receiver_uid)
            if scene.clear_extend:
                conMysql.updateUserextendMoneyClearSql(receiver_uid)

        # 2. 发起打赏
        pay_kwargs: Dict[str, Any] = {}
        if scene.rid is AREA_RID:
            pay_kwargs['rid'] = self.area_rid
        elif scene.rid is not None:
            pay_kwargs['rid'] = scene.rid
        if scene.receiver == RECEIVER_BROKER:
            pay_kwargs['uid'] = receiver_uid
        if scene.is_box:
            pay_kwargs['giftId'] = config.giftId['46']
        data = encodeOverseaData(payType=scene.pay_type, **pay_kwargs)
        res = post_request_session(config.oversea_pay_url, data, token_name='app')

        # 3. 校验接口
        assert_code(res['code'])
        assert_body(res['body'], 'success', scene.success)
        if scene.msg is not None:
            assert_body(res['body'], 'msg', scene.msg)

        # 4. 检查余额
        if scene.payer_expect is not None:
            assert_equal(conMysql.selectUserInfoSql('sum_money', config.oversea_payUid), scene.payer_expect)
        income = self._query_account(receiver_uid, scene.income_account, scene.income_money_type)
        if scene.income_min:
            assert_len(income, scene.income_expect)
        else:
            assert_equal(income, scene.income_expect)
        if scene.check_pay_change:
            rec_account = scene.reconcile_account or scene.income_account
            rec_type = scene.income_money_type if scene.reconcile_money_type is None else scene.reconcile_money_type
            rec_value = self._query_account(receiver_uid, rec_account, rec_type)
            assert_equal(rec_value, conMysql.selectUserInfoSql(accountType='pay_change', uid=receiver_uid))

        # 5. 记录结果
        case_list[scene.des] = result

    @staticmethod
    def _query_account(uid: int, account: str, money_type: Optional[str]) -> int:
        """查询账户字段（money_type 为 None 时不传，保持与原调用一致）"""
        if money_type is None:
            return conMysql.selectUserInfoSql(account, uid)
        return conMysql.selectUserInfoSql(account, uid, money_type=money_type)
