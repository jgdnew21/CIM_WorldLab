from dataclasses import dataclass, field
from typing import Dict, Any

from cim_worldlab.world.events.event import Event
from cim_worldlab.world.runtime.event_log import EventLog

@dataclass
class WorldRuntime:
    t: int = 0
    event_log: EventLog = field(default_factory=EventLog)

    def tick(self, payload: Dict[str, Any] | None = None) -> Event:
        self.t += 1
        e = Event(
            t=self.t,
            type="WORLD_TICK",
            payload=payload or {},
        )
        self.event_log.append(e)
        return e
