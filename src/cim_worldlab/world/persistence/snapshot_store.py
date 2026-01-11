"""
snapshot_store.py
=================
这一文件实现：SnapshotStore（状态快照存储）

为什么需要快照？
- 事件溯源系统的经典问题：事件越多，回放越慢
- 快照 = “某个时间点的状态存档”
- 回放时：先加载快照，再补上快照之后的事件，速度会大幅提升

我们用最简单的方式实现：
- 快照文件是 JSON
- 内容包含：
  - state: WorldState 的字段
  - last_event_index: 这个快照覆盖到事件日志中的第几条（从 0 开始）
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from cim_worldlab.world.state import WorldState


@dataclass(frozen=True)
class SnapshotStore:
    """
    path: 快照文件路径（例如 out/snapshot.json）
    """
    path: Path

    def save(self, state: WorldState, last_event_index: int) -> None:
        """
        保存快照到 JSON 文件。

        last_event_index：
        - 表示这份 state 是基于 event_log[0..last_event_index] 推导出来的
        - replay_fast 时就能从 last_event_index + 1 开始补事件
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)

        obj: Dict[str, Any] = {
            "last_event_index": last_event_index,
            "state": {
                "t": state.t,
                "tick_count": state.tick_count,
                "input_count": state.input_count,
                "last_input": state.last_input,
            },
        }

        self.path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self) -> Optional[Tuple[WorldState, int]]:
        """
        读取快照。

        返回：
        - None：文件不存在（没有快照）
        - (state, last_event_index)：成功读取
        """
        if not self.path.exists():
            return None

        obj = json.loads(self.path.read_text(encoding="utf-8"))
        s = obj["state"]

        state = WorldState(
            t=int(s["t"]),
            tick_count=int(s["tick_count"]),
            input_count=int(s["input_count"]),
            last_input=s.get("last_input", None),
        )
        last_event_index = int(obj["last_event_index"])
        return state, last_event_index
