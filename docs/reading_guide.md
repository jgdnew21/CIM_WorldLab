# CIM_WorldLab Reading Guide  
**（工程级 Python 项目的 5 轮阅读法）**

> 本文不是教你“怎么写代码”，  
> 而是教你：**如何系统性地读懂一个工程项目**。

CIM_WorldLab 被设计为一个 **事件驱动、可回放、可解释的工程世界**。  
它的价值，不在于某一段实现，而在于**整体结构与责任边界**。

因此，阅读本项目，请**不要逐行阅读**，而是采用下面的 **5 轮阅读法**。

---

## 总原则（必读）

> **读工程代码，不是为了看懂所有细节，  
> 而是为了理解系统是如何承担责任的。**

每一轮阅读，你只回答一个问题：

- 这一层 **负责什么？**
- 这一层 **不负责什么？**

---

## 第 0 轮：建立世界观（5 分钟）

### 目标
知道：**这是一个什么系统？解决什么问题？**

### 阅读顺序
1. `README.md`
2. `docs/architecture/ARCHITECTURE.md`
3. `docs/glossary/terms.yaml`

### 本轮不做的事
- ❌ 不打开 `src/`
- ❌ 不看任何实现细节

### 本轮完成标准
你可以用 **3 句话**回答：
> CIM_WorldLab 是做什么的？  
> 它的核心抽象是什么？  
> 它和普通脚本程序有什么不同？

---

## 第 1 轮：跟一条事件链（20–30 分钟）

### 目标
理解系统 **“是怎么动起来的”**。

### 推荐入口
1. `tests/test_step18_action_loop.py`
2. `src/cim_worldlab/world/runtime/runtime.py`
3. `src/cim_worldlab/world/policy/`
4. `src/cim_worldlab/world/events/`

### 只回答这些问题
- 输入事件从哪里来？
- 系统会生成哪些事件？
- decision 和 action 是如何串起来的？

### 关键认知
> TEMP 高  
> → POLICY_DECISION（判断）  
> → ACTION_EXECUTED（执行留痕）

**不要纠结字段细节，只看流程。**

---

## 第 2 轮：理解世界如何“记忆”（30 分钟）

### 目标
搞清楚 **state / reducer / replay** 的关系。

### 阅读顺序
1. `src/cim_worldlab/world/state/state.py`
2. `src/cim_worldlab/world/state/reducer.py`
3. `tests/test_state_reducer.py`
4. `src/cim_worldlab/world/persistence/`

### 重点问题
- state 是否不可变（或逻辑不可变）？
- reducer 是否是纯函数？
- 为什么事件回放一定能复现状态？

### 本轮完成标准
你能解释清楚：
> 给同一串事件，  
> 为什么世界状态一定是一样的？

---

## 第 3 轮：系统如何“对人说话”（20 分钟）

### 目标
理解 **metrics 与 CLI 的角色边界**。

### 阅读顺序
1. `src/cim_worldlab/world/metrics/`
2. `tests/test_metrics_compute.py`
3. `src/cim_worldlab/cli/main.py`
4. `src/cim_worldlab/cli/utils.py`

### 核心问题
- metrics 为什么只读 state？
- CLI 为什么不包含业务逻辑？

### 关键认知
> 如果删除 CLI，  
> 系统依然可以完整运行。

CLI 只是 **展示层**，不是系统核心。

---

## 第 4 轮：外部世界与系统边界（可选）

### 目标
理解系统如何 **安全地接入现实世界**。

### 阅读顺序
1. `src/cim_worldlab/world/gateway/`
2. `src/cim_worldlab/plugins/http_ingest_app.py`
3. `schemas/*.json`
4. `tests/test_http_*`

### 核心问题
- 为什么输入必须先过 schema？
- gateway 为什么不做判断？

---

## 三个强烈推荐的阅读技巧

### 1️⃣ 以测试为导航
> **优先读 test，而不是实现。**

- test 描述的是“系统应该如何表现”
- 实现只是“如何做到”

---

### 2️⃣ 画责任边界线
读任何文件时，问一句：

> 如果我在这里加功能，会不会越界？

例如：
- 在 runtime 里算指标 → ❌
- 在 metrics 里发事件 → ❌
- 在 policy 里改 state → ❌

---

### 3️⃣ 允许暂时看不懂
工程阅读不是线性的。

- utils / helper 看不懂？先跳过
- 某个细节没想通？先记下

当你有了整体地图，再回头看，理解速度会显著提升。

---

## 阅读完成自检清单

- [ ] 我能说清楚每个目录的职责
- [ ] 我能解释 runtime / policy / reducer 的区别
- [ ] 我能完整讲一遍 Step18 的事件闭环
- [ ] 我知道为什么 decision ≠ action
- [ ] 我理解 metrics 为什么不能改 state

如果以上都能做到，  
你已经 **真正读懂了 CIM_WorldLab**。

---

## 一句阅读心法（送给读者）

> **读工程代码，不是寻找答案，  
> 而是在理解作者做了哪些选择，  
> 以及刻意放弃了哪些可能性。**

CIM_WorldLab 的价值，不在于“代码技巧”，  
而在于它展示了：  
**如何把现实世界的工程判断，压缩成一个可解释的系统。**