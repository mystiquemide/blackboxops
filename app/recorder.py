from __future__ import annotations

import json
from pathlib import Path

from app.models import AgentEvent


class EventRecorder:
    def __init__(self, path: str | Path = "data/blackbox_events.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: AgentEvent) -> AgentEvent:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(event.model_dump_json() + "\n")
        return event

    def append_many(self, events: list[AgentEvent]) -> list[AgentEvent]:
        for event in events:
            self.append(event)
        return events

    def list_events(self, incident_id: str | None = None) -> list[AgentEvent]:
        if not self.path.exists():
            return []
        events: list[AgentEvent] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                event = AgentEvent.model_validate(json.loads(line))
                if incident_id is None or event.incident_id == incident_id:
                    events.append(event)
        return events

    def clear(self) -> None:
        self.path.write_text("", encoding="utf-8")
