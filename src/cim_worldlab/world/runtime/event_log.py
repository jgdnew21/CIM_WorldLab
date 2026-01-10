from dataclasses import dataclass, field
from typing import List, Optional

from cim_worldlab.world.events.event import Event

@dataclass
class EventLog:
    _events: List[Event] = field(default_factory=list)

    def append(self, e: Event) -> None:
        self._events.append(e)

    def all(self) -> List[Event]:
        return self._events

    def last(self) -> Optional[Event]:
        return self._events[-1] if self._events else None

    def __len__(self) -> int:
        return len(self._events)
