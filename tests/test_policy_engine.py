"""
test_policy_engine.py
=====================
Step 17 验收测试：

- 当收到温度输入 TEMP_READING 且 temp_c > threshold
  -> runtime 应该自动追加一条 POLICY_DECISION 事件

我们直接用 FakePluginGateway 来模拟输入（不需要 HTTP）。
"""

from cim_worldlab.world.events.external_input import ExternalInput
from cim_worldlab.world.events.policy_decision import POLICY_DECISION_TYPE
from cim_worldlab.world.gateway import FakePluginGateway
from cim_worldlab.world.runtime import WorldRuntime


def test_temp_high_triggers_policy_decision():
    fake = FakePluginGateway(queued=[
        ExternalInput(source="plugin", channel="equipment", name="TEMP_READING", data={"temp_c": 99.0}, trace_id="TR-1")
    ])

    rt = WorldRuntime(gateway=fake)

    rt.tick()
    rt.ingest_inputs()

    # event_log 里应该有：WORLD_TICK + EXTERNAL_INPUT + POLICY_DECISION（顺序上决策在输入之后）
    types = [e.type for e in rt.event_log.all()]
    assert "WORLD_TICK" in types
    assert "EXTERNAL_INPUT" in types
    assert POLICY_DECISION_TYPE in types

    # 取最后一条决策事件，检查 payload
    decision_events = [e for e in rt.event_log.all() if e.type == POLICY_DECISION_TYPE]
    assert len(decision_events) == 1
    de = decision_events[0]

    assert de.payload["rule_id"] == "TEMP_HIGH_PAUSE"
    assert de.payload["recommended_action"] == "PAUSE"
    assert de.payload["severity"] == "ALERT"
    assert de.payload.get("trace_id") == "TR-1"

    assert "POLICY_DECISION" in types
    assert "ACTION_EXECUTED" in types
    assert types.index("ACTION_EXECUTED") > types.index("POLICY_DECISION")

