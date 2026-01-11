/**
 * send_inputs.mjs
 * ==============
 * Node.js 示例插件：向 CIM WorldLab ingest server 发送输入
 *
 * 运行前：
 *  1) 先启动 server：
 *     python -m cim_worldlab serve --port 8000
 *
 * 运行：
 *  node plugins/examples/http_node/send_inputs.mjs --n 5
 *
 * 说明：
 *  - Node 18+ 自带 fetch，无需安装依赖
 *  - 这份代码就是“跨语言插件接入”的最小模板
 */

function parseArgs() {
  const args = process.argv.slice(2);
  const out = { baseUrl: "http://127.0.0.1:8000", n: 3, sleepMs: 200 };
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === "--base-url") out.baseUrl = args[++i];
    else if (a === "--n") out.n = Number(args[++i]);
    else if (a === "--sleep-ms") out.sleepMs = Number(args[++i]);
  }
  return out;
}

async function postInput(baseUrl, payload) {
  const r = await fetch(`${baseUrl}/v1/inputs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await r.json();
  if (!r.ok) {
    throw new Error(`HTTP ${r.status}: ${JSON.stringify(data)}`);
  }
  console.log("POST OK:", data);
}

function sleep(ms) {
  return new Promise((res) => setTimeout(res, ms));
}

async function main() {
  const { baseUrl, n, sleepMs } = parseArgs();
  for (let i = 0; i < n; i++) {
    const payload = {
      source: "plugin",
      channel: "equipment",
      name: "TEMP_READING",
      data: { temp_c: 90 + i },
      trace_id: `NODE-DEMO-${i}`,
    };
    await postInput(baseUrl, payload);
    await sleep(sleepMs);
  }
}

main().catch((e) => {
  console.error("ERROR:", e.message);
  process.exit(1);
});
