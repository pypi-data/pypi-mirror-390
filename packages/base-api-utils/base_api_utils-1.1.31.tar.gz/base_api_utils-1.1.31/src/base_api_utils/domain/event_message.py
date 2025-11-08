import json
from dataclasses import dataclass
from typing import Dict, Optional, Any


@dataclass
class EventMessage:
    event_type: str
    payload: Dict[str, Any]
    routing_key: str
    properties: Optional[Dict[str, Any]] = None

    @classmethod
    def from_rabbit(cls, ch, method, properties, body):
        try:
            payload = json.loads(body) if isinstance(body, (str, bytes)) else body
        except json.JSONDecodeError:
            payload = {"raw_body": str(body)}

        return cls(
            event_type=method.routing_key,
            payload=payload,
            routing_key=method.routing_key,
            properties=vars(properties) if properties else None
        )
