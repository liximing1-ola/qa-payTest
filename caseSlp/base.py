# coding=utf-8
"""
SLP 域支付测试公共基类

通过 SlpCase + run_case 提供数据驱动的 SLP 支付场景执行模板，
把 caseSlp/ 各测试文件中重复的"数据准备 -> 请求 -> 断言 -> 校验 -> 记录"
流程收敛到基类。七段式执行骨架（准备 -> 查询 -> 请求 -> 断言 -> 等待 ->
校验 -> 记录）由 common/scene_base.py 的 SceneFlowBase 编排，
本模块为其 SLP 域适配层（请求走 caseSlp/config.py 的 pay_url，token=slp）。
"""
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from caseSlp.config import payUid, pay_url
from common.Assert import assert_body, assert_code, assert_equal
from common.Consts import case_list, case_list_b, result
from common.Request import post_request_session
from common.basicSlpData import encodeData
from common.conSlpMysql import conMysql as mysql
from common.scene_base import SceneFlowBase, resolve, resolve_check
from common.sqlScript import UserCommodityOperations, UserMoneyOperations

# 场景结果记录表（与各测试文件的报告表一一对应）
REPORT_TABLES = {
    'case_list': case_list,
    'case_list_b': case_list_b,
}


@dataclass(frozen=True)
class SlpCase:
    """SLP 支付场景参数

    一个场景完整描述一次 SLP 支付验证的全部差异点，
    由 SlpTestBase.run_case 统一执行（字段语义对齐 case.base.PayCase）。
    """

    # 用例描述（同时作为报告表键）
    des: str
    # 自定义组合准备 callable(testcase)，先于 setup 执行
    prepare: Optional[Callable] = None
    # 数据准备步骤（_prepare_test_data 分发格式）
    setup: list = field(default_factory=list)
    # 请求前查询：((ctx 键, 无参可调用), ...)，结果存入 ctx 供 data/checks 引用
    queries: list = field(default_factory=list)
    # encodeData 参数；值可为 callable(ctx) 在运行期求值
    data: Dict[str, Any] = field(default_factory=dict)
    # 响应 success 预期值（失败场景为 0）
    success: int = 1
    # 响应 msg 预期值（None 时跳过断言）
    msg: Optional[str] = None
    # 请求后等待秒数（等待异步数据落库）
    post_wait: float = 0
    # DB 校验项（_validate_db_state 格式）；expected 可为 callable(ctx) 延迟求值
    checks: list = field(default_factory=list)
    # 结果记录表：'case_list' / 'case_list_b'
    report: str = 'case_list'


class SlpTestBase(SceneFlowBase):
    """SLP 支付测试通用基类

    子类在模块级场景表中声明各场景的差异点，test 方法调用 run_case 执行。
    场景执行由 SceneFlowBase.run_flow 编排，本类实现各阶段钩子。
    """

    def run_case(self, case: SlpCase) -> None:
        """执行单个 SLP 支付场景

        Args:
            case: 场景参数（模块级场景表中声明）
        """
        self.run_flow(case)

    # ============ 场景骨架钩子实现 ============
    def flow_prepare(self, case: SlpCase, ctx: Dict[str, Any]) -> None:
        """1. 准备测试数据（自定义组合准备 + 标准步骤）"""
        if case.prepare is not None:
            case.prepare(self)
        if case.setup:
            self._prepare_test_data(case.setup)

    def flow_queries(self, case: SlpCase, ctx: Dict[str, Any]) -> None:
        """2. 请求前查询（供动态 data/checks 引用）"""
        for key, query in case.queries:
            ctx[key] = query()

    def flow_request(self, case: SlpCase, ctx: Dict[str, Any]) -> None:
        """3. 发起 SLP 支付请求（pay_url + token=slp）"""
        data = encodeData(**{key: resolve(value, ctx) for key, value in case.data.items()})
        ctx['_res'] = post_request_session(pay_url, data, token_name='slp')

    def flow_assert(self, case: SlpCase, ctx: Dict[str, Any]) -> None:
        """4. 响应断言"""
        res = ctx['_res']
        assert_code(res['code'])
        assert_body(res['body'], 'success', case.success)
        if case.msg is not None:
            assert_body(res['body'], 'msg', case.msg)

    def flow_wait(self, case: SlpCase, ctx: Dict[str, Any]) -> None:
        """5. 等待异步数据落库"""
        if case.post_wait:
            time.sleep(case.post_wait)

    def flow_validate(self, case: SlpCase, ctx: Dict[str, Any]) -> None:
        """6. DB 校验"""
        if case.checks:
            self._validate_db_state([resolve_check(check, ctx) for check in case.checks], ctx)

    def flow_record(self, case: SlpCase, ctx: Dict[str, Any]) -> None:
        """7. 记录结果"""
        REPORT_TABLES[case.report][case.des] = result

    def _prepare_test_data(self, setup_steps):
        """准备测试数据（SLP 域通用步骤分发器）

        支持的 action:
            update_money         → UserMoneyOperations.update(**params)
            clear_user_money     → mysql.updateUserMoneyClearSql(*uids)
            delete_user_account  → mysql.deleteUserAccountSql(table, uid)
            delete_commodity     → mysql.deleteUserAccountSql('user_commodity', uid)
            insert_commodity     → UserCommodityOperations.insert(uid, **params)
            update_user_god      → mysql.updateUserGodSql(uid, god)
            update_user_title    → mysql.updateUserInfoSql('user_title_new', uid, level)
            check_user_broker    → assert_equal(mysql.checkUserBroker(uid), expected)
            check_rid_type       → assert_equal(mysql.checkRidFactoryType(rid), expected)
        """
        for step in setup_steps:
            action = step['action']
            params = step.get('params', {})
            if action == 'update_money':
                UserMoneyOperations.update(**params)
            elif action == 'clear_user_money':
                mysql.updateUserMoneyClearSql(*step['uids'])
            elif action == 'delete_user_account':
                mysql.deleteUserAccountSql(params.get('table', step.get('table')),
                                           params.get('uid', step.get('uid')))
            elif action == 'delete_commodity':
                mysql.deleteUserAccountSql('user_commodity', step['uid'])
            elif action == 'insert_commodity':
                insert_params = dict(params)
                uid = insert_params.pop('uid', payUid)
                UserCommodityOperations.insert(uid, **insert_params)
            elif action == 'update_user_god':
                mysql.updateUserGodSql(params['uid'], params['god'])
            elif action == 'update_user_title':
                mysql.updateUserInfoSql('user_title_new', params['uid'], level=params['level'])
            elif action == 'check_user_broker':
                assert_equal(mysql.checkUserBroker(step['uid']), step['expected'])
            elif action == 'check_rid_type':
                assert_equal(mysql.checkRidFactoryType(step['rid']), step['expected'])

    def _validate_db_state(self, checks, ctx=None):
        """验证数据库状态（SLP 域校验分发器）

        每个 check 字典支持的 key:
            field       (必填) 查询字段
            uid         (可选) 用户 ID，默认 payUid
            expected    (可选) 期望值
            kwargs      (可选) 额外查询参数 dict
            money_type  (可选) 货币类型（single_money 专用）
            cid         (可选) 物品/渠道 ID
            payuid      (可选) 守护关系查询中的付款人 ID
            assert_func (可选) 自定义断言函数 assert_func(ctx)
        """
        for check in checks:
            if 'assert_func' in check:
                check['assert_func'](ctx)
                continue
            field = check['field']
            uid = check.get('uid', payUid)
            kwargs = dict(check.get('kwargs', {}))
            if 'money_type' in check:
                kwargs.setdefault('money_type', check['money_type'])
            if 'cid' in check:
                kwargs.setdefault('cid', check['cid'])
            if 'payuid' in check:
                kwargs.setdefault('payuid', check['payuid'])
            actual = mysql.selectUserInfoSql(field, uid, **kwargs)
            assert_equal(actual, check.get('expected'))
