"""
send_inputs.py
==============
示例插件（Python）——向 CIM WorldLab 的 ingest server 发送输入

这份代码的“教学价值”：
- 它就是外部插件的最小形态（跨语言协议）
- 你以后用 Node/Go/Java 写插件，逻辑也一样：HTTP POST JSON

运行方式：
  source .venv/bin/activate
  python plugins/examples/http_python/send_inputs.py --n 3

前提：
- 你已经启动了 server：
  python -m cim_worldlab serve --port 8000
"""

from __future__ import annotations

import argparse
import time
from typing import Any, Dict

import httpx


def post_input(base_url: str, payload: Dict[str, Any]) -> None:
    """
    向 /v1/inputs POST 一条输入。
    """
    r = httpx.post(f"{base_url}/v1/inputs", json=payload, timeout=5.0)
    r.raise_for_status()
    print("POST OK:", r.json())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8000")
    ap.add_argument("--n", type=int, default=3, help="send N demo inputs")
    ap.add_argument("--sleep", type=float, default=0.2, help="sleep between inputs")
    args = ap.parse_args()

    for i in range(args.n):
        payload = {
            "source": "plugin",
            "channel": "equipment",
            "name": "TEMP_READING",
            "data": {"temp_c": 90.0 + i},
            "trace_id": f"PLUGIN-DEMO-{i}",
        }
        post_input(args.base_url, payload)
        time.sleep(args.sleep)


if __name__ == "__main__":
    main()
