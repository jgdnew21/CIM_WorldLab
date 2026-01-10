# ----------------------------
# 3) 世界运行时 WorldRuntime（世界会动的心脏）
# ----------------------------
"""
runtime.py
==========
这一文件定义：WorldRuntime（世界运行时）

WorldRuntime 是“世界会动”的最小心脏：
- t：世界时间（tick 计数器）
- tick()：推进世界一步，并产生事件
- event_log：记录发生过的一切事件（可追溯）

这就是你未来的 CIM 世界内核的起点：
- 现在只有 tick
- 以后会有：
  - 外部输入（来自插件/HTTP）
  - 策略决策（policy）
  - 动作执行（action）
  - 度量指标（metrics）
  - 持久化（persistence）
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from cim_worldlab.world.events.event import Event
from cim_worldlab.world.runtime.event_log import EventLog


@dataclass
class WorldRuntime:
    """
    字段解释：
    - t: 当前世界时间（从 0 开始）
    - event_log: 事件日志（默认是一个新的 EventLog）

    dataclass 的 field(default_factory=EventLog) 表示：
    - 每创建一个 WorldRuntime，都会创建一个新的 EventLog
    - 避免多个 WorldRuntime 共用一个日志（严重 bug）
    """
    t: int = 0
    event_log: EventLog = field(default_factory=EventLog)

    def tick(self, payload: Optional[Dict[str, Any]] = None) -> Event:
        """
        推进世界一步，并生成一个事件。

        参数 payload：
        - 可选的 dict（可能为 None）
        - 用来附加这一步的额外信息
          例如：外部输入、观察值、调试信息等

        返回：
        - 本次 tick 产生的 Event

        行为（业务逻辑）：
        1) 世界时间 +1
        2) 产生事件 Event(t=?, type="WORLD_TICK", payload=?)
        3) 写入 event_log
        4) 返回事件（方便调用方马上使用）
        """
        # 1) 推进世界时间
        self.t += 1

        # 2) 构造事件
        e = Event(
            t=self.t,
            type="WORLD_TICK",
            payload=payload or {},  # 如果 payload 为 None，就用空字典
        )

        # 3) 记录事件（留痕）
        self.event_log.append(e)

        # 4) 返回事件给调用方
        return e
