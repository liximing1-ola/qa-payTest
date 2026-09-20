# coding=utf-8
"""
海外版测试公共基类

OverseaTestBase 承载全部海外版用例的公共前置处理（礼物配置检查/
用户大区/房间大区/Redis 缓存清理），其下两个场景模型分支：

- OverseaAreaTestBase + PayScene + run_scene：区域消费差异化场景
  （构造余额 -> 发起打赏 -> 接口校验 -> 余额/对账校验 -> 记录结果）；
- OverseaBizTestBase + OverseaBizCase + run_case：通用支付业务场景
  （金豆兑换/商城购买/开箱/盲盒/私聊打赏/守护/人气值等）。

七段式执行骨架由 common/scene_base.py 的 SceneFlowBase 编排。
"""
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from common.Config import config
from common.conPtMysql import conMysql
from common.Request import post_request_session
from common.Assert import assert_code, assert_body, assert_len, assert_equal
from common.basicData import encodeOverseaData
from common.Consts import result, case_list
from common.scene_base import SceneFlowBase, resolve

# 哨兵：房间 ID 取 setUpClass 中查询的 cls.area_rid（None 表示用 encodeOverseaData 默认房）
AREA_RID = object()

# 收礼人类型：非主播 / 公会主播
RECEIVER_NORMAL = 'normal'
RECEIVER_BROKER = 'broker'

# 等待 DB 写入传播后再清 Redis 缓存（秒）
REDIS_CLEAR_WAIT = 0.3


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


class OverseaTestBase(SceneFlowBase):
    """海外版测试公共基类：公共前置处理（礼物配置检查/用户大区/房间大区/Redis 清理）

    子类通过类属性声明各自的前置行为：
        check_gift_config:        setUpClass 检查礼物配置（checkXsGiftConfig）
        bigarea_id:               用户大区 ID（None 不设置大区，通用业务场景默认）
        room_type/room_rid/room_area:
                                  bigarea_id 与 room_rid 均非 None 时设置房间大区信息
        clear_redis_on_setup:     setUpClass 后清理大区 Redis 缓存
        clear_redis_on_teardown:  tearDownClass 时清理大区 Redis 缓存（含 0.3s 延迟）
    """

    check_gift_config: bool = False
    bigarea_id: Optional[int] = None
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
        """测试前准备：检查礼物配置、设置用户大区（及可选的房间大区/Redis 清理）"""
        if cls.check_gift_config:
            conMysql.checkXsGiftConfig()
        if cls.bigarea_id is not None:
            conMysql.updateUserBigArea(*config.oversea_user.values(), bigarea_id=cls.bigarea_id)
            if cls.room_rid is not None:
                conMysql.updateUserRidInfoSql(cls.room_type, cls.room_rid, area=cls.room_area)
            if cls.clear_redis_on_setup:
                cls._clear_area_redis()

    @classmethod
    def tearDownClass(cls) -> None:
        """测试后清理：恢复用户大区（及可选的 Redis 清理）"""
        if cls.bigarea_id is not None:
            conMysql.updateUserBigArea(*config.oversea_user.values())
            if cls.clear_redis_on_teardown:
                time.sleep(REDIS_CLEAR_WAIT)
                cls._clear_area_redis()


class OverseaAreaTestBase(OverseaTestBase):
    """海外版分区域测试基类

    子类通过类属性声明各自的差异：
        bigarea_id:               大区 ID（1=英语, 3=阿拉伯, 4=韩语, ...，默认 1）
        room_type/room_rid/room_area:
                                  若 room_rid 非 None，setUpClass 中额外设置房间大区信息
        clear_redis_on_setup:     setUpClass 后清理大区 Redis 缓存
        clear_redis_on_teardown:  tearDownClass 时清理大区 Redis 缓存（含 0.3s 延迟）

    测试方法调用 self.run_scene(SCENES[n]) 执行模块级 SCENES 表中声明的场景。
    """

    bigarea_id: int = 1

    def run_scene(self, scene: PayScene) -> None:
        """执行单个区域消费差异化场景

        Args:
            scene: 场景参数
        """
        self.run_flow(scene)

    # ============ 场景骨架钩子实现 ============
    def flow_prepare(self, scene: PayScene, ctx: Dict[str, Any]) -> None:
        """准备：构造用户数据（receiver_uid 存入 ctx 供后续阶段使用）"""
        receiver_uid = (config.oversea_brokerUid if scene.receiver == RECEIVER_BROKER
                        else config.oversea_testUid)
        ctx['receiver_uid'] = receiver_uid

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

    def flow_request(self, scene: PayScene, ctx: Dict[str, Any]) -> None:
        """请求：发起打赏（响应存入 ctx['_res'] 供断言阶段使用）"""
        pay_kwargs: Dict[str, Any] = {}
        if scene.rid is AREA_RID:
            pay_kwargs['rid'] = self.area_rid
        elif scene.rid is not None:
            pay_kwargs['rid'] = scene.rid
        if scene.receiver == RECEIVER_BROKER:
            pay_kwargs['uid'] = ctx['receiver_uid']
        if scene.is_box:
            pay_kwargs['giftId'] = config.giftId['46']
        data = encodeOverseaData(payType=scene.pay_type, **pay_kwargs)
        ctx['_res'] = post_request_session(config.oversea_pay_url, data, token_name='app')

    def flow_assert(self, scene: PayScene, ctx: Dict[str, Any]) -> None:
        """断言：校验接口响应"""
        res = ctx['_res']
        assert_code(res['code'])
        assert_body(res['body'], 'success', scene.success)
        if scene.msg is not None:
            assert_body(res['body'], 'msg', scene.msg)

    def flow_validate(self, scene: PayScene, ctx: Dict[str, Any]) -> None:
        """校验：检查余额与对账"""
        receiver_uid = ctx['receiver_uid']
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

    def flow_record(self, scene: PayScene, ctx: Dict[str, Any]) -> None:
        """记录：写入报告表"""
        case_list[scene.des] = result

    @staticmethod
    def _query_account(uid: int, account: str, money_type: Optional[str]) -> int:
        """查询账户字段（money_type 为 None 时不传，保持与原调用一致）"""
        if money_type is None:
            return conMysql.selectUserInfoSql(account, uid)
        return conMysql.selectUserInfoSql(account, uid, money_type=money_type)


# ============ 通用支付业务场景（非区域消费） ============

@dataclass(frozen=True)
class OverseaBizCase:
    """海外版通用支付业务场景参数

    一个场景完整描述一次海外版支付业务验证（金豆兑换/商城购买/开箱/
    盲盒/私聊打赏/守护/人气值等）的全部差异点，由 OverseaBizTestBase.run_case
    统一执行。
    """

    # 用例描述（同时作为 case_list 报告键）
    des: str
    # 数据准备步骤（_prepare_test_data 分发格式）
    setup: list = field(default_factory=list)
    # encodeOverseaData 参数（只声明与默认值的差异）；值可为 callable(ctx) 在运行期求值
    data: Dict[str, Any] = field(default_factory=dict)
    # 请求地址（None 时用 config.oversea_pay_url）
    url: Optional[str] = None
    # 响应 success 预期值（失败场景为 0）
    success: int = 1
    # 响应 msg 预期值（None 时跳过断言）
    msg: Optional[str] = None
    # 请求后等待秒数（等待异步数据落库）
    post_wait: float = 0
    # DB 校验项（_validate_db_state 格式）
    checks: list = field(default_factory=list)


# 非 selectUserInfoSql 通用字段的特殊查询（check 字典 field 名 -> 查询函数）
EXTRA_QUERY_MAP = {
    'pay_room_money': conMysql.sqlXsUserprofile_pay_room_money,
    'popularity': conMysql.sqlXsUserpopularity,
}


class OverseaBizTestBase(OverseaTestBase):
    """海外版通用支付业务测试基类（非区域消费场景）

    子类在模块级场景表中声明各场景的差异点，test 方法调用 run_case 执行。
    前置行为（礼物配置检查/大区设置等）由 OverseaTestBase 提供。
    """

    def run_case(self, case: OverseaBizCase) -> None:
        """执行单个海外版通用支付业务场景

        Args:
            case: 场景参数（模块级场景表中声明）
        """
        self.run_flow(case)

    # ============ 场景骨架钩子实现 ============
    def flow_prepare(self, case: OverseaBizCase, ctx: Dict[str, Any]) -> None:
        """1. 准备测试数据"""
        if case.setup:
            self._prepare_test_data(case.setup)

    def flow_request(self, case: OverseaBizCase, ctx: Dict[str, Any]) -> None:
        """3. 发起支付请求（默认走 config.oversea_pay_url，token=app）"""
        data = encodeOverseaData(**{key: resolve(value, ctx) for key, value in case.data.items()})
        url = case.url if case.url is not None else config.oversea_pay_url
        ctx['_res'] = post_request_session(url, data, token_name='app')

    def flow_assert(self, case: OverseaBizCase, ctx: Dict[str, Any]) -> None:
        """4. 响应断言"""
        res = ctx['_res']
        assert_code(res['code'])
        assert_body(res['body'], 'success', case.success)
        if case.msg is not None:
            assert_body(res['body'], 'msg', case.msg)

    def flow_wait(self, case: OverseaBizCase, ctx: Dict[str, Any]) -> None:
        """5. 等待异步数据落库"""
        if case.post_wait:
            time.sleep(case.post_wait)

    def flow_validate(self, case: OverseaBizCase, ctx: Dict[str, Any]) -> None:
        """6. DB 校验"""
        if case.checks:
            self._validate_db_state(case.checks)

    def flow_record(self, case: OverseaBizCase, ctx: Dict[str, Any]) -> None:
        """7. 记录结果"""
        case_list[case.des] = result

    def _prepare_test_data(self, setup_steps):
        """准备测试数据（海外版通用业务步骤分发器）

        支持的 action:
            update_money         → conMysql.updateMoneySql(**params)
            clear_money          → conMysql.updateUserMoneyClearSql(*params['uids'])
            delete_user_account  → conMysql.deleteUserAccountSql(table, uid)
            insert_commodity     → conMysql.insertXsUserCommodity(uid, cid, num)
            insert_box           → conMysql.insertXsUserBox(uid)
            clear_extend_money   → conMysql.updateUserextendMoneyClearSql(uid)
            clear_pay_room_money → conMysql.updateXsUserprofile_pay_room_money(uid)
            clear_popularity     → conMysql.updateXsUserpopularity(uid)
        """
        for step in setup_steps:
            action = step['action']
            params = step.get('params', {})
            if action == 'update_money':
                conMysql.updateMoneySql(**params)
            elif action == 'clear_money':
                conMysql.updateUserMoneyClearSql(*params['uids'])
            elif action == 'delete_user_account':
                conMysql.deleteUserAccountSql(params['table'], params['uid'])
            elif action == 'insert_commodity':
                conMysql.insertXsUserCommodity(params['uid'], params['cid'], params['num'])
            elif action == 'insert_box':
                conMysql.insertXsUserBox(params['uid'])
            elif action == 'clear_extend_money':
                conMysql.updateUserextendMoneyClearSql(params['uid'])
            elif action == 'clear_pay_room_money':
                conMysql.updateXsUserprofile_pay_room_money(params['uid'])
            elif action == 'clear_popularity':
                conMysql.updateXsUserpopularity(params['uid'])

    def _validate_db_state(self, checks):
        """验证数据库状态（海外版通用业务校验分发器）

        每个 check 字典支持的 key:
            assert_func (可选) 自定义无参断言函数（存在时忽略其余 key）
            field       (必填) 查询字段（含 pay_room_money / popularity 特殊字段）
            uid         (可选) 用户 ID，默认 config.oversea_payUid
            expected    (可选) 期望相等值（assert_equal）
            min         (可选) 期望最小值（assert_len）
            money_type  (可选) 货币类型（single_money 专用）
            kwargs      (可选) 额外查询参数 dict
        """
        for check in checks:
            if 'assert_func' in check:
                check['assert_func']()
                continue
            field = check['field']
            uid = check.get('uid', config.oversea_payUid)
            if field in EXTRA_QUERY_MAP:
                actual = EXTRA_QUERY_MAP[field](uid)
            else:
                kwargs = dict(check.get('kwargs', {}))
                if 'money_type' in check:
                    kwargs.setdefault('money_type', check['money_type'])
                actual = conMysql.selectUserInfoSql(field, uid, **kwargs)
            if 'expected' in check:
                assert_equal(actual, check['expected'])
            if 'min' in check:
                assert_len(actual, check['min'])
