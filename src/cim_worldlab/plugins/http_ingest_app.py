"""
http_ingest_app.py
==================
Step 15 工程化加固版：FastAPI app 工厂化 + 依赖注入更彻底

你现在的 ingest 服务是一个“边界服务”（boundary service）：
- 只接收输入（HTTP POST JSON）
- 不跑世界，不做业务判断
- 把输入写入 FileInputQueue（JSONL）

为什么要做 create_app()？
- 工程系统要可测试、可配置、可部署
- 如果 app 在模块导入时就绑定死依赖（例如固定 queue），测试会很难写
- create_app(queue=...) 让依赖“显式注入”，这是工业级做法

我们仍保留：
- app：默认实例（用于 uvicorn 直接启动）
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional, Callable

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field

from cim_worldlab.world.events.external_input import ExternalInput
from cim_worldlab.world.persistence.file_input_queue import FileInputQueue


DEFAULT_QUEUE_PATH = "out/input_queue.jsonl"


class InputIn(BaseModel):
    """
    外部插件发送的 JSON 协议（跨语言稳定）：

    source: plugin/human/system
    channel: equipment/order/ops/...
    name: TEMP_READING/NEW_ORDER/PAUSE/...
    data: 任意 JSON 对象（字典）
    trace_id: 可选，用于把多条输入串成一个外部事务
    """
    source: str = Field(..., examples=["plugin"])
    channel: str = Field(..., examples=["equipment"])
    name: str = Field(..., examples=["TEMP_READING"])
    data: Dict[str, Any] = Field(default_factory=dict)
    trace_id: Optional[str] = None


def default_queue_factory() -> FileInputQueue:
    """
    默认队列工厂：从环境变量读取路径。
    这是“部署友好”的方式：不用改代码，只改 env 即可。
    """
    path = Path(os.getenv("CIM_INPUT_QUEUE_PATH", DEFAULT_QUEUE_PATH))
    return FileInputQueue(path=path)


def create_app(queue_factory: Callable[[], FileInputQueue] = default_queue_factory) -> FastAPI:
    """
    app 工厂函数：创建一个 FastAPI app。

    参数：
    - queue_factory：返回 FileInputQueue 的可调用对象
      - 默认：从环境变量读取
      - 测试：可以注入一个固定路径/内存替身（更可控）

    FastAPI 的依赖注入本质：
    - Depends(get_queue) 每次请求都会调用 get_queue()
    - 我们的 get_queue 内部调用 queue_factory()
    - 因此 queue_factory 就是你可注入、可替换的“依赖源”
    """
    app = FastAPI(title="CIM WorldLab Input Gateway", version="0.2.0")

    def get_queue() -> FileInputQueue:
        return queue_factory()

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/inputs")
    def post_input(inp: InputIn, queue: FileInputQueue = Depends(get_queue)) -> Dict[str, Any]:
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


# 默认 app 实例：给 uvicorn 使用
app = create_app()
