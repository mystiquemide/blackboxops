from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.demo_agent import INCIDENT_ID, run_demo_incident
from app.models import IncidentReplay, IncidentSummary, PolicyDecision, Postmortem
from app.policy_engine import PolicyEngine
from app.postmortem import generate_postmortem
from app.recorder import EventRecorder

app = FastAPI(title="BlackBoxOps", version="0.1.0")
_LAST_REPLAY: IncidentReplay | None = None


class QueryRequest(BaseModel):
    query: str
    time_range: str = "-15m to now"


class ActionRequest(BaseModel):
    action_type: str
    target: str
    evidence_refs: list[str] = []


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "blackboxops"}


@app.post("/demo/run", response_model=IncidentReplay)
def demo_run() -> IncidentReplay:
    global _LAST_REPLAY
    _LAST_REPLAY = run_demo_incident()
    return _LAST_REPLAY


@app.get("/incidents", response_model=list[IncidentSummary])
def incidents() -> list[IncidentSummary]:
    path = Path("data/sample_incidents.jsonl")
    if not path.exists():
        return []
    summaries = [
        IncidentSummary.model_validate(json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return [summary for summary in summaries if summary.incident_id == INCIDENT_ID]


def _require_supported_incident(incident_id: str) -> None:
    if incident_id != INCIDENT_ID:
        raise HTTPException(status_code=404, detail=f"No replay is available for incident_id={incident_id}")


@app.get("/incidents/{incident_id}/replay", response_model=IncidentReplay)
def incident_replay(incident_id: str) -> IncidentReplay:
    _require_supported_incident(incident_id)
    global _LAST_REPLAY
    if _LAST_REPLAY is None or _LAST_REPLAY.incident_id != incident_id:
        _LAST_REPLAY = run_demo_incident()
    return _LAST_REPLAY


@app.get("/incidents/{incident_id}/postmortem", response_model=Postmortem)
def incident_postmortem(incident_id: str) -> Postmortem:
    _require_supported_incident(incident_id)
    replay = incident_replay(incident_id)
    return generate_postmortem(replay)


@app.post("/policy/evaluate-query", response_model=PolicyDecision)
def evaluate_query(request: QueryRequest) -> PolicyDecision:
    return PolicyEngine.from_file("policies/default.yaml").evaluate_query(request.query, request.time_range)


@app.post("/policy/evaluate-action", response_model=PolicyDecision)
def evaluate_action(request: ActionRequest) -> PolicyDecision:
    return PolicyEngine.from_file("policies/default.yaml").evaluate_action(request.action_type, request.target, request.evidence_refs)
