"""
test_http_ingest_to_runtime.py
==============================
Step 15 加固版测试：使用 create_app(queue_factory=...) 显式注入队列依赖

好处：
- 测试稳定、可控
- 不依赖环境变量的导入时机
- 更符合工业级“依赖注入”写法
"""

from pathlib import Path

from fastapi.testclient import TestClient

from cim_worldlab.plugins.http_ingest_app import create_app
from cim_worldlab.world.gateway import FileQueueGateway
from cim_worldlab.world.persistence.file_input_queue import FileInputQueue
from cim_worldlab.world.runtime import WorldRuntime
from cim_worldlab.world.events.external_input import EXTERNAL_INPUT_TYPE


def test_http_post_writes_queue_and_runtime_ingests(tmp_path: Path):
    queue_path = tmp_path / "input_queue.jsonl"

    # 1) 显式注入队列工厂：每次请求都写到 tmp_path 的文件里
    def queue_factory() -> FileInputQueue:
        return FileInputQueue(path=queue_path)

    app = create_app(queue_factory=queue_factory)
    client = TestClient(app)

    # 2) 发一个 HTTP 输入
    resp = client.post("/v1/inputs", json={
        "source": "plugin",
        "channel": "equipment",
        "name": "TEMP_READING",
        "data": {"temp_c": 93.0},
        "trace_id": "T-001",
    })
    assert resp.status_code == 200

    # 3) runtime ingest：从同一个 queue_path 读新输入
    queue = FileInputQueue(path=queue_path)
    gateway = FileQueueGateway(queue=queue)

    rt = WorldRuntime(gateway=gateway)
    rt.tick()

    events = rt.ingest_inputs()
    assert len(events) == 1

    e = events[0]
    assert e.type == EXTERNAL_INPUT_TYPE
    assert e.t == 1
    assert e.payload["channel"] == "equipment"
    assert e.payload["name"] == "TEMP_READING"
    assert e.payload["data"]["temp_c"] == 93.0
    assert e.payload["trace_id"] == "T-001"
