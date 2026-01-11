"""
schema_validation.py
====================
JSON Schema 校验工具（Step 16）

为什么要 JSON Schema？
- Pydantic 很适合 Python 内部验证
- 但“跨语言协议”最通用的表达方式是 JSON Schema
- 你把 schema 放在 schemas/ 目录，相当于给全世界一个“契约文件”
- Node/Go/Java 都能读同一个 schema 来生成类型或做校验

本文件提供：
- load_schema(path): 读取 schema JSON
- validate_or_raise(payload, schema): 校验 payload，不通过就抛出 ValueError（含可读错误）
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from jsonschema import Draft202012Validator


def load_schema(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_or_raise(payload: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """
    校验 payload 是否符合 schema。

    如果不符合：
    - 抛出 ValueError，信息里包含“哪一个字段”不合法
    """
    v = Draft202012Validator(schema)
    errors = sorted(v.iter_errors(payload), key=lambda e: e.path)

    if not errors:
        return

    # 只取第一条错误，保证返回信息简洁（MVP）
    e = errors[0]
    # e.path 是一个 deque，表示出错字段路径
    path = ".".join([str(p) for p in e.path]) if e.path else "(root)"
    raise ValueError(f"Schema validation error at {path}: {e.message}")
