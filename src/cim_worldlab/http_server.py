"""
http_server.py
==============
一个非常小的启动器：用 uvicorn 启动 http_ingest_app。

你以后会常用它做课堂演示：
- 开一个窗口跑 server
- 另一个窗口跑 runtime（世界）
- 插件（甚至用 curl）往 server 发输入
- 世界通过 FileQueueGateway 拉取输入并产生 EXTERNAL_INPUT 事件
"""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    host = os.getenv("CIM_HTTP_HOST", "127.0.0.1")
    port = int(os.getenv("CIM_HTTP_PORT", "8000"))

    # 这里用 "module:app" 形式，让 uvicorn 热重载等功能更标准
    uvicorn.run(
        "cim_worldlab.plugins.http_ingest_app:app",
        host=host,
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()
