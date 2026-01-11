"""
http_server.py
==============
启动 HTTP 输入接收服务（uvicorn）

用法：
  CIM_INPUT_QUEUE_PATH=out/input_queue.jsonl python -m cim_worldlab serve

说明：
- uvicorn 指向 cim_worldlab.plugins.http_ingest_app:app
- app 是通过 create_app() 创建的默认实例（依赖从 env 读取）
"""

from __future__ import annotations

import os
import uvicorn


def main() -> None:
    host = os.getenv("CIM_HTTP_HOST", "127.0.0.1")
    port = int(os.getenv("CIM_HTTP_PORT", "8000"))

    uvicorn.run(
        "cim_worldlab.plugins.http_ingest_app:app",
        host=host,
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()
