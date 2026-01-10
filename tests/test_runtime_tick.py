# ----------------------------
# 5) 测试：验证“世界时间推进 + 事件留痕”是稳定的
# ----------------------------
"""
test_runtime_tick.py
====================
这是“工程地基”的单元测试。

我们验证：
1) tick 会让世界时间 t 递增
2) tick 会产生 Event，且字段正确
3) tick 会把事件写入 EventLog（留痕）
"""

from cim_worldlab.world.runtime import WorldRuntime


def test_tick_increments_time_and_logs_event():
    # 创建一个全新的世界运行时
    rt = WorldRuntime()

    # 第一次 tick：不传 payload（默认空 dict）
    e1 = rt.tick()
    assert rt.t == 1
    assert e1.t == 1
    assert e1.type == "WORLD_TICK"
    assert e1.payload == {}
    assert len(rt.event_log) == 1

    # 第二次 tick：传入 payload
    e2 = rt.tick({"source": "unit_test"})
    assert rt.t == 2
    assert e2.t == 2
    assert e2.payload["source"] == "unit_test"
    assert len(rt.event_log) == 2

    # last() 应该返回最后一次事件
    assert rt.event_log.last() == e2