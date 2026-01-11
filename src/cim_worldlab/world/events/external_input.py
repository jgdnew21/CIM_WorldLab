"""
external_input.py
=================
这一文件做一件事：把“外部输入”这类事件规范化。

重要设计选择：
- 我们仍然使用通用 Event(t, type, payload)
- 但我们提供“构造函数”和“字段约定”，避免每个人随意写 payload

为什么不直接写 payload？
- 工程系统最怕“字段随意、口口相传、后来人看不懂”
- 所以我们要把约定变成代码（让它可阅读、可测试、可复用）

外部输入的典型来源：
- 设备插件：温度、压力、告警、状态机变化
- 订单系统：新订单、取消订单、优先级变化
- 人工操作：暂停/恢复、切换配方、确认放行
"""

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional

from cim_worldlab.world.events.event import Event

# 外部输入事件的 type：用常量，避免手写字符串写错
EXTERNAL_INPUT_TYPE = "EXTERNAL_INPUT"

# 你可以把 source 理解为“输入从哪里来”
InputSource = Literal["plugin", "human", "system"]


@dataclass(frozen=True)
class ExternalInput:
    """
    ExternalInput 是 payload 的“结构化约定”。

    注意：
    - 它不是一个新的 Event（我们仍然用 Event）
    - 它是 Event.payload 的“规范模板”

    字段解释：
    - source: 输入来源（插件/人/系统）
    - channel: 通道名（例如 "equipment", "order", "ops"）
    - name: 事件名（例如 "TEMP_READING", "NEW_ORDER", "PAUSE"）
    - data: 具体数据（必须是可 JSON 化结构）
    - trace_id: 可选，用于把多条输入串成一次“外部事务”
    """
    source: InputSource
    channel: str
    name: str
    data: Dict[str, Any]
    trace_id: Optional[str] = None

    def to_event(self, t: int) -> Event:
        """
        把 ExternalInput 转成世界内部统一 Event。

        关键点：Event.type 固定为 EXTERNAL_INPUT
        具体的输入内容都放在 payload 里，方便跨语言/跨协议传输。
        """
        payload: Dict[str, Any] = {
            "source": self.source,
            "channel": self.channel,
            "name": self.name,
            "data": self.data,
        }
        if self.trace_id is not None:
            payload["trace_id"] = self.trace_id

        return Event(t=t, type=EXTERNAL_INPUT_TYPE, payload=payload)
