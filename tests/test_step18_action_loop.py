"""
test_step18_action_loop.py
==========================
锁死 Step18 的最小闭环：

TEMP 高 -> POLICY_DECISION -> ACTION_EXECUTED
并且：
- reducer/state 能正确累计 action_count / last_action
- metrics 能展示 action_count / last_action_summary
"""

from cim_worldlab.world.events.external_input import ExternalInput
from cim_worldlab.world.gateway import FakePluginGateway
from cim_worldlab.world.runtime import WorldRuntime


def test_step18_temp_high_produces_action_executed_and_metrics():
    # 1) 准备一个会触发策略的输入（你 Step17 已有这条规则）
    fake = FakePluginGateway(queued=[
        ExternalInput(
            source="plugin",
            channel="equipment",
            name="TEMP_READING",
            data={"temp_c": 99.0},
            trace_id="S18-TR-1",
        )
    ])

    rt = WorldRuntime(gateway=fake)

    # 2) tick 推进时间（t=1），并让 runtime 在 _record() 中 ingest_inputs + policy hook 生效
    rt.tick()
    rt.ingest_inputs()

    # 3) 断言事件链：必须出现 POLICY_DECISION 和 ACTION_EXECUTED 且顺序正确
    events = rt.event_log.all() if hasattr(rt.event_log, "all") else rt.event_log
    types = [e.type for e in events]

    assert "POLICY_DECISION" in types
    assert "ACTION_EXECUTED" in types
    assert types.index("ACTION_EXECUTED") > types.index("POLICY_DECISION")

    # 4) 断言 state（reducer 推导的权威状态）
    assert rt.state.action_count >= 1
    assert rt.state.last_action is not None
    assert rt.state.last_action.get("action_type")  # 非空即可

    # 5) 断言 metrics（看板/投屏输出）
    m = rt.metrics()
    assert m.action_count == rt.state.action_count
    assert m.last_action_summary is not None
    assert m.last_action_summary.get("action_type")
