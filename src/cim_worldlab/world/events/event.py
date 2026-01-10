from dataclasses import dataclass, asdict
from typing import Any, Dict

@dataclass(frozen=True)
class Event:
    t: int
    type: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
