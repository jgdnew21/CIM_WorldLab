# src/cim_worldlab/world/events/action_executed.py
"""
ACTION_EXECUTED 事件（Step18）

为什么要有 ACTION_EXECUTED？
- POLICY_DECISION：是“判断/建议”（我认为应该怎么做、为什么）
- ACTION_EXECUTED：是“动作已执行的留痕”（我真的做了什么、为什么、关联哪个决策）

这两者拆开非常重要：
- 可复盘：你可以看到“建议了什么” vs “实际上做了什么”
- 可 replay：事件回放时，状态能重建动作轨迹
- 可扩展：以后接真实设备/工艺，只需要把“动作执行”替换为真实执行即可

本事件 payload 设计（MVP，最小可用）：
- action_type: str        动作类型（例如 "SLOW_DOWN"/"STOP"/"OBSERVE"/"NOOP"）
- reason: str             为什么执行这个动作（投屏友好）
- from_policy_t: int|None 关联的 POLICY_DECISION 事件时间戳（最小追溯；如果未来有 event_id 可替换）
- trace_id: str|None      链路追踪（可选，跟 ExternalInput/PolicyDecision 一致）
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from cim_worldlab.world.events.event import Event

ACTION_EXECUTED_TYPE = "ACTION_EXECUTED"


@dataclass(frozen=True)
class ActionExecuted:
    """
    ActionExecuted 是 payload 的“结构化约定”。

    你仍然可以直接写 Event(t, type, payload)。
    但提供这个类的好处是：
    - 约束字段命名（团队不容易写出五花八门的 payload）
    - 更好读、更好测试
    """

    action_type: str
    reason: str
    from_policy_t: Optional[int] = None
    trace_id: Optional[str] = None

    def to_event(self, t: int) -> Event:
        payload: Dict[str, Any] = {
            "action_type": self.action_type,
            "reason": self.reason,
            "from_policy_t": self.from_policy_t,
        }
        if self.trace_id is not None:
            payload["trace_id"] = self.trace_id
        return Event(t=t, type=ACTION_EXECUTED_TYPE, payload=payload)
