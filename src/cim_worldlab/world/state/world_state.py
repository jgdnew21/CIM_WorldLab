"""
world_state.py
==============
这一文件定义：WorldState（世界状态）

你可以把“事件”和“状态”这样理解：

- Event（事件）：发生过什么（事实记录，可留痕、可回放）
- State（状态）：当前世界是什么样（由历史事件推导出来）

为什么要把 State 单独做出来？
1) 工程可解释：状态 = 事件的结果，不是“拍脑袋写死”
2) 可回放：只要有事件，就能重建状态（哪怕程序重启、跨天）
3) 易测试：对同一串事件，状态必须一致（可验证）

MVP 版本的 WorldState 我们先只放几个“看得见”的字段：
- t: 世界时间（最后一个 WORLD_TICK 的 t）
- tick_count: 世界 tick 的次数（与 t 在 MVP 中相同，但未来可能不相同）
- input_count: ingest 的外部输入事件数量（EXTERNAL_INPUT 的累计）
- last_input: 最近一次外部输入的摘要（用于教学观察/调试）
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class WorldState:
    """
    frozen=True：不可变状态（immutable state）

    好处：
    - reducer 每次返回“新状态”，不会在原对象上偷偷改字段
    - 回放时更安全：不会因为某次修改污染历史
    - 对教学非常友好：你能清晰解释“新状态从哪里来”

    注意：
    - 不可变并不代表不能更新，而是“更新 = 产生一个新对象”
    """
    t: int
    tick_count: int
    input_count: int
    last_input: Optional[Dict[str, Any]]

    @staticmethod
    def initial() -> "WorldState":
        """
        返回世界初始状态（世界刚诞生，啥也没发生）。
        """
        return WorldState(
            t=0,
            tick_count=0,
            input_count=0,
            last_input=None,
        )
