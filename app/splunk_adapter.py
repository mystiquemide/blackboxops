from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from app.models import EvidenceRef


class SplunkAdapter:
    def __init__(self, sample_path: str | Path = "data/sample_splunk_events.jsonl", use_mock: bool | None = None):
        self.sample_path = Path(sample_path)
        self.use_mock = use_mock if use_mock is not None else os.getenv("USE_MOCK_SPLUNK", "true").lower() == "true"

    def search(self, query: str, time_range: str = "-15m to now", incident_id: str | None = None) -> list[EvidenceRef]:
        if self.use_mock:
            return self.mock_search(query, time_range, incident_id)
        return self.real_search_stub(query, time_range)

    def mock_search(self, query: str, time_range: str = "-15m to now", incident_id: str | None = None) -> list[EvidenceRef]:
        rows = self._load_sample_events()
        if incident_id:
            rows = [row for row in rows if row.get("incident_id") == incident_id]
        query_lower = query.lower()
        if "checkout" in query_lower:
            rows = [row for row in rows if row.get("service") == "checkout"]
        elif "cache" in query_lower:
            rows = [row for row in rows if row.get("service") == "cache"]
        if not rows:
            return []
        evidence: list[EvidenceRef] = []
        for row in rows[:3]:
            confidence = 0.95 if row.get("severity") in {"error", "warn"} else 0.75
            evidence.append(
                EvidenceRef(
                    query=query,
                    time_range=time_range,
                    source="mock_splunk",
                    sample_event=row,
                    confidence=confidence,
                    risk_flags=row.get("risk_flags", []),
                )
            )
        return evidence

    def real_search_stub(self, query: str, time_range: str = "-15m to now") -> list[EvidenceRef]:
        return [
            EvidenceRef(
                query=query,
                time_range=time_range,
                source="splunk_search_api",
                sample_event={"note": "Real Splunk search hook configured but not executed in mock demo."},
                confidence=0.5,
                risk_flags=["integration-stub"],
            )
        ]

    def send_hec_event(self, event: dict[str, Any]) -> bool:
        if self.use_mock:
            return True
        # Hook point for Splunk HEC POST using SPLUNK_HEC_TOKEN.
        return False

    def _load_sample_events(self) -> list[dict[str, Any]]:
        if not self.sample_path.exists():
            return []
        with self.sample_path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
