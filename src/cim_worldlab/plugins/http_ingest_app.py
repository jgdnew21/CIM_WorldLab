"""
http_ingest_app.py
==================
Step 16 加固版：加入 JSON Schema 校验（跨语言协议契约）

你现在具备三层“输入合法性保证”：
1) Pydantic：字段类型/基本结构（Python 侧）
2) JSON Schema：跨语言契约一致（工业协作）
3) 写入 FileInputQueue：append-only 留痕

注意：
- Schema 校验失败返回 400（Bad Request）
- 这和“字段缺失/类型错误”很匹配
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional, Callable

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from cim_worldlab.world.events.external_input import ExternalInput
from cim_worldlab.world.persistence.file_input_queue import FileInputQueue
from cim_worldlab.plugins.schema_validation import load_schema, validate_or_raise


DEFAULT_QUEUE_PATH = "out/input_queue.jsonl"
DEFAULT_SCHEMA_PATH = Path("schemas/input.schema.json")


class InputIn(BaseModel):
    source: str = Field(..., examples=["plugin"])
    channel: str = Field(..., examples=["equipment"])
    name: str = Field(..., examples=["TEMP_READING"])
    data: Dict[str, Any] = Field(default_factory=dict)
    trace_id: Optional[str] = None


def default_queue_factory() -> FileInputQueue:
    path = Path(os.getenv("CIM_INPUT_QUEUE_PATH", DEFAULT_QUEUE_PATH))
    return FileInputQueue(path=path)


def create_app(
    queue_factory: Callable[[], FileInputQueue] = default_queue_factory,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
) -> FastAPI:
    """
    app 工厂：支持注入 queue_factory，并加载 input.schema.json 用于校验。
    """
    app = FastAPI(title="CIM WorldLab Input Gateway", version="0.3.0")

    # 启动时加载 schema（一次即可）
    schema = load_schema(schema_path)

    def get_queue() -> FileInputQueue:
        return queue_factory()

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/inputs")
    def post_input(inp: InputIn, queue: FileInputQueue = Depends(get_queue)) -> Dict[str, Any]:
        # 1) 把 Pydantic 模型转成 dict（准备做 JSON Schema 校验）
        payload = inp.model_dump()

        # 2) JSON Schema 校验（跨语言契约）
        try:
            validate_or_raise(payload, schema)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # 3) 写入队列
        ext = ExternalInput(
            source=inp.source,
            channel=inp.channel,
            name=inp.name,
            data=inp.data,
            trace_id=inp.trace_id,
        )
        queue.append(ext)
        return {"ok": True, "queue_path": str(queue.path)}

    return app


app = create_app()
