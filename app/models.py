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
    display_id: str | None = None
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
    updated_at: str = "2026-05-29T10:05:00Z"
    actor: str = "bb-agent/checkout-v2"
    source: EvidenceSource = "mock_splunk"
    evidence_refs: int = 0
    policy_id: str = "POL-INJ-01"
    policy_outcome: str = "BLOCKED"

class PolicySummary(BaseModel):
    policy_id: str
    name: str
    description: str
    status: PolicyStatus
    enabled: bool = True
    risk_level: RiskLevel = "low"
    splunk_source: EvidenceSource = "mock_splunk"
    original_rule_id: str | None = None

class IncidentReplay(BaseModel):
    incident_id: str
    title: str
    status: str = "recorded"
    session_id: str | None = None
    source: EvidenceSource = "mock_splunk"
    started_at: str | None = None
    outcome: str = "recorded"
    approval_required: bool = False
    events: list[AgentEvent] = Field(default_factory=list)
    evidence: list[EvidenceRef] = Field(default_factory=list)
    policy_decisions: list[PolicyDecision] = Field(default_factory=list)
    llm_analysis: str | None = None


class ActionProposalRequest(BaseModel):
    incident_id: str
    action_type: str
    target: str
    evidence_refs: list[str] = Field(default_factory=list)
    requested_by: str = "operator@blackboxops.local"
    reason: str = ""


class ActionProposal(BaseModel):
    action_id: str = Field(default_factory=lambda: _id("act"))
    incident_id: str
    action_type: str
    target: str
    evidence_refs: list[str] = Field(default_factory=list)
    requested_by: str
    reason: str = ""
    status: Literal["pending_approval", "blocked", "allowed", "warned", "approved", "rejected"]
    decision: PolicyDecision
    created_at: str = Field(default_factory=lambda: utc_now().isoformat().replace("+00:00", "Z"))
    approved_by: str | None = None
    rejected_by: str | None = None
    review_note: str | None = None
    reviewed_at: str | None = None


class ActionReviewRequest(BaseModel):
    reviewer: str
    note: str = ""


class ActionReviewResponse(BaseModel):
    action_id: str
    incident_id: str
    status: Literal["approved", "rejected"]
    reviewer: str
    note: str = ""
    reviewed_at: str
    signature: str | None = None


class Postmortem(BaseModel):
    incident_id: str
    title: str
    markdown: str
