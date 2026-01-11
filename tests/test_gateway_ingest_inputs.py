"""
test_gateway_ingest_inputs.py
=============================
本文件测试的是：WorldRuntime.ingest_inputs() 的基础行为。

重要说明（Step 17 之后）：
- ingest_inputs() 会把外部输入写成 EXTERNAL_INPUT 事件（这是“事实事件”）
- 同时，runtime 在记录事件后，会触发 Policy Engine：
  某些输入可能会额外产生 POLICY_DECISION（这是“判断事件”）

因此：
- ingest_inputs() 的返回值仍然只包含“外部输入事件”
- 但 event_log 总量可能 > 外部输入事件数（因为多了决策事件）
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

    # 1) ingest_inputs() 的返回值：只包含外部输入事件（数量仍然是 2）
    assert len(events) == 2
    assert all(e.type == EXTERNAL_INPUT_TYPE for e in events)

    # 2) event_log 里至少包含这两条外部输入事件
    #    （但可能还会有 POLICY_DECISION 等额外事件）
    all_events = rt.event_log.all()
    external_events = [e for e in all_events if e.type == EXTERNAL_INPUT_TYPE]
    assert len(external_events) == 2

    # 3) 队列应被清空（FakePluginGateway 的 queued 会被 pop 掉）
    assert fake.queued == []
