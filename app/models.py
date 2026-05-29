from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

EventType = Literal[
    "prompt",
    "response",
    "spl_query",
    "evidence",
    "policy_check",
    "action_proposal",
    "approval",
    "remediation_result",
]
PolicyStatus = Literal["allow", "block", "approval_required", "warn"]
RiskLevel = Literal["low", "medium", "high", "critical"]
EvidenceSource = Literal["mock_splunk", "splunk_mcp", "splunk_search_api"]


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EvidenceRef(BaseModel):
    evidence_id: str = Field(default_factory=lambda: _id("ev"))
    query: str
    time_range: str
    source: EvidenceSource = "mock_splunk"
    sample_event: dict[str, Any]
    confidence: float = Field(ge=0.0, le=1.0)
    risk_flags: list[str] = Field(default_factory=list)


class PolicyDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: _id("pol"))
    policy_id: str
    status: PolicyStatus
    reason: str
    risk_level: RiskLevel = "low"
    matched_rules: list[str] = Field(default_factory=list)
    required_approval: bool = False

    @field_validator("required_approval", mode="before")
    @classmethod
    def approval_matches_status(cls, value: bool, info):
        if info.data.get("status") == "approval_required":
            return True
        return bool(value)


class AgentEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: _id("evt"))
    incident_id: str
    session_id: str
    timestamp: datetime = Field(default_factory=utc_now)
    event_type: EventType
    actor: str
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    summary: str
    payload: dict[str, Any] = Field(default_factory=dict)
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)
    policy_decision: PolicyDecision | None = None


class IncidentSummary(BaseModel):
    incident_id: str
    title: str
    severity: str = "medium"
    status: str = "open"
    description: str = ""


class IncidentReplay(BaseModel):
    incident_id: str
    title: str
    status: str = "recorded"
    events: list[AgentEvent] = Field(default_factory=list)
    evidence: list[EvidenceRef] = Field(default_factory=list)
    policy_decisions: list[PolicyDecision] = Field(default_factory=list)


class Postmortem(BaseModel):
    incident_id: str
    title: str
    markdown: str
