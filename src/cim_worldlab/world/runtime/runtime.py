"""
runtime.py
==========
WorldRuntime：世界运行时（世界会动的心脏）

我们现在的完整能力链：
Step 7: tick + 内存 EventLog
Step 8: 事件落盘 FileEventStore + replay
Step 9: 外部输入 ingest_inputs + PluginGateway
Step 10: WorldState + reducer（状态由事件推导）
Step 11: metrics（可观测指标）
Step 12: snapshot（快照）+ replay 加速

本文件新增：
- maybe_snapshot(snapshot_store, every_n_events)
- replay_fast_from_store(event_store, snapshot_store)
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple

from cim_worldlab.world.events.event import Event
from cim_worldlab.world.events.external_input import ExternalInput, EXTERNAL_INPUT_TYPE
from cim_worldlab.world.runtime.event_log import EventLog
from cim_worldlab.world.persistence.file_event_store import FileEventStore
from cim_worldlab.world.persistence.snapshot_store import SnapshotStore
from cim_worldlab.world.gateway.plugin_gateway import PluginGateway

from cim_worldlab.world.state import WorldState, apply_event, apply_events


@dataclass
class WorldRuntime:
    t: int = 0
    state: WorldState = field(default_factory=WorldState.initial)
    event_log: EventLog = field(default_factory=EventLog)
    event_store: Optional[FileEventStore] = None
    gateway: Optional[PluginGateway] = None

    def _record(self, e: Event) -> None:
        """
        统一留痕入口：
        - event_log.append
        - event_store.append（可选）
        - state = apply_event(state, e)
        - t 与 state.t 同步
        """
        self.event_log.append(e)
        if self.event_store is not None:
            self.event_store.append(e)

        self.state = apply_event(self.state, e)
        self.t = self.state.t

    def tick(self, payload: Optional[Dict[str, Any]] = None) -> Event:
        next_t = self.t + 1
        e = Event(t=next_t, type="WORLD_TICK", payload=payload or {})
        self._record(e)
        return e

    def ingest_inputs(self) -> List[Event]:
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

    def metrics(self):
        """
        返回当前世界指标快照（WorldMetrics）。
        这里使用“函数内 import”避免潜在循环依赖。
        """
        from cim_worldlab.world.metrics import compute_metrics
        return compute_metrics(self.state, self.event_log)

    # -------------------------------
    # Step 12: 快照相关能力
    # -------------------------------

    def maybe_snapshot(self, snapshot_store: SnapshotStore, every_n_events: int = 50) -> bool:
        """
        根据事件数量，决定是否保存快照。

        参数：
        - snapshot_store：快照存储
        - every_n_events：每累计 N 条事件保存一次

        返回：
        - True：这次保存了快照
        - False：这次没保存（事件数量还没到阈值）

        规则（MVP）：
        - 当 len(event_log) 是 every_n_events 的倍数时保存
        - last_event_index = len(event_log) - 1
        """
        n = len(self.event_log)
        if n == 0:
            return False
        if n % every_n_events != 0:
            return False

        last_event_index = n - 1
        snapshot_store.save(self.state, last_event_index=last_event_index)
        return True

    @classmethod
    def replay_from_store(cls, store: FileEventStore) -> "WorldRuntime":
        """
        传统 replay：从第一条事件开始回放（慢但简单）。
        """
        events = store.load_all()
        final_state = apply_events(WorldState.initial(), events)

        rt = cls(t=final_state.t, state=final_state, event_store=store, gateway=None)
        for e in events:
            rt.event_log.append(e)
        return rt

    @classmethod
    def replay_fast_from_store(cls, store: FileEventStore, snapshot_store: SnapshotStore) -> "WorldRuntime":
        """
        快速 replay：优先使用快照，再补快照之后的事件。

        流程：
        1) 尝试读取快照：
           - 没快照：退化为 replay_from_store（全量回放）
        2) 有快照：
           - 从快照拿到 state + last_event_index
           - 从事件存储读取 last_event_index+1 之后的事件
           - 用 apply_events 把“剩余事件”补到快照 state 上
        3) 构造 runtime：
           - state/t 与最终结果对齐
           - event_log 仍然装入所有事件（为了教学可视化）
             （未来可做：只装一部分，或按需加载）
        """
        snap = snapshot_store.load()
        if snap is None:
            return cls.replay_from_store(store)

        base_state, last_event_index = snap

        remaining = store.load_from_index(last_event_index + 1)
        final_state = apply_events(base_state, remaining)

        rt = cls(t=final_state.t, state=final_state, event_store=store, gateway=None)

        # 为了保持“event_log 可视化”，我们仍加载全部事件
        # （MVP：简单清晰；未来：可以优化为懒加载）
        for e in store.load_all():
            rt.event_log.append(e)

        return rt
