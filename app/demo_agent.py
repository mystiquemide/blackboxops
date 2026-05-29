from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.models import AgentEvent, IncidentReplay, PolicyDecision
from app.policy_engine import PolicyEngine
from app.recorder import EventRecorder
from app.splunk_adapter import SplunkAdapter

INCIDENT_ID = "inc_prompt_injection_checkout"
INCIDENT_TITLE = "Checkout latency spike with prompt-injection log payload"


def run_demo_incident(event_store_path: str | Path = "data/blackbox_events.jsonl", use_mock: bool = True) -> IncidentReplay:
    session_id = f"sess_{uuid4().hex[:8]}"
    recorder = EventRecorder(event_store_path)
    recorder.clear()
    policy = PolicyEngine.from_file("policies/default.yaml")
    splunk = SplunkAdapter(use_mock=use_mock)
    events: list[AgentEvent] = []
    decisions: list[PolicyDecision] = []

    def add(event: AgentEvent) -> None:
        recorder.append(event)
        events.append(event)

    add(AgentEvent(
        incident_id=INCIDENT_ID,
        session_id=session_id,
        event_type="prompt",
        actor="sre_user",
        summary="User asks AI ops agent to investigate checkout latency spike.",
        payload={"prompt": "Investigate checkout latency and propose a safe remediation."},
    ))

    safe_query = 'index=main sourcetype=app_logs service=checkout (error OR warn) | stats count by severity, host'
    query_decision = policy.evaluate_query(safe_query, "-15m to now")
    decisions.append(query_decision)
    add(AgentEvent(
        incident_id=INCIDENT_ID,
        session_id=session_id,
        event_type="policy_check",
        actor="blackboxops_policy",
        risk_score=0.1,
        summary="Policy allowed scoped checkout Splunk query.",
        payload={"query": safe_query},
        policy_decision=query_decision,
    ))

    evidence = splunk.search(safe_query, "-15m to now", INCIDENT_ID)
    add(AgentEvent(
        incident_id=INCIDENT_ID,
        session_id=session_id,
        event_type="spl_query",
        actor="demo_agent",
        risk_score=0.2,
        summary="Agent queried mock Splunk for checkout errors and warnings.",
        payload={"query": safe_query, "result_count": len(evidence)},
        evidence_refs=evidence,
    ))

    for item in evidence:
        add(AgentEvent(
            incident_id=INCIDENT_ID,
            session_id=session_id,
            event_type="evidence",
            actor="mock_splunk",
            risk_score=0.6 if "prompt-injection" in item.risk_flags else 0.35,
            summary="Splunk evidence captured for incident replay.",
            payload={"sample_event": item.sample_event},
            evidence_refs=[item],
        ))
        content_decision = policy.evaluate_content(item.sample_event.get("message", ""))
        if content_decision.status != "allow":
            decisions.append(content_decision)
            add(AgentEvent(
                incident_id=INCIDENT_ID,
                session_id=session_id,
                event_type="policy_check",
                actor="blackboxops_policy",
                risk_score=1.0,
                summary="Prompt injection detected in retrieved log content and blocked from steering the agent.",
                payload={"message": item.sample_event.get("message")},
                evidence_refs=[item],
                policy_decision=content_decision,
            ))

    unsafe_query = "index=* | delete"
    blocked_query = policy.evaluate_query(unsafe_query, "-24h@h to now")
    decisions.append(blocked_query)
    add(AgentEvent(
        incident_id=INCIDENT_ID,
        session_id=session_id,
        event_type="policy_check",
        actor="blackboxops_gateway",
        risk_score=1.0,
        summary="Unsafe broad/destructive SPL was blocked before reaching Splunk.",
        payload={"query": unsafe_query},
        policy_decision=blocked_query,
    ))

    evidence_ids = [item.evidence_id for item in evidence]
    action_decision = policy.evaluate_action("restart_service", "checkout-api", evidence_ids)
    decisions.append(action_decision)
    add(AgentEvent(
        incident_id=INCIDENT_ID,
        session_id=session_id,
        event_type="action_proposal",
        actor="demo_agent",
        risk_score=0.8,
        summary="Agent proposed restarting checkout-api; BlackBoxOps requires human approval before disruption.",
        payload={"action_type": "restart_service", "target": "checkout-api"},
        evidence_refs=evidence,
        policy_decision=action_decision,
    ))

    add(AgentEvent(
        incident_id=INCIDENT_ID,
        session_id=session_id,
        event_type="response",
        actor="demo_agent",
        risk_score=0.2,
        summary="Agent returns evidence-backed diagnosis without executing unsafe remediation.",
        payload={"diagnosis": "Checkout errors spiked after deploy; malicious log payload was isolated; restart requires approval."},
        evidence_refs=evidence,
    ))

    return IncidentReplay(
        incident_id=INCIDENT_ID,
        title=INCIDENT_TITLE,
        status="recorded",
        events=events,
        evidence=evidence,
        policy_decisions=decisions,
    )
