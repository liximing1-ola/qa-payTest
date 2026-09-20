# coding=utf-8
"""
Starify 域支付测试公共基类

通过 StarifyCase + run_case 提供数据驱动的 Starify 支付场景执行模板，
把 caseStarify/ 各测试文件中重复的"数据准备 -> 请求 -> 断言 -> 校验 -> 记录"
流程收敛到基类。七段式执行骨架（准备 -> 查询 -> 请求 -> 断言 -> 等待 ->
校验 -> 记录）由 common/scene_base.py 的 SceneFlowBase 编排，
本模块为其 Starify 域适配层（请求走 common.Request.post_starify）。

与 caseSlp/base.py 的差异：
- Starify 域无请求前查询（queries）与请求后等待（post_wait）需求；
- 响应断言区分两种模式——成功用例断言 success，失败用例仅断言 msg
  （由 StarifyCase.success 的 None 语义表达）；
- DB 校验为自定义断言 callable 列表（无通用字段式查询分发器）。
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from common.Assert import assert_body, assert_code
from common.Consts import case_list, case_list_b, result
from common.Request import post_starify
from common.conStarifyMysql import conMysql
from common.scene_base import SceneFlowBase

# 场景结果记录表（与各测试文件的报告表一一对应）
REPORT_TABLES = {
    'case_list': case_list,
    'case_list_b': case_list_b,
}


@dataclass(frozen=True)
class StarifyCase:
    """Starify 支付场景参数

    一个场景完整描述一次 Starify 支付验证的全部差异点，
    由 StarifyTestBase.run_case 统一执行（字段语义对齐 case.base.PayCase）。
    """

    # 用例描述（同时作为报告表键）
    des: str
    # 数据准备步骤（_prepare_test_data 分发格式）
    setup: list = field(default_factory=list)
    # post_starify 请求数据（deal_pay_data / deal_pay_contract_data 产物）
    data: Dict[str, Any] = field(default_factory=dict)
    # 响应 success 预期值；None 表示不断言 success（失败用例仅断言 msg）
    success: Optional[bool] = True
    # 响应 msg 预期值（None 时跳过断言）
    msg: Optional[str] = None
    # DB 校验函数列表（无参 callable，逐个调用执行断言）
    checks: list = field(default_factory=list)
    # 结果记录表：'case_list' / 'case_list_b'
    report: str = 'case_list'


class StarifyTestBase(SceneFlowBase):
    """Starify 支付测试通用基类

    子类在模块级场景表中声明各场景的差异点，test 方法调用 run_case 执行。
    场景执行由 SceneFlowBase.run_flow 编排，本类实现各阶段钩子。
    """

    def run_case(self, case: StarifyCase) -> None:
        """执行单个 Starify 支付场景

        Args:
            case: 场景参数（模块级场景表中声明）
        """
        self.run_flow(case)

    # ============ 场景骨架钩子实现 ============
    def flow_prepare(self, case: StarifyCase, ctx: Dict[str, Any]) -> None:
        """1. 准备测试数据"""
        if case.setup:
            self._prepare_test_data(case.setup)

    def flow_request(self, case: StarifyCase, ctx: Dict[str, Any]) -> None:
        """3. 发起 Starify 支付请求"""
        ctx['_res'] = post_starify(case.data)

    def flow_assert(self, case: StarifyCase, ctx: Dict[str, Any]) -> None:
        """4. 响应断言（success 为 None 时仅断言 msg）"""
        res = ctx['_res']
        assert_code(res['code'])
        if case.success is not None:
            assert_body(res['body'], 'success', case.success)
        if case.msg is not None:
            assert_body(res['body'], 'msg', case.msg)

    def flow_validate(self, case: StarifyCase, ctx: Dict[str, Any]) -> None:
        """6. DB 校验（逐个执行自定义断言函数）"""
        for check in case.checks:
            check()

    def flow_record(self, case: StarifyCase, ctx: Dict[str, Any]) -> None:
        """7. 记录结果"""
        REPORT_TABLES[case.report][case.des] = result

    def _prepare_test_data(self, setup_steps):
        """准备测试数据（Starify 域通用步骤分发器）

        支持的 action:
            update_money           → conMysql.updateMoneySql(uid, money)
            update_wealth          → conMysql.updateWealthSql(uid, wealth)
            update_charm           → conMysql.updateCharmSql(uid, charm)
            delete_user_account    → conMysql.deleteUserAccountSql(table, uid, wid)
            insert_commodity       → conMysql.insertXsUserCommodity(uid, cid, num)
            delete_producer_singer → conMysql.deleteProducerSinger(singer_uid)
            update_singer_worth    → conMysql.updateSingerWorth(singer_uid, worth)
        """
        for step in setup_steps:
            action = step['action']
            params = step.get('params', {})
            if action == 'update_money':
                conMysql.updateMoneySql(params['uid'], params['money'])
            elif action == 'update_wealth':
                conMysql.updateWealthSql(params['uid'], params['wealth'])
            elif action == 'update_charm':
                conMysql.updateCharmSql(params['uid'], params['charm'])
            elif action == 'delete_user_account':
                conMysql.deleteUserAccountSql(params['table'], params['uid'],
                                              params.get('wid', 0))
            elif action == 'insert_commodity':
                conMysql.insertXsUserCommodity(params['uid'], params['cid'], params['num'])
            elif action == 'delete_producer_singer':
                conMysql.deleteProducerSinger(params['singer_uid'])
            elif action == 'update_singer_worth':
                conMysql.updateSingerWorth(params['singer_uid'], params['worth'])
