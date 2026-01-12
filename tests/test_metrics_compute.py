"""
test_metrics_compute.py
=======================
验证 Step 11 的核心承诺：

- 世界发生 tick / ingest_inputs 后
- metrics() 能输出可读、正确的指标
"""

from cim_worldlab.world.events.external_input import ExternalInput
from cim_worldlab.world.gateway import FakePluginGateway
from cim_worldlab.world.runtime import WorldRuntime


def test_metrics_counts_inputs_by_channel_and_last_input_summary():
    fake = FakePluginGateway(queued=[
        ExternalInput(source="plugin", channel="equipment", name="TEMP", data={"v": 1}),
        ExternalInput(source="plugin", channel="equipment", name="PRESSURE", data={"v": 2}),
        ExternalInput(source="system", channel="order", name="NEW_ORDER", data={"id": "O1"}),
    ])

    rt = WorldRuntime(gateway=fake)

    # 先推进一次 tick，让世界时间变成 1
    rt.tick()

    # ingest 外部输入（附着在当前 t=1）
    rt.ingest_inputs()

    m = rt.metrics()

    assert m.t == 1
    assert m.tick_count == 1
    assert m.input_count == 3

    # 按 channel 分组统计
    assert m.inputs_by_channel["equipment"] == 2
    assert m.inputs_by_channel["order"] == 1

    # last_input_summary 应该对应最后一条输入（NEW_ORDER）
    assert m.last_input_summary is not None
    assert m.last_input_summary["channel"] == "order"
    assert m.last_input_summary["name"] == "NEW_ORDER"

    # Step18-3：默认还没有 action（这个测试场景里没有触发 policy）
    assert m.action_count == 0
    assert m.last_action_summary is None
