"""
http_ingest_app.py
==================
HTTP 输入接收服务（FastAPI）

我们在 Step 13 的目标是：
- 外部插件（任何语言）通过 HTTP POST JSON 发送输入
- 服务端把输入写入 FileInputQueue（JSONL 文件）
- WorldRuntime 通过 FileQueueGateway 读取新行，并 ingest 成 EXTERNAL_INPUT 事件

本文件的一个“容易踩坑点”：
- 如果你在模块导入时就创建 queue（队列路径从 env 读取一次），
  那么测试里用 monkeypatch.setenv(...) 改环境变量就不会生效，
  因为 queue 已经初始化完了。

因此我们用 FastAPI 的依赖注入（Dependency Injection）：
- 用 get_queue() 在“每次请求时”读取环境变量并构造队列对象
- 这样测试里 monkeypatch.setenv(...) 就能影响请求行为
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field

from cim_worldlab.world.events.external_input import ExternalInput
from cim_worldlab.world.persistence.file_input_queue import FileInputQueue


# 默认队列文件路径（如果外部没设置 CIM_INPUT_QUEUE_PATH）
DEFAULT_QUEUE_PATH = "out/input_queue.jsonl"

app = FastAPI(title="CIM WorldLab Input Gateway", version="0.1.0")


def get_queue() -> FileInputQueue:
    """
    FastAPI 依赖函数：返回一个 FileInputQueue。

    关键设计：
    - 每次请求都会调用 get_queue()
    - 因此每次请求都会读取最新的环境变量 CIM_INPUT_QUEUE_PATH
    - 测试里 monkeypatch.setenv(...) 就能生效
    """
    path = Path(os.getenv("CIM_INPUT_QUEUE_PATH", DEFAULT_QUEUE_PATH))
    return FileInputQueue(path=path)


class InputIn(BaseModel):
    """
    外部插件发送的 JSON 格式（跨语言稳定协议）。

    字段说明：
    - source：输入来源（plugin/human/system）
    - channel：输入通道（equipment/order/ops...）
    - name：输入事件名（TEMP_READING/NEW_ORDER/PAUSE...）
    - data：任意 JSON 对象（字典）
    - trace_id：可选，用于把多条输入串成一次“外部事务”
    """
    source: str = Field(..., examples=["plugin"])
    channel: str = Field(..., examples=["equipment"])
    name: str = Field(..., examples=["TEMP_READING"])
    data: Dict[str, Any] = Field(default_factory=dict)
    trace_id: Optional[str] = None


@app.get("/health")
def health() -> Dict[str, str]:
    """健康检查：用于监控 / 演示服务存活。"""
    return {"status": "ok"}


@app.post("/v1/inputs")
def post_input(inp: InputIn, queue: FileInputQueue = Depends(get_queue)) -> Dict[str, Any]:
    """
    外部插件投递输入：
    1) 把请求体转成 ExternalInput（payload 的结构化约定）
    2) 写入 FileInputQueue（JSONL 文件追加写）
    3) 返回 ok + 实际写入的 queue_path（方便调试）
    """
    ext = ExternalInput(
        source=inp.source,
        channel=inp.channel,
        name=inp.name,
        data=inp.data,
        trace_id=inp.trace_id,
    )
    queue.append(ext)
    return {"ok": True, "queue_path": str(queue.path)}
