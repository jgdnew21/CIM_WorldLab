# CIM_WorldLab 分层地图（runtime / state / policy / metrics / cli）

## 1) runtime 层（编排与事件主循环）

核心文件：
- `src/cim_worldlab/world/runtime/runtime.py`
- `src/cim_worldlab/world/runtime/event_log.py`

职责：
- 维护 `WorldRuntime`：`tick()`、`ingest_inputs()`、`_record()` 统一事件入口。
- 在 `_record()` 中串联：事件写入 `EventLog` / `FileEventStore`、状态推进（`apply_event`）、策略评估（`evaluate_event`）、动作留痕（`ACTION_EXECUTED`）。
- 提供 `metrics()`（调用 metrics 层）与 replay / snapshot 能力（对接 persistence）。

## 2) state 层（纯函数状态演化）

核心文件：
- `src/cim_worldlab/world/state/world_state.py`
- `src/cim_worldlab/world/state/reducer.py`

职责：
- 定义不可变状态 `WorldState`（`frozen=True`）。
- 通过 `apply_event` / `apply_events` 把事件序列映射为确定性状态。
- 目前处理三类关键事件：`WORLD_TICK`、`EXTERNAL_INPUT`、`ACTION_EXECUTED`。

## 3) policy 层（规则判断，纯决策）

核心文件：
- `src/cim_worldlab/world/policy/engine.py`
- `src/cim_worldlab/world/events/policy_decision.py`

职责：
- `evaluate_event(e)` 对输入事件做规则判断，只返回 `PolicyDecision`（不直接写日志、不改状态）。
- 当前规则聚焦设备温度：`TEMP_READING` 且 `temp_c > threshold` 时输出建议动作。
- 由 runtime 把 `PolicyDecision` 转成事件并继续走统一 `_record()`。

## 4) metrics 层（可观测快照）

核心文件：
- `src/cim_worldlab/world/metrics/compute.py`
- `src/cim_worldlab/world/metrics/world_metrics.py`

职责：
- `compute_metrics(state, event_log)` 从“权威状态 + 事件历史”生成 `WorldMetrics`。
- 提供 `inputs_by_channel`、`last_input_summary`、`action_count`、`last_action_summary` 等看板字段。
- 保持纯函数，支持稳定 replay 与测试。

## 5) cli 层（入口与用例编排）

核心文件：
- `src/cim_worldlab/cli/main.py`
- `src/cim_worldlab/cli/commands.py`
- `src/cim_worldlab/cli/config.py`

职责：
- `main.py`：argparse 路由 `serve` / `run-once` / `run` / `replay`。
- `commands.py`：落地命令业务（构建 runtime、tick+ingest、保存 cursor、触发 snapshot/replay、打印指标）。
- 把 runtime 的核心能力包装成可操作的 CLI 工作流。

---

## 端到端调用链（从输入到输出）

### A. 在线运行链（run-once / run）
1. 用户执行 `cim_worldlab run-once`（CLI 入口）。
2. `cli.main.main()` 调度到 `cmd_run_once()`。
3. `cmd_run_once()` 通过 `build_runtime_for_cli()` 组装 `WorldRuntime`（含 `FileQueueGateway`、`FileEventStore`、cursor）。
4. 调用 `rt.tick()`：生成 `WORLD_TICK`，进入 `rt._record()`。
5. `rt.ingest_inputs()`：从 gateway 拉输入，转 `EXTERNAL_INPUT`，逐条进入 `_record()`。
6. `_record()` 内部顺序：
   - 事件写入 `event_log` / `event_store`；
   - `apply_event` 更新 `state` 与 `t`；
   - `evaluate_event` 产出决策；
   - 决策转 `POLICY_DECISION` 并再次 `_record()`；
   - 再生成 `ACTION_EXECUTED` 并 `_record()`。
7. `rt.metrics()` 调 `compute_metrics(state, event_log)` 生成指标。
8. CLI 保存 cursor、可选 snapshot，并输出 JSON 或 pretty 文本。

### B. 复盘链（replay）
1. 用户执行 `cim_worldlab replay`。
2. `cmd_replay()` 选择 `replay_fast_from_store()` 或 `replay_from_store()`。
3. replay 过程中通过 `apply_events` 还原最终 `WorldState`。
4. 回放完成后调用 `rt.metrics()` 输出同构指标视图。

### C. 分层依赖方向（高层 -> 低层）
- `cli` -> `runtime` -> (`state`, `policy`, `metrics`, `gateway/persistence`)
- `policy` 只依赖事件模型，不反向依赖 runtime。
- `state` / `metrics` 保持纯计算，便于测试与 replay 一致性。
