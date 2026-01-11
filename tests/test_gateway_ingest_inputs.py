"""
test_gateway_ingest_inputs.py
=============================
验证：外部输入 -> ingest_inputs -> 变成事件 -> 写入 event_log

我们用 FakePluginGateway 模拟外部插件输入：
- queued 里放两个 ExternalInput
- ingest 后：
  - 返回两个 Event
  - event_log 多两条
  - gateway 队列被清空
"""

from cim_worldlab.world.events.external_input import ExternalInput, EXTERNAL_INPUT_TYPE
from cim_worldlab.world.gateway import FakePluginGateway
from cim_worldlab.world.runtime import WorldRuntime


def test_ingest_inputs_records_events_and_clears_queue():
    fake = FakePluginGateway(queued=[
        ExternalInput(source="plugin", channel="equipment", name="TEMP_READING", data={"temp_c": 92.5}),
        ExternalInput(source="human", channel="ops", name="PAUSE", data={"reason": "check machine"}),
    ])

    rt = WorldRuntime(gateway=fake)
    assert len(rt.event_log) == 0

    events = rt.ingest_inputs()

    assert len(events) == 2
    assert len(rt.event_log) == 2

    assert events[0].type == EXTERNAL_INPUT_TYPE
    assert events[0].payload["channel"] == "equipment"
    assert events[0].payload["name"] == "TEMP_READING"
    assert events[0].payload["data"]["temp_c"] == 92.5

    assert events[1].payload["source"] == "human"
    assert events[1].payload["name"] == "PAUSE"

    # 队列被消费清空（非常重要：避免重复消费）
    assert fake.queued == []
