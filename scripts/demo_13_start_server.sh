#!/usr/bin/env bash
set -euo pipefail

# ===========================
# Step 13 Demo - Server Side
# ===========================
# 这个脚本启动 HTTP Server：
# - 外部插件用 HTTP POST /v1/inputs 投递输入
# - Server 把输入追加写到 JSONL 文件（FileInputQueue）
#
# 你会看到一个文件不断增长：
#   out/demo_input_queue.jsonl
#
# 注意：
# - 这个脚本会阻塞在前台（因为 server 在跑）
# - 演示时请开一个终端窗口专门跑它

export CIM_INPUT_QUEUE_PATH="out/demo_input_queue.jsonl"
export CIM_HTTP_HOST="127.0.0.1"
export CIM_HTTP_PORT="8000"

echo "== Step13 Demo Server =="
echo "Queue file: $CIM_INPUT_QUEUE_PATH"
echo "Listening : http://$CIM_HTTP_HOST:$CIM_HTTP_PORT"
echo ""
echo "Try health check:"
echo "  curl http://$CIM_HTTP_HOST:$CIM_HTTP_PORT/health"
echo ""

python -m cim_worldlab.http_server
