"""
file_event_store.py
===================
这一文件实现：FileEventStore（文件事件存储）

你可以把它理解为一个“非常简单但非常工程化”的东西：
- 每发生一个事件 Event，就把它写到一个文件里（追加写 append）
- 文件格式选择 JSONL（JSON Lines）：
  - 每一行是一个 JSON 对象
  - 好处：追加写非常简单，不需要读全文件，不容易损坏
  - 缺点：不是最省空间，但对教学/调试/工程留痕非常友好

为什么要 EventStore（事件存储）？
- EventLog（内存）只能在程序活着时存在，关了就没了
- 工程系统必须“可追溯、可复盘”，所以必须落盘
- 这就是“工程文明”：责任留痕、过程可回放、经验可沉淀

我们会提供两个核心能力：
1) append(event)：把事件追加写入文件
2) load_all()：从文件读出所有事件（用于 replay 回放）
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from cim_worldlab.world.events.event import Event


@dataclass(frozen=True)
class FileEventStore:
    """
    FileEventStore 只保存一个东西：path（文件路径）

    注意：frozen=True
    - 表示一旦创建，就不能改 path（避免运行时乱改路径导致留痕混乱）
    """
    path: Path

    def append(self, e: Event) -> None:
        """
        追加写入一条事件到 JSONL 文件中。

        关键点：
        - 使用 "a" 模式：append（追加）
        - 每写一条就加一个换行符 \n，形成“每行一个 JSON”

        这样即使程序崩溃：
        - 最多丢最后半行（极少）
        - 大部分历史仍然可用
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)

        line_dict = e.to_dict()              # Event -> dict
        line_json = json.dumps(line_dict, ensure_ascii=False)

        with self.path.open("a", encoding="utf-8") as f:
            f.write(line_json + "\n")

    def load_all(self) -> List[Event]:
        """
        读取文件中所有事件（按行解析 JSON）。

        设计说明：
        - 如果文件不存在：返回空列表（表示没有历史）
        - 忽略空行（健壮性）
        - 读出来后重新构造 Event 对象

        这一步就是“回放 replay”的基础：
        - 有了事件序列，就能重建世界
        """
        if not self.path.exists():
            return []

        events: List[Event] = []
        with self.path.open("r", encoding="utf-8") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                obj = json.loads(raw)
                # 这里不做复杂校验，MVP 阶段够用
                events.append(
                    Event(
                        t=int(obj["t"]),
                        type=str(obj["type"]),
                        payload=dict(obj.get("payload", {})),
                    )
                )
        return events
