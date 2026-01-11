"""
test_http_ingest_to_runtime.py
==============================
验证 Step 13 的“端到端最小闭环”：

HTTP POST /v1/inputs
  -> 追加写入 out/input_queue.jsonl（这里用 tmp_path 替代）
  -> runtime 通过 FileQueueGateway pull_inputs()
  -> ingest_inputs 产生 EXTERNAL_INPUT 事件并留痕

我们不启动真实端口服务（避免 flaky）：
- 使用 FastAPI 的 TestClient（进程内模拟 HTTP）
"""

import os
from pathlib import Path

from fastapi.testclient import TestClient

from cim_worldlab.plugins.http_ingest_app import app
from cim_worldlab.world.gateway import FileQueueGateway
from cim_worldlab.world.persistence.file_input_queue import FileInputQueue
from cim_worldlab.world.runtime import WorldRuntime
from cim_worldlab.world.events.external_input import EXTERNAL_INPUT_TYPE


def test_http_post_writes_queue_and_runtime_ingests(tmp_path: Path, monkeypatch):
    # 1) 把 HTTP app 使用的队列路径切到临时目录（不污染真实 out/）
    queue_path = tmp_path / "input_queue.jsonl"
    monkeypatch.setenv("CIM_INPUT_QUEUE_PATH", str(queue_path))

    # 2) 重新导入 app 模块会更复杂，所以我们直接创建本测试用 queue/gateway
    queue = FileInputQueue(path=queue_path)
    gateway = FileQueueGateway(queue=queue)

    client = TestClient(app)

    # 3) 发一个 HTTP 输入
    resp = client.post("/v1/inputs", json={
        "source": "plugin",
        "channel": "equipment",
        "name": "TEMP_READING",
        "data": {"temp_c": 93.0},
        "trace_id": "T-001",
    })
    assert resp.status_code == 200

    # 4) runtime ingest：把文件队列里的新输入拉进世界
    rt = WorldRuntime(gateway=gateway)
    rt.tick()  # 让世界时间变成 1，便于观察输入附着的 t

    events = rt.ingest_inputs()

    assert len(events) == 1
    e = events[0]
    assert e.type == EXTERNAL_INPUT_TYPE
    assert e.t == 1
    assert e.payload["channel"] == "equipment"
    assert e.payload["name"] == "TEMP_READING"
    assert e.payload["data"]["temp_c"] == 93.0
    assert e.payload["trace_id"] == "T-001"
