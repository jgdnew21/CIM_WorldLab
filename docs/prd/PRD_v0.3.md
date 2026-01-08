# CIM World PRD v0.3

## 1. 一句话定义
CIM World 是一个面向学生的半导体工厂虚拟世界：可仿真、可插件、可回放、可进化。  
学生以“厂长视角”通过连续场景项目亲手构建 MES/EAP/OMS/SPC/FDC/APC/RMS 等工厂软件能力，并通过 replay 对比看见系统前后差异。

## 2. 核心目标（North Star）
只要学生愿意花时间，能在同一个世界里系统性学完半导体工厂常见软件体系，并产出可回放、可度量、可解释的工程作品。

## 3. 设计原则
- 世界先于系统：先让工厂跑起来
- 事件驱动：变化源自事件流
- 动作留痕：证据→决策→执行→结果
- 不限制语言：限制协议，不限制创造
- 不误导：宁可简化也不歪曲因果

## 4. 范围（能力树概览）
- 基础：WIP/Flow、Dispatch、Basic EAP、Trace/History、Replay
- 稳定：FDC、SPC、Maintenance、RMS
- 运营：OMS、Scheduling、Yield/Quality
- 自优化：APC、AI Copilot、Policy Governance

## 5. 世界组成
- Factory Twin：设备/产线/物料/工艺/订单/质量 的仿真
- World Runtime：时间推进、事件总线、状态存储、回放引擎
- Plugin Layer：跨语言插件（HTTP JSON）
- UI & Tools：指挥台、回放、对比评测、事故复盘、术语库

## 6. 协议
- Event schema：schemas/event.schema.json
- Action schema：schemas/action.schema.json

## 7. Project Pack（场景包）
每个项目场景包含：story、case_input、baseline、evaluation、tests、glossary_refs。

## 8. 评分（分层）
- 功能分：是否达成场景目标
- 工程分：稳定性/可解释/可追溯
- 文明分：降级策略/避免过度动作/权衡意识

## 9. AI 探索（边界）
允许：解释助手、RCA 假设、策略草拟、术语翻译  
暂不允许：AI 直接执行高风险控制（停机/改 recipe），除非门槛+验证+可回滚

## 10. 路线图（MVP）
- MVP-0：世界能跑
- MVP-1：P01 场景闭环
- MVP-2：插件接入
- MVP-3：评分与 replay 对比
- MVP-4：沉浸 UI