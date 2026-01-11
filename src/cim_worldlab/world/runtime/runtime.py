"""
runtime.py
==========
世界运行时（WorldRuntime）——世界会动的心脏

Step 9 我们有：
- tick 产生 WORLD_TICK
- ingest_inputs 产生 EXTERNAL_INPUT
- _record 统一留痕（内存 + 可选落盘）

Step 10 我们加入：
- state: WorldState（世界状态）
- reducer: apply_event(state, event) -> new_state
- 每次 _record 时，除了留痕，还会“推导状态”

工程上的重要变化：
- runtime 不再“手写维护各种状态字段”
- runtime 只负责：记录事件 + 用 reducer 得到新状态
- replay 不再只恢复 t，而是恢复整个 state
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

from cim_worldlab.world.events.event import Event
from cim_worldlab.world.events.external_input import ExternalInput, EXTERNAL_INPUT_TYPE
from cim_worldlab.world.runtime.event_log import EventLog
from cim_worldlab.world.persistence.file_event_store import FileEventStore
from cim_worldlab.world.gateway.plugin_gateway import PluginGateway

from cim_worldlab.world.state import WorldState, apply_event, apply_events


@dataclass
class WorldRuntime:
    """
    字段解释：
    - t: 世界时间（为了兼容早期代码/直观展示，仍保留）
    - state: 世界状态（权威来源：由事件推导）
    - event_log: 内存事件日志
    - event_store: 可选落盘
    - gateway: 可选外部输入网关
    """
    t: int = 0
    state: WorldState = field(default_factory=WorldState.initial)
    event_log: EventLog = field(default_factory=EventLog)
    event_store: Optional[FileEventStore] = None
    gateway: Optional[PluginGateway] = None

    def _record(self, e: Event) -> None:
        """
        统一留痕入口（非常关键）：

        1) 写入内存日志（可调试/可教学）
        2) 可选：落盘写入 FileEventStore（工程留痕）
        3) 更新 state（由 reducer 推导，而不是手写乱改）

        注意：
        - 我们仍然维护 self.t，但它应该和 self.state.t 同步
        - 长远看，你甚至可以去掉 self.t，只保留 state.t
          但为了教学循序渐进，我们先两者并存。
        """
        # (1) 内存留痕
        self.event_log.append(e)

        # (2) 文件留痕（可选）
        if self.event_store is not None:
            self.event_store.append(e)

        # (3) 状态推导（核心）
        self.state = apply_event(self.state, e)

        # (4) 同步 runtime.t（直观展示用）
        self.t = self.state.t

    def tick(self, payload: Optional[Dict[str, Any]] = None) -> Event:
        """
        世界自身推进一步：
        - 推进世界时间（t+1）
        - 产生 WORLD_TICK 事件
        - 留痕 + 推导状态
        """
        next_t = self.t + 1
        e = Event(t=next_t, type="WORLD_TICK", payload=payload or {})
        self._record(e)
        return e

    def ingest_inputs(self) -> List[Event]:
        """
        从插件网关拉取外部输入，并转成 EXTERNAL_INPUT 事件写入日志。

        设计选择（MVP）：
        - 外部输入事件“附着在当前世界时间点 t”
        - ingest 本身不推进世界时间
        """
        if self.gateway is None:
            return []

        inputs: List[ExternalInput] = self.gateway.pull_inputs()
        events: List[Event] = []

        for inp in inputs:
            e = inp.to_event(t=self.t)
            assert e.type == EXTERNAL_INPUT_TYPE
            self._record(e)
            events.append(e)

        return events

    @classmethod
    def replay_from_store(cls, store: FileEventStore) -> "WorldRuntime":
        """
        从事件存储回放 replay，重建 runtime。

        Step 10 的关键点：
        - 不只恢复 t
        - 要恢复完整 state（由事件序列推导得到）
        """
        events = store.load_all()

        # 1) 从初始状态开始，把所有事件应用一遍得到最终状态
        final_state = apply_events(WorldState.initial(), events)

        # 2) 构造 runtime：t/state 对齐，event_log 装入历史
        rt = cls(
            t=final_state.t,
            state=final_state,
            event_store=store,
            gateway=None,
        )
        for e in events:
            rt.event_log.append(e)

        return rt
