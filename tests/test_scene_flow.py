# coding=utf-8
"""
common/scene_base.py 单元测试（场景执行骨架 / 延迟求值辅助）

无任何外部依赖，可直接运行：
    python -m pytest tests/test_scene_flow.py -v
"""
import unittest

from common.scene_base import SceneFlowBase, resolve, resolve_check


class _DummyFlow(SceneFlowBase):
    """仅用于承载被测方法的空骨架子类（不定义 test_ 方法与钩子）"""


class _RecorderFlow(SceneFlowBase):
    """记录各阶段调用顺序的骨架子类（events 由测试注入）"""

    events = None

    def flow_prepare(self, scene, ctx):
        self.events.append('prepare')

    def flow_queries(self, scene, ctx):
        self.events.append('queries')

    def flow_request(self, scene, ctx):
        self.events.append('request')

    def flow_assert(self, scene, ctx):
        self.events.append('assert')

    def flow_wait(self, scene, ctx):
        self.events.append('wait')

    def flow_validate(self, scene, ctx):
        self.events.append('validate')

    def flow_record(self, scene, ctx):
        self.events.append('record')


class TestRunFlow(unittest.TestCase):
    """run_flow 阶段编排"""

    def test_flow_order(self):
        """七个阶段必须按固定顺序执行"""
        flow = _RecorderFlow.__new__(_RecorderFlow)
        flow.events = []
        flow.run_flow('scene')
        self.assertEqual(flow.events,
                         ['prepare', 'queries', 'request',
                          'assert', 'wait', 'validate', 'record'])

    def test_ctx_assembly_and_shared_state(self):
        """ctx 初始含 cls/self，且各阶段共享同一字典实例"""
        seen = {}

        class _Probe(SceneFlowBase):
            def flow_prepare(self, scene, ctx):
                ctx['token'] = 42

            def flow_queries(self, scene, ctx):
                seen['cls'] = ctx['cls']
                seen['self'] = ctx['self']
                seen['token'] = ctx['token']

            def flow_request(self, scene, ctx):
                pass

        flow = _Probe.__new__(_Probe)
        flow.run_flow('scene')
        self.assertIs(seen['cls'], _Probe)
        self.assertIs(seen['self'], flow)
        self.assertEqual(seen['token'], 42)

    def test_request_default_raises(self):
        """未实现 flow_request 的子类执行时必须显式报错"""
        flow = _DummyFlow.__new__(_DummyFlow)
        with self.assertRaises(NotImplementedError):
            flow.run_flow('scene')

    def test_optional_hooks_default_to_noop(self):
        """除 flow_request 外其余钩子默认可省略"""

        class _Minimal(SceneFlowBase):
            def flow_request(self, scene, ctx):
                pass

        flow = _Minimal.__new__(_Minimal)
        flow.run_flow('scene')  # 不应抛出任何异常


class TestResolveHelpers(unittest.TestCase):
    """resolve / resolve_check 延迟求值"""

    def test_resolve_callable_with_ctx(self):
        self.assertEqual(resolve(lambda ctx: ctx['q'] + 1, {'q': 7}), 8)

    def test_resolve_plain_value(self):
        self.assertEqual(resolve(7, {}), 7)
        self.assertEqual(resolve('abc', {}), 'abc')

    def test_resolve_check_resolves_callable_expected(self):
        """expected 为 callable 时返回解析后的新字典，且不修改原字典"""
        check = {'field': 'bean', 'expected': lambda ctx: ctx['q'] * 2}
        resolved = resolve_check(check, {'q': 5})
        self.assertEqual(resolved, {'field': 'bean', 'expected': 10})
        self.assertIsNot(resolved, check)
        self.assertTrue(callable(check['expected']))

    def test_resolve_check_returns_original_when_plain(self):
        check = {'field': 'bean', 'expected': 5}
        self.assertIs(resolve_check(check, {}), check)


if __name__ == '__main__':
    unittest.main()
