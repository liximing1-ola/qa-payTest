# coding=utf-8
"""
场景执行骨架（模板方法模式）

统一 case/base.py（PayTestBase）与 caseOversea/base.py（OverseaAreaTestBase）
重复实现的七段式场景执行流程：

    prepare -> queries -> request -> assert -> wait -> validate -> record

适配层继承 SceneFlowBase 后，只需按域实现各 flow_* 钩子；
run_flow 负责组装阶段间共享上下文 ctx 并按固定顺序编排调用。
"""
import unittest
from typing import Any, Dict


def resolve(value: Any, ctx: Dict[str, Any]) -> Any:
    """解析场景值：callable 在运行期以 ctx 求值，其余原样返回"""
    return value(ctx) if callable(value) else value


def resolve_check(check: dict, ctx: Dict[str, Any]) -> dict:
    """解析校验项中延迟求值的 expected（返回新字典，不修改原项）"""
    if callable(check.get('expected')):
        return {**check, 'expected': check['expected'](ctx)}
    return check


class SceneFlowBase(unittest.TestCase):
    """场景执行骨架

    子类通过 run_flow(scene) 执行场景；ctx 为阶段间共享状态，初始包含：
        cls  - 当前测试类（等价 type(self)，兼容原用例 ctx['cls'] 用法）
        self - 当前测试实例
    各阶段可将中间结果（请求响应、解析后的断言项等）写入 ctx 供后续阶段读取。

    默认实现：flow_request 必须被子类覆盖（骨架无默认请求语义），
    其余阶段默认不执行任何操作。
    """

    def run_flow(self, scene: Any) -> None:
        """按固定顺序执行七个阶段

        Args:
            scene: 场景参数对象（PayCase / PayScene 等）
        """
        ctx: Dict[str, Any] = {'cls': type(self), 'self': self}
        self.flow_prepare(scene, ctx)
        self.flow_queries(scene, ctx)
        self.flow_request(scene, ctx)
        self.flow_assert(scene, ctx)
        self.flow_wait(scene, ctx)
        self.flow_validate(scene, ctx)
        self.flow_record(scene, ctx)

    # ============ 阶段钩子（子类按需覆盖） ============
    def flow_prepare(self, scene: Any, ctx: Dict[str, Any]) -> None:
        """1. 准备：前置数据构造"""

    def flow_queries(self, scene: Any, ctx: Dict[str, Any]) -> None:
        """2. 查询：前置查询结果写入 ctx，供延迟求值引用"""

    def flow_request(self, scene: Any, ctx: Dict[str, Any]) -> None:
        """3. 请求：发起场景请求（必须由子类实现）"""
        raise NotImplementedError('子类必须实现 flow_request')

    def flow_assert(self, scene: Any, ctx: Dict[str, Any]) -> None:
        """4. 断言：响应校验"""

    def flow_wait(self, scene: Any, ctx: Dict[str, Any]) -> None:
        """5. 等待：异步消息处理等待"""

    def flow_validate(self, scene: Any, ctx: Dict[str, Any]) -> None:
        """6. 校验：数据库状态校验"""

    def flow_record(self, scene: Any, ctx: Dict[str, Any]) -> None:
        """7. 记录：结果写入报告表"""
