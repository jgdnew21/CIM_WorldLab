"""
file_event_store.py
===================
FileEventStore：JSONL 事件存储（每行一个 JSON）

Step 8 我们已有：
- append(event): 追加写入
- load_all(): 读取全部事件

Step 12 新增：
- load_from_index(start_index): 从第 start_index 条开始读取（用于快照后补事件）
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from cim_worldlab.world.events.event import Event


@dataclass(frozen=True)
class FileEventStore:
    path: Path

    def append(self, e: Event) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line_json = json.dumps(e.to_dict(), ensure_ascii=False)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line_json + "\n")

    def load_all(self) -> List[Event]:
        return self.load_from_index(0)

    def load_from_index(self, start_index: int) -> List[Event]:
        """
        从 JSONL 文件中读取事件，从第 start_index 条开始（0-based）。

        例子：
        - start_index=0：读全部
        - start_index=10：跳过前 10 条，只读后面的
        """
        if not self.path.exists():
            return []

        events: List[Event] = []
        with self.path.open("r", encoding="utf-8") as f:
            for idx, raw in enumerate(f):
                if idx < start_index:
                    continue
                raw = raw.strip()
                if not raw:
                    continue
                obj = json.loads(raw)
                events.append(
                    Event(
                        t=int(obj["t"]),
                        type=str(obj["type"]),
                        payload=dict(obj.get("payload", {})),
                    )
                )
        return events
