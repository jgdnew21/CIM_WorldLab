"""
file_input_queue.py
===================
FileInputQueue：文件输入队列（JSONL）

它解决一个非常现实的工程问题：
- HTTP Server 和 WorldRuntime 往往是两个进程（甚至两台机器）
- 内存队列无法跨进程共享
- 我们需要一个“最小但可靠”的中介

选择 JSONL（每行一个 JSON）：
- append-only：只追加，不修改历史（留痕）
- 写入简单：一条输入就是一行
- 读取简单：按行读，并用 cursor 记住读到哪一行

消费模型：
- 生产者（HTTP server）：append(input)
- 消费者（world runtime）：read_since(cursor) -> (items, new_cursor)

cursor 是一个整数：表示“已经消费到第几行”
例如：
- cursor=0：表示还没消费任何行
- read_since(0) 返回第 0 行开始的全部输入，并返回 new_cursor = 总行数
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from cim_worldlab.world.events.external_input import ExternalInput


@dataclass(frozen=True)
class FileInputQueue:
    """
    path：队列文件路径，例如 out/input_queue.jsonl
    """
    path: Path

    def append(self, inp: ExternalInput) -> None:
        """
        追加一条外部输入到 JSONL 文件中。

        重要：append-only
        - 只追加，不覆盖
        - 输入历史天然可追溯
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)

        obj = {
            "source": inp.source,
            "channel": inp.channel,
            "name": inp.name,
            "data": inp.data,
        }
        if inp.trace_id is not None:
            obj["trace_id"] = inp.trace_id

        line = json.dumps(obj, ensure_ascii=False)

        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def read_since(self, cursor: int) -> Tuple[List[ExternalInput], int]:
        """
        从 cursor 开始读取“新输入”，并返回 (inputs, new_cursor)。

        cursor 含义：
        - cursor=0：从第 0 行开始读
        - cursor=n：跳过前 n 行，从第 n 行开始读

        new_cursor：
        - 读取完成后，new_cursor = 文件总行数
        - 下次再读，用 new_cursor 作为 cursor，就不会重复读取
        """
        if not self.path.exists():
            return [], cursor

        inputs: List[ExternalInput] = []
        total_lines = 0

        with self.path.open("r", encoding="utf-8") as f:
            for idx, raw in enumerate(f):
                total_lines += 1
                if idx < cursor:
                    continue

                raw = raw.strip()
                if not raw:
                    continue

                obj = json.loads(raw)
                inputs.append(
                    ExternalInput(
                        source=obj["source"],
                        channel=obj["channel"],
                        name=obj["name"],
                        data=dict(obj.get("data", {})),
                        trace_id=obj.get("trace_id"),
                    )
                )

        return inputs, total_lines
