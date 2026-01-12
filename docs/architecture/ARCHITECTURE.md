太好了，这一步**非常适合“学习 & 整理模式”**。
我会直接帮你把 `docs/architecture/ARCHITECTURE.md` **升级成一页“分层地图”**，风格是：

* ✅ **一页就能看懂全系统**
* ✅ 面向「工程学习 / 教学 / 复盘」
* ✅ 不讲实现细节，只讲**分层职责 + 建模逻辑**
* ✅ 完全贴合你现在的 **真实目录结构（Step18 已完成态）**

你可以**整页直接覆盖原文件**，或另存为 `ARCHITECTURE_MAP.md`。

---

# CIM_WorldLab Architecture Map

**（一页分层地图 / Architecture at a Glance）**

---

## 一、系统一句话定义（System Statement）

**CIM_WorldLab 是一个「事件驱动、可回放、可解释的世界模拟系统」。**

它把现实世界中的工程过程拆解为：

> **事实 → 判断 → 执行 → 记忆 → 汇报**

并用清晰的分层结构，把这些过程变成**可测试、可教学、可复盘的工程系统**。

---

## 二、整体分层总览（Layer Overview）

```
┌───────────────────────────────┐
│        Presentation Layer     │
│   CLI / HTTP / Scripts        │
└───────────────▲───────────────┘
                │
┌───────────────┴───────────────┐
│        Runtime Orchestration  │
│      world/runtime            │
└───────────────▲───────────────┘
                │
┌───────────────┴───────────────┐
│   Domain Core (The World)     │
│ events / policy / state       │
│ reducer / actions             │
└───────────────▲───────────────┘
                │
┌───────────────┴───────────────┐
│   Observation & Memory        │
│ metrics / persistence         │
└───────────────▲───────────────┘
                │
┌───────────────┴───────────────┐
│   External World Interface    │
│ gateway / plugins             │
└───────────────────────────────┘
```

---

## 三、各层职责说明（What Each Layer Does）

### 1️⃣ Presentation Layer（入口与展示层）

**位置**

```
src/cim_worldlab/cli
src/cim_worldlab/http_server.py
scripts/
plugins/examples/
```

**职责**

* 提供 CLI / HTTP 接口
* 把外部输入送入系统
* 把系统结果以「人能读懂」的方式展示

**不负责**

* 不理解业务规则
* 不维护世界状态
* 不产生判断逻辑

👉 **现实对应**：操作台 / 调试终端 / 教学投屏

---

### 2️⃣ Runtime Orchestration（运行编排层）

**位置**

```
src/cim_worldlab/world/runtime/
```

**职责**

* 世界的“主循环 / 调度器”
* 接收输入事件
* 调用 policy 生成判断
* 自动生成 ACTION_EXECUTED 留痕
* 统一 record 事件（log / state / persistence）

**核心原则**

* runtime 只**编排流程**
* 不直接写业务规则
* 不直接算指标

👉 **现实对应**：工厂调度系统 / 中控系统

---

### 3️⃣ Domain Core – The World（世界核心层）

这是系统的“工程文明核心”。

#### 3.1 Events（世界发生了什么）

```
src/cim_worldlab/world/events/
```

* Event / ExternalInput / PolicyDecision / ActionExecuted
* 所有“发生过的事”都必须变成事件

👉 **现实对应**：黑匣子 / 生产履历 / 审计日志

---

#### 3.2 Policy（世界如何判断）

```
src/cim_worldlab/world/policy/
```

* 把事实（EXTERNAL_INPUT）转化为判断（POLICY_DECISION）
* 输出 `suggested_action` + `reason`

👉 **现实对应**：SOP / 工程经验 / 规则引擎
👉 **关键建模原则**：判断 ≠ 执行

---

#### 3.3 Actions（世界能做什么）

```
src/cim_worldlab/world/actions/
```

* 定义系统“可以采取的动作语义”
* 不负责是否执行

👉 **现实对应**：停机 / 降速 / 报警 / 切换策略等动作字典

---

#### 3.4 State + Reducer（世界现在是什么样）

```
src/cim_worldlab/world/state/
```

* `WorldState`：世界当前快照
* `reducer`：纯函数
  `state + event → new_state`

**核心原则**

* state 不可变（或逻辑上不可变）
* reducer 无副作用
* 世界状态可回放、可复现

👉 **现实对应**：工厂当前状态 / 系统内存态

---

### 4️⃣ Observation & Memory（观察与记忆层）

#### 4.1 Metrics（管理视角）

```
src/cim_worldlab/world/metrics/
```

* 从 `state + event_log` 计算指标
* 例如：action_count / last_action_summary

👉 **现实对应**：老板仪表盘 / 监控看板
👉 **原则**：只读、不改世界

---

#### 4.2 Persistence（历史存档 / 回放）

```
src/cim_worldlab/world/persistence/
out/
```

* event log / snapshot
* replay / rewind / fast replay

👉 **现实对应**：事故复盘 / 教学回放 / 审计留档

---

### 5️⃣ External World Interface（外部世界接口层）

```
src/cim_worldlab/world/gateway/
src/cim_worldlab/plugins/
schemas/
```

**职责**

* 接收外部世界输入
* 校验 schema
* 转化为 EXTERNAL_INPUT 事件

👉 **现实对应**：传感器、人工录入、外部系统

---

## 四、一次完整世界运行路径（End-to-End）

```
外部输入
  ↓
gateway → EXTERNAL_INPUT
  ↓
runtime
  ↓
policy → POLICY_DECISION
  ↓
runtime → ACTION_EXECUTED
  ↓
reducer → WorldState 更新
  ↓
metrics → 指标快照
  ↓
CLI / HTTP / out 文件
```

---

## 五、架构设计的核心价值（Why This Architecture）

* ✅ **可解释**：每个判断、每个动作都有 reason
* ✅ **可回放**：事件驱动，历史可重建
* ✅ **可测试**：纯函数 reducer / metrics
* ✅ **可教学**：工程直觉 → 系统实现 → 文明抽象

---

## 六、架构一句话总结（Architecture Mantra）

> **Event 是历史，
> State 是现在，
> Reducer 是规律，
> Runtime 是编排，
> Metrics 是观察。**

---

太好了，这一步**非常“工程教材级”**。
我直接给你一页 **《字段血缘总览附录（Field Lineage Appendix）》**，可以**原样追加**到
`docs/architecture/ARCHITECTURE.md` 末尾，作为 **Appendix A**。

这页的目标不是“列字段”，而是**让读者一眼看懂：字段如何承载责任与因果**。

---

# Appendix A · Field Lineage Map

**（字段血缘总览附录）**

> 本附录回答一个核心问题：
> **系统里的每一个关键字段，从哪里来，经过哪里，最终服务谁。**

---

## A.1 字段血缘的基本原则（先读）

在 CIM_WorldLab 中，字段不是“数据属性”，而是**责任载体**：

* **事实字段**：描述世界发生了什么（不可争辩）
* **判断字段**：描述系统/人怎么看这件事（可质询）
* **执行字段**：描述系统真正做了什么（可追责）
* **汇总字段**：描述系统整体运行状况（给人决策）

字段血缘，就是把这四类字段串成一条**可回放的工程因果链**。

---

## A.2 核心字段血缘总览（全景图 · 文本版）

```
【外部世界】
  value / channel
        ↓
【事实事件】
  EXTERNAL_INPUT
        ↓
【判断事件】
  POLICY_DECISION
    ├─ suggested_action
    ├─ reason
    ├─ severity
    └─ rule_id
        ↓
【执行事件】
  ACTION_EXECUTED
    ├─ action_type
    ├─ reason
    ├─ from_policy_t
    └─ trace_id
        ↓
【世界状态】
  WorldState
    ├─ last_action
    └─ action_count
        ↓
【观察视角】
  Metrics / CLI / Replay
```

---

## A.3 字段级血缘说明（逐字段）

### 1️⃣ `value` / `channel`

**类型**：事实字段（World Fact）

**来源**

* 传感器
* 人工输入
* 外部系统

**路径**

```
External World
→ EXTERNAL_INPUT.payload.value / channel
→ policy.evaluate_event
→ decision.reason（引用）
→ action.reason（继承）
→ CLI / Replay
```

**工程意义**

> 世界发生了什么，是一切判断与责任的起点。

---

### 2️⃣ `suggested_action`

**类型**：判断字段（Opinion）

**来源**

* Policy Engine（规则 / 工程经验）

**路径**

```
EXTERNAL_INPUT
→ POLICY_DECISION.payload.suggested_action
→ runtime 读取
→ ACTION_EXECUTED.action_type
→ WorldState.last_action
→ Metrics / CLI
```

**关键建模原则**

> `suggested_action` ≠ 执行
> 它是“意见”，不是“命令”。

---

### 3️⃣ `reason`

**类型**：解释字段（Accountability）

**来源**

* Policy Engine（判断理由）
* Runtime（继承，不创造）

**路径**

```
EXTERNAL_INPUT（事实）
→ POLICY_DECISION.reason（为什么这么判断）
→ ACTION_EXECUTED.reason（为什么这么执行）
→ Metrics / CLI / Replay
```

**工程意义**

> `reason` 是系统“向人类说话”的能力。
> 没有 reason，就没有可解释系统。

---

### 4️⃣ `action_type`

**类型**：执行字段（Commitment）

**来源**

* Runtime（代表系统真实行为）

**路径**

```
POLICY_DECISION.suggested_action
→ runtime
→ ACTION_EXECUTED.action_type
→ reducer
→ WorldState
→ Metrics
```

**工程意义**

> 这是系统对世界做出的**真实承诺记录**。

---

### 5️⃣ `from_policy_t`

**类型**：因果锚点字段（Causal Anchor）

**来源**

* Runtime（建立判断与执行的因果关联）

**路径**

```
POLICY_DECISION.t
→ ACTION_EXECUTED.from_policy_t
→ Replay / Debug / Audit
```

**工程意义**

> 回答一个高阶问题：
> **“这个动作，是基于哪一次判断？”**

---

### 6️⃣ `trace_id`

**类型**：横向血缘字段（Correlation）

**来源**

* 外部输入或系统生成

**路径**

```
EXTERNAL_INPUT.trace_id
→ POLICY_DECISION.trace_id
→ ACTION_EXECUTED.trace_id
→ 全链路串联
```

**工程意义**

> 把一组事件认定为“同一件事”的身份证。

---

## A.4 字段血缘与系统分层的对应关系

| 分层             | 主要字段                        | 责任   |
| -------------- | --------------------------- | ---- |
| External World | value / channel             | 描述事实 |
| Policy         | suggested_action / reason   | 表达判断 |
| Runtime        | action_type / from_policy_t | 记录执行 |
| State          | last_action / action_count  | 记忆世界 |
| Metrics        | summary fields              | 汇报世界 |

---

## A.5 为什么字段血缘比“类图”更重要？

* 类图回答：**系统怎么实现**
* 字段血缘回答：**系统如何承担责任**

在工程系统中：

> **不能画清字段血缘的系统，一定不可解释；
> 不可解释的系统，迟早会失控。**

---

## A.6 本系统的字段设计一句话总结

> **事实不可篡改，
> 判断必须留痕，
> 执行必须可追，
> 汇总必须给人。**

---

### 使用建议（给读者）

* 初学者：先看 **A.2 全景图**
* 教学/讲解：重点讲 **suggested_action vs action_type**
* 工程复盘：重点看 **reason + from_policy_t + trace_id**

---

太好了，这一步其实是**整个项目的“灵魂总章”**。

> **《工程文明地图（Engineering Civilization Map）》**
> ——把 Architecture（结构）+ Field Lineage（责任）合成一张“世界观级”地图。

下面内容你可以**原样使用**。

---

# Appendix B · Engineering Civilization Map

**（工程文明地图）**

> 本页不是技术文档，而是**世界观文档**。
> 它回答一个问题：
> **为什么 CIM_WorldLab 的架构不是“程序结构”，而是“工程文明结构”。**

---

## B.1 工程文明的最小闭环

任何成熟的工程文明，至少要回答五个问题：

1. **发生了什么？**（事实）
2. **我们如何判断？**（判断）
3. **我们做了什么？**（执行）
4. **现在世界变成什么样？**（状态）
5. **我们如何向人解释与复盘？**（汇报）

CIM_WorldLab 把这五个问题，映射为五个稳定分层。

---

## B.2 工程文明五层图（Conceptual Map）

```
┌──────────────────────────────────────────┐
│            Presentation Civilization     │
│        CLI / HTTP / Teaching / Replay    │
│   “我如何把世界讲给人类听？”              │
└──────────────────▲───────────────────────┘
                   │
┌──────────────────┴───────────────────────┐
│           Observation Civilization       │
│          Metrics / Dashboards             │
│   “我如何总结这个世界的运行？”            │
└──────────────────▲───────────────────────┘
                   │
┌──────────────────┴───────────────────────┐
│            Memory Civilization           │
│        State / Event Log / Persistence   │
│   “我如何记住发生过的一切？”              │
└──────────────────▲───────────────────────┘
                   │
┌──────────────────┴───────────────────────┐
│          Decision & Action Civilization  │
│     Policy → Decision → Action Executed │
│   “我如何判断？如何行动？”                │
└──────────────────▲───────────────────────┘
                   │
┌──────────────────┴───────────────────────┐
│            Reality Interface             │
│        Gateway / External Input           │
│   “现实世界如何进入系统？”                │
└──────────────────────────────────────────┘
```

---

## B.3 架构层 ↔ 文明角色 对照表

| 架构层                       | 目录                            | 文明角色 | 核心问题     |
| ------------------------- | ----------------------------- | ---- | -------- |
| Reality Interface         | `world/gateway`               | 感知文明 | 世界发生了什么？ |
| Decision Civilization     | `world/policy`                | 判断文明 | 我们怎么看？   |
| Action Civilization       | `world/runtime`               | 行动文明 | 我们做了什么？  |
| Memory Civilization       | `world/state` / `persistence` | 记忆文明 | 世界现在怎样？  |
| Observation Civilization  | `world/metrics`               | 管理文明 | 我们如何总结？  |
| Presentation Civilization | `cli` / `http`                | 传播文明 | 我们如何讲述？  |

---

## B.4 字段血缘在文明中的位置

工程文明不是靠“模块”，而是靠**字段责任**运转。

```
【事实文明】
value / channel
↓
【判断文明】
suggested_action / reason
↓
【行动文明】
action_type / from_policy_t
↓
【记忆文明】
WorldState / Event Log
↓
【观察文明】
Metrics / Summary
↓
【传播文明】
CLI / Teaching / Replay
```

> **字段，是文明的最小载体。**

---

## B.5 为什么一定要拆 “Decision” 与 “Action”

这是工程文明与“脚本程序”的分水岭。

### 如果不拆（低级文明）

```
TEMP > 80 → 执行 COOL_DOWN
```

系统无法回答：

* 当时你**有没有意识到风险**？
* 你是判断错了，还是执行慢了？
* 有没有人/系统**不同意这个判断**？

---

### 拆开后（工程文明）

```
TEMP > 80
→ POLICY_DECISION（我认为应该 COOL_DOWN）
→ ACTION_EXECUTED（我确实执行了 COOL_DOWN）
```

系统可以回答：

* 判断是否合理
* 执行是否到位
* 责任是否清晰
* 是否可教学、可复盘

---

## B.6 CIM_WorldLab 的文明宣言（Mantra）

> **事实必须被尊重，
> 判断必须被记录，
> 行动必须可追责，
> 记忆必须可回放，
> 汇报必须面向人类。**

---

## B.7 为什么这是一套好的 Python 教材架构？

因为它不是在教：

* “怎么写 Python”
* “怎么组织文件”

而是在教：

* 如何用 Python 表达 **工程责任**
* 如何用 dataclass / reducer / event 表达 **文明级约束**
* 如何用测试守住 **文明边界**

> **语言只是工具，
> 文明才是结构。**

---

## B.8 给读者的阅读路径建议

* **初学者**：
  Architecture Map → Field Lineage → 本页文明地图
* **工程师**：
  本页 → runtime / reducer → replay / tests
* **教学使用**：
  本页 + Step18 Action Loop 测试

---

## B.9 一句话总结（刻在项目里的那一句）

> **CIM_WorldLab 不是一个程序，
> 而是一个把工程判断转化为可回放文明的世界。**

---

