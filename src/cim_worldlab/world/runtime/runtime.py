"""
runtime.py
==========
世界运行时（WorldRuntime）——世界会动的心脏

你现在的世界有两类“发生的事”：
1) 世界自身推进：tick -> 产生 WORLD_TICK 事件
2) 外部注入输入：ingest_inputs -> 产生 EXTERNAL_INPUT 事件

非常重要的工程原则：
- runtime 不做“业务含义判断”
- runtime 只做：时间推进 + 事件留痕 + 调用边界
- 真正的业务规则（例如 OMS/FDC/SPC）会在后面通过“状态机/reducer/policy”来做

这一层像什么？
- 像操作系统的内核：它负责调度与记录，不负责业务决策
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

from cim_worldlab.world.events.event import Event
from cim_worldlab.world.events.external_input import ExternalInput, EXTERNAL_INPUT_TYPE
from cim_worldlab.world.runtime.event_log import EventLog
from cim_worldlab.world.persistence.file_event_store import FileEventStore
from cim_worldlab.world.gateway.plugin_gateway import PluginGateway


@dataclass
class WorldRuntime:
    """
    字段解释：
    - t: 世界时间（tick 计数）
    - event_log: 内存日志（调试/教学很直观）
    - event_store: 可选的持久化存储（工程留痕）
    - gateway: 可选插件网关（外部输入来源）
      gateway 不一定总是存在：例如纯离线 replay 场景
    """
    t: int = 0
    event_log: EventLog = field(default_factory=EventLog)
    event_store: Optional[FileEventStore] = None
    gateway: Optional[PluginGateway] = None

    def _record(self, e: Event) -> None:
        """
        统一的“留痕入口”：
        - 先写内存
        - 如果配置了 store，再落盘

        把留痕集中在一个地方，是工程化的关键：
        - 以后你想加“指标更新/审计钩子/调试输出”，改这里就够了
        """
        self.event_log.append(e)
        if self.event_store is not None:
            self.event_store.append(e)

    def tick(self, payload: Optional[Dict[str, Any]] = None) -> Event:
        """
        世界自身推进一步：
        - t += 1
        - 产生 WORLD_TICK
        - 留痕
        """
        self.t += 1
        e = Event(t=self.t, type="WORLD_TICK", payload=payload or {})
        self._record(e)
        return e

    def ingest_inputs(self) -> List[Event]:
        """
        从插件网关拉取外部输入，并转成世界内部事件写入日志。

        返回：
        - 这次 ingest 产生的 Event 列表（可能为空）

        关键点：
        - ingest_inputs 不推进世界时间（不做 t += 1）
          因为外部输入发生在“当前世界时间点 t”
          （你也可以设计成：每个输入推进一步，这取决于你的世界规则；
           但 MVP 阶段先采用“输入附着在当前 t”）
        """
        if self.gateway is None:
            return []

        inputs: List[ExternalInput] = self.gateway.pull_inputs()
        events: List[Event] = []

        for inp in inputs:
            e = inp.to_event(t=self.t)  # 外部输入附着在当前时间点
            # 再次强调：Event.type 固定为 EXTERNAL_INPUT
            # 具体含义在 payload.name/channel/source/data
            assert e.type == EXTERNAL_INPUT_TYPE
            self._record(e)
            events.append(e)

        return events

    @classmethod
    def replay_from_store(cls, store: FileEventStore) -> "WorldRuntime":
        """
        从持久化事件存储回放 replay，重建 runtime。

        MVP 规则：
        - t = 最后事件的 t（没事件则 0）
        - event_log 复原所有历史事件（用于教学/调试）
        - event_store 指向同一个 store（便于继续追加）
        - gateway 默认 None（回放通常是离线，不接外部输入）
        """
        events = store.load_all()
        rt = cls(t=0, event_store=store, gateway=None)

        for e in events:
            rt.event_log.append(e)
            rt.t = e.t

        return rt
