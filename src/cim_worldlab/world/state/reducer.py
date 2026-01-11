"""
reducer.py
==========
这一文件定义：apply_event(state, event) -> new_state

这就是“世界的计算规则”最小雏形。

在很多工程系统/游戏引擎/事件溯源系统里，都有类似结构：
- 事件流（Event Stream）是输入
- reducer（apply_event）把输入转成状态变化

工程意义：
- 你把“世界怎么变化”的规则写成纯函数
- 纯函数最容易测试：给定输入，输出一定确定
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Dict

from cim_worldlab.world.events.event import Event
from cim_worldlab.world.events.external_input import EXTERNAL_INPUT_TYPE
from cim_worldlab.world.state.world_state import WorldState


def apply_event(state: WorldState, e: Event) -> WorldState:
    """
    根据事件 e 推导出新状态（纯函数）。

    使用 dataclasses.replace(state, field=new_value, ...)
    - 它会“基于旧对象复制出一个新对象”
    - 非常适合 immutable state 的更新方式
    """
    # 1) 世界 tick：推进时间与计数
    if e.type == "WORLD_TICK":
        # 在我们的约定里：WORLD_TICK 事件的 t 就是新的世界时间
        # tick_count 也随之 +1（MVP）
        return replace(
            state,
            t=e.t,
            tick_count=state.tick_count + 1,
        )

    # 2) 外部输入：只改变 input_count 和 last_input
    if e.type == EXTERNAL_INPUT_TYPE:
        # last_input：为了教学可读性，我们保存 payload 的摘要
        # 你也可以只保留部分字段，这里先保留整份 payload（MVP）
        return replace(
            state,
            input_count=state.input_count + 1,
            last_input=dict(e.payload),  # 复制一份，避免引用被外部改动
        )

    # 3) 其他事件类型：MVP 先“不改变状态”
    # 以后你加 FDC/SPC/OMS 事件类型时，再在这里扩展规则
    return state


def apply_events(initial: WorldState, events: list[Event]) -> WorldState:
    """
    把一串事件按顺序应用到状态上，得到最终状态。

    这就是 replay 的核心：
    - 初始状态 + 事件序列 = 最终状态
    """
    s = initial
    for e in events:
        s = apply_event(s, e)
    return s
