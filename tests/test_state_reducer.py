"""
test_state_reducer.py
=====================
这一测试专门验证 Step 10 的核心承诺：

- 状态 state 不靠手写维护
- 状态由事件推导（apply_event/apply_events）而来
"""

from cim_worldlab.world.events.event import Event
from cim_worldlab.world.events.external_input import EXTERNAL_INPUT_TYPE
from cim_worldlab.world.state import WorldState, apply_events


def test_apply_events_builds_state_from_history():
    history = [
        Event(t=1, type="WORLD_TICK", payload={}),
        Event(t=1, type=EXTERNAL_INPUT_TYPE, payload={"source": "plugin", "channel": "equipment", "name": "TEMP", "data": {"temp": 90}}),
        Event(t=2, type="WORLD_TICK", payload={}),
        Event(t=2, type=EXTERNAL_INPUT_TYPE, payload={"source": "human", "channel": "ops", "name": "PAUSE", "data": {"reason": "check"}}),
    ]

    s0 = WorldState.initial()
    s = apply_events(s0, history)

    # 最终时间来自最后一个 WORLD_TICK 的 t（这里是 2）
    assert s.t == 2
    assert s.tick_count == 2

    # 输入事件有两条
    assert s.input_count == 2

    # last_input 是最后一条 EXTERNAL_INPUT 的 payload
    assert s.last_input is not None
    assert s.last_input["name"] == "PAUSE"
