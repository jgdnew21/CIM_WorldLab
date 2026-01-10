from cim_worldlab.world.runtime import WorldRuntime

def test_tick_increments_time_and_logs_event():
    rt = WorldRuntime()

    e1 = rt.tick()
    assert rt.t == 1
    assert e1.t == 1
    assert e1.type == "WORLD_TICK"
    assert len(rt.event_log) == 1

    e2 = rt.tick({"source": "unit_test"})
    assert rt.t == 2
    assert e2.payload["source"] == "unit_test"
    assert len(rt.event_log) == 2
    assert rt.event_log.last() == e2
