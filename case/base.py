# coding=utf-8
"""
支付测试公共基类

提取 case/ 目录下各测试文件中重复的 _prepare_test_data / _validate_db_state
辅助方法，并通过 PayCase + run_case 提供数据驱动的支付场景执行模板。
七段式执行骨架（准备 -> 查询 -> 请求 -> 断言 -> 等待 -> 校验 -> 记录）由
common/scene_base.py 的 SceneFlowBase 编排，本模块为其支付域适配层。

兼容别名（供现有用例与测试引用）：
- 模块级 _resolve、PayTestBase._resolve_check
- REPORT_TABLES 保留本模块定义，报告路由与测试 patch 目标不变
"""
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from common.Config import config
from common.Assert import assert_equal, assert_len, assert_code, assert_body
from common.Request import post_request_session
from common.basicData import encodeData
from common.Consts import case_list, case_list_b, case_list_c, result
from common.conMysql import conMysql as mysql
from common.scene_base import SceneFlowBase, resolve, resolve_check
from common.sqlScript import UserMoneyOperations, UserCommodityOperations

# 场景结果记录表（与各测试文件的报告表一一对应）
REPORT_TABLES = {
    'case_list': case_list,
    'case_list_b': case_list_b,
    'case_list_c': case_list_c,
}

# 兼容别名：原模块级延迟求值辅助（现由 common.scene_base 提供）
_resolve = resolve


@dataclass(frozen=True)
class PayCase:
    """支付场景参数

    一个场景完整描述一次支付验证的全部差异点，
    由 PayTestBase.run_case 统一执行。
    """

    # 用例描述（同时作为报告表键）
    des: str
    # 数据准备步骤（_prepare_test_data 分发格式）
    setup: list = field(default_factory=list)
    # encodeData 参数；值可为 callable(ctx) 在运行期求值
    data: Dict[str, Any] = field(default_factory=dict)
    # DB 校验项（_validate_db_state 格式）；expected 可为 callable(ctx) 延迟求值
    checks: list = field(default_factory=list)
    # 响应 success 预期值（失败场景为 0）
    success: int = 1
    # 响应 msg 预期值（None 时跳过断言）
    msg: Optional[str] = None
    # 请求后等待秒数（等待 NSQ 等异步消息处理）
    post_wait: float = 0
    # 请求前查询：((ctx 键, 无参可调用), ...)，结果存入 ctx 供 data/checks 引用
    queries: list = field(default_factory=list)
    # 自定义组合准备 callable(testcase)，先于 setup 执行
    prepare: Optional[Callable] = None
    # 结果记录表：'case_list' / 'case_list_b' / 'case_list_c'
    report: str = 'case_list'


class PayTestBase(SceneFlowBase):
    """支付测试通用基类

    提供通用的数据准备和数据库验证方法，以及数据驱动的场景执行模板，
    子类只需在模块级 SCENES 表中声明各场景的差异点。
    场景执行由 SceneFlowBase.run_flow 编排，本类实现各阶段钩子。
    """

    # 兼容别名：原 PayTestBase._resolve_check
    _resolve_check = staticmethod(resolve_check)

    def run_case(self, case: PayCase) -> None:
        """执行单个支付场景

        Args:
            case: 场景参数（模块级 SCENES 表中声明）
        """
        self.run_flow(case)

    # ============ 场景骨架钩子实现 ============
    def flow_prepare(self, case: PayCase, ctx: Dict[str, Any]) -> None:
        """1. 准备测试数据（自定义组合准备 + 标准步骤）"""
        if case.prepare is not None:
            case.prepare(self)
        if case.setup:
            self._prepare_test_data(case.setup)

    def flow_queries(self, case: PayCase, ctx: Dict[str, Any]) -> None:
        """2. 请求前查询（供动态 data/checks 引用）"""
        for key, query in case.queries:
            ctx[key] = query()

    def flow_request(self, case: PayCase, ctx: Dict[str, Any]) -> None:
        """3. 发起请求（响应存入 ctx['_res'] 供断言阶段使用）"""
        data = encodeData(**{key: resolve(value, ctx) for key, value in case.data.items()})
        ctx['_res'] = post_request_session(config.pay_url, data)

    def flow_assert(self, case: PayCase, ctx: Dict[str, Any]) -> None:
        """4. 响应断言"""
        res = ctx['_res']
        assert_code(res['code'])
        assert_body(res['body'], 'success', case.success)
        if case.msg is not None:
            assert_body(res['body'], 'msg', case.msg)

    def flow_wait(self, case: PayCase, ctx: Dict[str, Any]) -> None:
        """5. 等待异步消息处理（NSQ 等）"""
        if case.post_wait:
            time.sleep(case.post_wait)

    def flow_validate(self, case: PayCase, ctx: Dict[str, Any]) -> None:
        """6. DB 校验"""
        if case.checks:
            self._validate_db_state([self._resolve_check(check, ctx) for check in case.checks])

    def flow_record(self, case: PayCase, ctx: Dict[str, Any]) -> None:
        """7. 记录结果"""
        REPORT_TABLES[case.report][case.des] = result

    def _prepare_test_data(self, setup_steps):
        """准备测试数据（通用步骤分发器）

        支持的 action:
            update_money         → UserMoneyOperations.update(**params)
            clear_user_money     → mysql.updateUserMoneyClearSql(uid1, uid2?)
            clear_user_data      → mysql.updateUserMoneyClearSql(config.payUid, config.rewardUid)
            delete_user_account  → mysql.deleteUserAccountSql(table, uid)
            delete_account       → mysql.deleteUserAccountSql(table, uid)
            insert_commodity     → UserCommodityOperations.insert(uid, **params)
            insert_user_box      → mysql.insertXsUserBox(uid, **params)
            check_user_broker    → mysql.checkUserBroker(uid, bid)
            check_broker_rate    → mysql.checkBrokerUserRate(uid, creater, rate)
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
                params = dict(params)
                uid = params.pop('uid', config.payUid)
                UserCommodityOperations.insert(uid, **params)
            elif action == 'insert_user_box':
                uid = step.get('uid', config.payUid)
                mysql.insertXsUserBox(uid, **params)
            elif action == 'check_user_broker':
                mysql.checkUserBroker(**params) if params else mysql.checkUserBroker(step['uid'], bid=step['bid'])
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
