"""
test_http_schema_validation.py
==============================
验证 Step 16：JSON Schema 校验生效

- source 不在 enum（plugin/human/system）内 => 400
- 缺少必填字段 => 由 Pydantic 或 schema 拦截（这里我们测 schema 的 enum）
"""

from pathlib import Path

from fastapi.testclient import TestClient

from cim_worldlab.plugins.http_ingest_app import create_app
from cim_worldlab.world.persistence.file_input_queue import FileInputQueue


def test_schema_rejects_invalid_source(tmp_path: Path):
    queue_path = tmp_path / "q.jsonl"

    def queue_factory():
        return FileInputQueue(path=queue_path)

    app = create_app(queue_factory=queue_factory, schema_path=Path("schemas/input.schema.json"))
    client = TestClient(app)

    r = client.post("/v1/inputs", json={
        "source": "robot",  # 非法：不在 enum 内
        "channel": "equipment",
        "name": "TEMP_READING",
        "data": {"temp_c": 90},
    })
    assert r.status_code == 400
    assert "Schema validation error" in r.json()["detail"]
