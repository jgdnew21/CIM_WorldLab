# tests/test_action_executed_reducer.py
from cim_worldlab.world.events.action_executed import ActionExecuted, ACTION_EXECUTED_TYPE
from cim_worldlab.world.state import WorldState, apply_event


def test_reducer_action_executed_updates_state():
    s0 = WorldState.initial()

    e = ActionExecuted(
        action_type="SLOW_DOWN",
        reason="TEMP exceeded threshold",
        from_policy_t=123,
        trace_id="trace_1",
    ).to_event(t=10)

    s1 = apply_event(s0, e)

    assert s1.action_count == 1
    assert s1.last_action is not None
    assert s1.last_action["t"] == 10
    assert s1.last_action["action_type"] == "SLOW_DOWN"
    assert "TEMP" in s1.last_action["reason"]
    assert s1.last_action["from_policy_t"] == 123
    assert s1.last_action["trace_id"] == "trace_1"
