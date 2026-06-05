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
                    evidence_id=f"EVD-{100 + len(evidence)}",
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
        import time as _time
        import warnings

        import requests
        from requests.packages.urllib3.exceptions import InsecureRequestWarning  # type: ignore[attr-defined]

        warnings.filterwarnings("ignore", category=InsecureRequestWarning)

        host = os.getenv("SPLUNK_HOST", "localhost")
        port = int(os.getenv("SPLUNK_PORT", "8089"))
        token = os.getenv("SPLUNK_TOKEN", "")
        base = f"https://{host}:{port}"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            create = requests.post(
                f"{base}/services/search/jobs",
                headers=headers,
                data={
                    "search": f"search {query}",
                    "output_mode": "json",
                    "earliest_time": "-15m",
                    "latest_time": "now",
                    "count": 10,
                },
                verify=False,
                timeout=30,
            )
            create.raise_for_status()
            sid = create.json()["sid"]

            for _ in range(30):
                poll = requests.get(
                    f"{base}/services/search/jobs/{sid}",
                    headers=headers,
                    params={"output_mode": "json"},
                    verify=False,
                    timeout=10,
                )
                if poll.json()["entry"][0]["content"]["isDone"]:
                    break
                _time.sleep(1)

            results_resp = requests.get(
                f"{base}/services/search/jobs/{sid}/results",
                headers=headers,
                params={"output_mode": "json", "count": 10},
                verify=False,
                timeout=10,
            )
            rows = results_resp.json().get("results", [])

            if rows:
                return [
                    EvidenceRef(
                        query=query,
                        time_range=time_range,
                        source="splunk_search_api",
                        sample_event={k: str(v) for k, v in row.items() if not k.startswith("_")},
                        confidence=0.9,
                        risk_flags=["splunk-live"],
                    )
                    for row in rows[:3]
                ]
        except Exception as exc:
            return [
                EvidenceRef(
                    query=query,
                    time_range=time_range,
                    source="splunk_search_api",
                    sample_event={"error": str(exc), "note": "Splunk REST API call failed."},
                    confidence=0.2,
                    risk_flags=["splunk-error"],
                )
            ]

        return [
            EvidenceRef(
                query=query,
                time_range=time_range,
                source="splunk_search_api",
                sample_event={"note": "Splunk search returned 0 results."},
                confidence=0.5,
                risk_flags=[],
            )
        ]

    def send_hec_event(self, event: dict[str, Any]) -> bool:
        if self.use_mock:
            return True
        import warnings

        import requests
        from requests.packages.urllib3.exceptions import InsecureRequestWarning  # type: ignore[attr-defined]

        warnings.filterwarnings("ignore", category=InsecureRequestWarning)

        host = os.getenv("SPLUNK_HOST", "localhost")
        hec_port = int(os.getenv("SPLUNK_HEC_PORT", "8088"))
        token = os.getenv("SPLUNK_HEC_TOKEN", "")
        if not token:
            return False
        try:
            resp = requests.post(
                f"https://{host}:{hec_port}/services/collector",
                headers={"Authorization": f"Splunk {token}"},
                json={"event": event, "sourcetype": "blackboxops:agent_event"},
                verify=False,
                timeout=5,
            )
            return resp.status_code == 200
        except Exception:
            return False

    def _load_sample_events(self) -> list[dict[str, Any]]:
        if not self.sample_path.exists():
            return []
        with self.sample_path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
