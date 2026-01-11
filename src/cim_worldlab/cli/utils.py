"""
utils.py
========
CLI 常用小工具函数

我们把“文件游标 cursor”的读写提取出来：
- cursor 用于增量消费 input_queue.jsonl
- 避免每次 run-once 都从头 ingest（否则会重复消费）
"""

from __future__ import annotations

from pathlib import Path


def load_int(path: Path, default: int = 0) -> int:
    """
    从文件读取一个整数（例如 cursor）。
    - 文件不存在：返回 default
    - 内容为空：返回 default
    """
    if not path.exists():
        return default
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return default
    return int(raw)


def save_int(path: Path, value: int) -> None:
    """
    把整数写入文件（覆盖写）。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(value), encoding="utf-8")
