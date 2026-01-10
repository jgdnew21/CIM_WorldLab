# ----------------------------
# 4) 包的 __init__.py（让 import 更顺手）
# ----------------------------
"""
cim_worldlab.world
==================
world 包用于放“世界机制”：
- events：事件模型（发生了什么）
- runtime：运行时（世界怎么推进）
- persistence：持久化（如何落盘）
- metrics：指标与观测（如何看见世界）

目前我们只实现了 events + runtime 的最小闭环。
"""