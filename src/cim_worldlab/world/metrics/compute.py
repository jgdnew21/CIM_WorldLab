"""
compute.py
==========
这一文件定义：compute_metrics(state, event_log) -> WorldMetrics

重要设计：我们用“纯函数”来计算指标
- 纯函数：同样输入 -> 同样输出，没有副作用
- 好处：容易测试、容易回放、容易教学解释

计算指标的数据来源：
1) state：已经由 reducer 推导好的“权威状态”（快）
2) event_log：历史事件（可用于细分统计、追溯、debug）

MVP：
- inputs_by_channel：我们从 event_log 扫一遍统计
  （事件少时很简单；事件多时未来可做增量缓存）
"""

from __future__ import annotations

from typing import Dict, Optional

from cim_worldlab.world.events.external_input import EXTERNAL_INPUT_TYPE
from cim_worldlab.world.runtime.event_log import EventLog
from cim_worldlab.world.state import WorldState
from cim_worldlab.world.metrics.world_metrics import WorldMetrics


def compute_metrics(state: WorldState, event_log: EventLog) -> WorldMetrics:
    """
    从 state + event_log 计算出一个指标快照 WorldMetrics。
    """
    # 1) 统计 inputs_by_channel
    inputs_by_channel: Dict[str, int] = {}

    for e in event_log.all():
        if e.type != EXTERNAL_INPUT_TYPE:
            continue
        channel = str(e.payload.get("channel", "UNKNOWN"))
        inputs_by_channel[channel] = inputs_by_channel.get(channel, 0) + 1

    # 2) last_input_summary：从 state.last_input 提炼简要信息（更适合“看板”）
    last_input_summary: Optional[Dict[str, str]] = None
    if state.last_input is not None:
        last_input_summary = {
            "source": str(state.last_input.get("source", "")),
            "channel": str(state.last_input.get("channel", "")),
            "name": str(state.last_input.get("name", "")),
        }

    return WorldMetrics(
        t=state.t,
        tick_count=state.tick_count,
        input_count=state.input_count,
        inputs_by_channel=inputs_by_channel,
        last_input_summary=last_input_summary,
    )
