from __future__ import annotations

import hashlib
import hmac as _hmac
import json
import os
from pathlib import Path
from textwrap import dedent

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, Response
from pydantic import BaseModel

from app.auth import AuthSession, AuthUser, SigninRequest, SignupRequest, current_user_from_authorization, signin_user, signup_user, update_user_profile
from app.auth_google import build_google_authorization_url, callback_url_for_session, exchange_google_code_for_session, issue_mock_google_session, use_mock_auth
from app.demo_agent import (
    CACHE_INCIDENT_ID,
    INCIDENT_ID,
    run_cache_incident,
    run_demo_incident,
)
from app.models import ActionProposal, ActionProposalRequest, ActionReviewRequest, ActionReviewResponse, AgentEvent, IncidentReplay, IncidentSummary, PolicyDecision, PolicySummary, Postmortem, utc_now
from app.policy_engine import PolicyEngine
from app.postmortem import generate_postmortem
from app.recorder import EventRecorder

app = FastAPI(title="BlackBoxOps", version="0.2.0")
_LAST_REPLAY: IncidentReplay | None = None
_LAST_CACHE_REPLAY: IncidentReplay | None = None
_ACTION_PROPOSALS: list[ActionProposal] = []
_POLICY_ENABLED: dict[str, bool] = {}

_SUPPORTED_INCIDENTS = {INCIDENT_ID, CACHE_INCIDENT_ID}
_ANALYSIS_CACHE: dict[str, tuple[str, str]] = {}


class QueryRequest(BaseModel):
    query: str
    time_range: str = "-15m to now"


class ActionRequest(BaseModel):
    action_type: str
    target: str
    evidence_refs: list[str] = []


class ProfileUpdateRequest(BaseModel):
    name: str | None = None
    current_password: str | None = None
    new_password: str | None = None


def _truthy(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _splunk_configured() -> bool:
    return bool(os.getenv("SPLUNK_HEC_TOKEN") or os.getenv("SPLUNK_MCP_URL") or (os.getenv("SPLUNK_HOST") and os.getenv("SPLUNK_TOKEN")))


def _llm_configured() -> bool:
    return bool(
        os.getenv("GROQ_API_KEY")
        or (os.getenv("USE_SPLUNK_AI") == "true" and os.getenv("SPLUNK_TOKEN"))
    )


def _sign_approval(action_id: str, status: str, reviewer: str, reviewed_at: str) -> str:
    secret = os.getenv("APPROVAL_SECRET", "blackboxops-dev-secret-change-in-prod")
    msg = f"{action_id}:{status}:{reviewer}:{reviewed_at}"
    return _hmac.new(secret.encode(), msg.encode(), hashlib.sha256).hexdigest()


@app.get("/api/health")
@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "service": "blackboxops",
        "mock_splunk": _truthy(os.getenv("USE_MOCK_SPLUNK"), True),
        "splunk_configured": _splunk_configured(),
        "llm_configured": _llm_configured(),
        "policy_mode": "fail_closed",
    }


@app.post("/api/auth/signup", response_model=AuthSession)
def auth_signup(request: SignupRequest) -> AuthSession:
    return signup_user(request)


@app.post("/api/auth/signin", response_model=AuthSession)
def auth_signin(request: SigninRequest) -> AuthSession:
    return signin_user(request)


@app.get("/api/auth/me", response_model=AuthUser)
def auth_me(user: AuthUser = Depends(current_user_from_authorization)) -> AuthUser:
    return user


@app.patch("/api/auth/profile", response_model=AuthUser)
def auth_patch_profile(body: ProfileUpdateRequest, user: AuthUser = Depends(current_user_from_authorization)) -> AuthUser:
    return update_user_profile(
        user,
        name=body.name,
        current_password=body.current_password,
        new_password=body.new_password,
    )


@app.post("/api/auth/demo", response_model=AuthSession)
def auth_demo() -> AuthSession:
    from app.auth import _DEMO_TOKEN, _DEMO_USER_RECORD, AuthSession, _public_user
    return AuthSession(token=_DEMO_TOKEN, user=_public_user(_DEMO_USER_RECORD))


@app.get("/api/auth/google/login")
def auth_google_login() -> RedirectResponse:
    if use_mock_auth():
        return RedirectResponse(callback_url_for_session(issue_mock_google_session()))
    return RedirectResponse(build_google_authorization_url())


@app.get("/api/auth/google/callback")
def auth_google_callback(code: str | None = None, state: str | None = None) -> RedirectResponse:
    session = exchange_google_code_for_session(code, state)
    return RedirectResponse(callback_url_for_session(session))


@app.post("/api/demo/run", response_model=IncidentReplay)
@app.post("/demo/run", response_model=IncidentReplay)
def demo_run() -> IncidentReplay:
    global _LAST_REPLAY
    _ACTION_PROPOSALS.clear()
    _LAST_REPLAY = run_demo_incident()
    return _LAST_REPLAY


@app.post("/api/demo/run-cache", response_model=IncidentReplay)
def demo_run_cache() -> IncidentReplay:
    global _LAST_CACHE_REPLAY
    _LAST_CACHE_REPLAY = run_cache_incident()
    return _LAST_CACHE_REPLAY


def _demo_policy_id(rule_id: str) -> str:
    mapping = {
        "prompt-injection-content": "POL-INJ-01",
        "broad-index-search": "POL-SPL-01",
        "risky-spl-command": "POL-SPL-02",
        "destructive-action-approval": "POL-APPR-01",
        "low-risk-diagnostic-action": "POL-DIAG-01",
        "policy-load-fail-closed": "POL-FAIL-CLOSED",
    }
    return mapping.get(rule_id, rule_id.upper())


def _incident_summary_from_record(record: dict) -> IncidentSummary:
    is_injection = "prompt" in record["title"].lower() or "injection" in record["title"].lower()
    return IncidentSummary(
        incident_id=record["incident_id"],
        title=record["title"],
        severity="critical" if is_injection else record.get("severity", "medium"),
        status="blocked" if is_injection else record.get("status", "demo-ready"),
        description=record.get("description", ""),
        updated_at="2026-06-11T10:05:00Z",
        actor="bb-agent/checkout-v2" if is_injection else "bb-agent/cache-monitor",
        source="mock_splunk",
        evidence_refs=3 if is_injection else 1,
        policy_id="POL-INJ-01" if is_injection else "POL-DIAG-01",
        policy_outcome="BLOCKED" if is_injection else "ALLOWED",
    )


def _load_sample_incident_records() -> list[dict]:
    path = Path("data/sample_incidents.jsonl")
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


@app.get("/api/incidents", response_model=list[IncidentSummary])
def api_incidents() -> list[IncidentSummary]:
    return _incident_summaries()


def _incident_summaries() -> list[IncidentSummary]:
    records = _load_sample_incident_records()
    return [_incident_summary_from_record(r) for r in records if r.get("incident_id") in _SUPPORTED_INCIDENTS]


def _require_supported_incident(incident_id: str) -> None:
    if incident_id not in _SUPPORTED_INCIDENTS:
        raise HTTPException(status_code=404, detail=f"No replay available for incident_id={incident_id}")


def _with_analysis(replay: IncidentReplay) -> IncidentReplay:
    """Lazily inject LLM analysis if missing. Uses cache to avoid duplicate calls."""
    if replay.llm_analysis:
        return replay
    cached = _ANALYSIS_CACHE.get(replay.incident_id)
    if cached:
        return replay.model_copy(update={"llm_analysis": cached[0], "llm_source": cached[1]})
    from app.llm import LLMAnalyzer
    try:
        analyzer = LLMAnalyzer()
        text = analyzer.analyze_evidence(replay.evidence, replay.title)
        if text:
            _ANALYSIS_CACHE[replay.incident_id] = (text, analyzer.last_source)
            return replay.model_copy(update={"llm_analysis": text, "llm_source": analyzer.last_source})
    except Exception:
        pass
    return replay


def _get_or_run_replay(incident_id: str) -> IncidentReplay:
    global _LAST_REPLAY, _LAST_CACHE_REPLAY
    if incident_id == CACHE_INCIDENT_ID:
        if _LAST_CACHE_REPLAY is None or _LAST_CACHE_REPLAY.incident_id != incident_id:
            _LAST_CACHE_REPLAY = run_cache_incident()
        _LAST_CACHE_REPLAY = _with_analysis(_LAST_CACHE_REPLAY)
        return _LAST_CACHE_REPLAY
    if _LAST_REPLAY is None or _LAST_REPLAY.incident_id != incident_id:
        _LAST_REPLAY = run_demo_incident()
    _LAST_REPLAY = _with_analysis(_LAST_REPLAY)
    return _LAST_REPLAY


@app.get("/api/incidents/{incident_id}/replay", response_model=IncidentReplay)
@app.get("/incidents/{incident_id}/replay", response_model=IncidentReplay)
def incident_replay(incident_id: str) -> IncidentReplay:
    _require_supported_incident(incident_id)
    return _get_or_run_replay(incident_id)


@app.get("/api/incidents/{incident_id}/postmortem", response_model=Postmortem)
@app.get("/incidents/{incident_id}/postmortem", response_model=Postmortem)
def incident_postmortem(incident_id: str) -> Postmortem:
    _require_supported_incident(incident_id)
    return generate_postmortem(_get_or_run_replay(incident_id))


@app.get("/api/incidents/{incident_id}/postmortem/html")
def incident_postmortem_html(incident_id: str, signature: str | None = None) -> Response:
    """Returns a print-ready HTML postmortem. Open in browser and print to PDF."""
    _require_supported_incident(incident_id)
    from app.postmortem import generate_postmortem_html
    replay = _get_or_run_replay(incident_id)
    html = generate_postmortem_html(replay, signature=signature)
    return Response(content=html, media_type="text/html")


@app.get("/api/incidents/{incident_id}/splunk-dashboard")
def incident_splunk_dashboard(incident_id: str) -> Response:
    """Returns a Splunk Simple XML dashboard importable into any Splunk instance."""
    _require_supported_incident(incident_id)
    replay = _get_or_run_replay(incident_id)
    title = replay.title.replace('"', "'")
    xml = dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <dashboard version="1.1" theme="dark">
          <label>BlackBoxOps - {title}</label>
          <description>Incident replay and evidence timeline exported from BlackBoxOps. incident_id={incident_id}</description>

          <row>
            <panel>
              <title>Agent Event Timeline</title>
              <table>
                <search>
                  <query>index=main sourcetype=blackboxops:agent_event incident_id="{incident_id}"
        | eval risk=case(risk_score&gt;=0.9,"critical",risk_score&gt;=0.65,"high",risk_score&gt;=0.35,"medium",1=1,"low")
        | table _time, event_type, actor, summary, risk_score, risk
        | sort _time</query>
                  <earliest>-24h</earliest>
                  <latest>now</latest>
                </search>
              </table>
            </panel>
          </row>

          <row>
            <panel>
              <title>Policy Decisions</title>
              <table>
                <search>
                  <query>index=main sourcetype=blackboxops:agent_event incident_id="{incident_id}" event_type=policy_check
        | spath policy_decision.status output=policy_status
        | spath policy_decision.policy_id output=policy_id
        | spath policy_decision.risk_level output=risk_level
        | table _time, actor, policy_id, policy_status, risk_level
        | sort _time</query>
                  <earliest>-24h</earliest>
                  <latest>now</latest>
                </search>
              </table>
            </panel>
            <panel>
              <title>Risk Score Distribution</title>
              <chart>
                <search>
                  <query>index=main sourcetype=blackboxops:agent_event incident_id="{incident_id}"
        | eval risk=case(risk_score&gt;=0.9,"critical",risk_score&gt;=0.65,"high",risk_score&gt;=0.35,"medium",1=1,"low")
        | stats count by risk
        | sort -count</query>
                  <earliest>-24h</earliest>
                  <latest>now</latest>
                </search>
                <option name="charting.chart">pie</option>
                <option name="charting.chart.colorPalette">list</option>
                <option name="charting.chart.colors">0xFF4444,0xFF9900,0x4F46E5,0x22C55E</option>
              </chart>
            </panel>
          </row>

          <row>
            <panel>
              <title>Evidence References</title>
              <table>
                <search>
                  <query>index=main sourcetype=blackboxops:agent_event incident_id="{incident_id}"
        | spath evidence_refs{{}} output=ev_refs
        | where isnotnull(ev_refs)
        | table _time, actor, ev_refs
        | sort _time</query>
                  <earliest>-24h</earliest>
                  <latest>now</latest>
                </search>
              </table>
            </panel>
          </row>
        </dashboard>
    """)
    return Response(
        content=xml,
        media_type="application/xml",
        headers={"Content-Disposition": f'attachment; filename="blackboxops-{incident_id}.xml"'},
    )


def _proposal_status(decision: PolicyDecision) -> str:
    if decision.status == "approval_required":
        return "pending_approval"
    if decision.status == "block":
        return "blocked"
    if decision.status == "allow":
        return "allowed"
    return "warned"


@app.post("/api/actions/propose", response_model=ActionProposal)
def propose_action(request: ActionProposalRequest) -> ActionProposal:
    _require_supported_incident(request.incident_id)
    replay = _get_or_run_replay(request.incident_id)
    decision = PolicyEngine.from_file("policies/default.yaml").evaluate_action(
        request.action_type,
        request.target,
        request.evidence_refs,
    )
    proposal = ActionProposal(
        incident_id=request.incident_id,
        action_type=request.action_type,
        target=request.target,
        evidence_refs=request.evidence_refs,
        requested_by=request.requested_by,
        reason=request.reason,
        status=_proposal_status(decision),
        decision=decision,
    )
    _ACTION_PROPOSALS.append(proposal)
    replay.events.append(AgentEvent(
        incident_id=request.incident_id,
        session_id=replay.session_id or "sess_unknown",
        event_type="approval",
        actor="blackboxops_gateway",
        risk_score=0.95 if decision.status == "block" else 0.82,
        summary=(
            "Remediation proposal blocked because it was not evidence-bound."
            if decision.status == "block"
            else "Remediation proposal recorded and paused for human approval."
        ),
        payload={
            "action_id": proposal.action_id,
            "action_type": request.action_type,
            "target": request.target,
            "requested_by": request.requested_by,
            "reason": request.reason,
        },
        policy_decision=decision,
    ))
    if decision not in replay.policy_decisions:
        replay.policy_decisions.append(decision)
    return proposal


@app.get("/api/actions", response_model=list[ActionProposal])
def list_action_proposals(incident_id: str | None = None) -> list[ActionProposal]:
    if incident_id is None:
        return _ACTION_PROPOSALS
    _require_supported_incident(incident_id)
    return [p for p in _ACTION_PROPOSALS if p.incident_id == incident_id]


def _find_action_proposal(action_id: str) -> ActionProposal:
    for proposal in _ACTION_PROPOSALS:
        if proposal.action_id == action_id:
            return proposal
    raise HTTPException(status_code=404, detail=f"No action proposal found for action_id={action_id}")


def _review_action(action_id: str, request: ActionReviewRequest, status: str) -> ActionReviewResponse:
    proposal = _find_action_proposal(action_id)
    if proposal.status != "pending_approval":
        raise HTTPException(status_code=409, detail="Only pending approval actions can be approved or rejected")
    now = utc_now().isoformat().replace("+00:00", "Z")
    proposal.status = status  # type: ignore[assignment]
    proposal.review_note = request.note
    proposal.reviewed_at = now
    if status == "approved":
        proposal.approved_by = request.reviewer
    else:
        proposal.rejected_by = request.reviewer

    replay = _get_or_run_replay(proposal.incident_id)
    replay.events.append(AgentEvent(
        incident_id=proposal.incident_id,
        session_id=replay.session_id or "sess_unknown",
        event_type="approval",
        actor="human_reviewer",
        risk_score=0.4 if status == "approved" else 0.2,
        summary=(
            "Human approved pending remediation; execution handed to configured connector."
            if status == "approved"
            else "Human rejected pending remediation; no action executed."
        ),
        payload={
            "action_id": proposal.action_id,
            "decision": status,
            "reviewer": request.reviewer,
            "note": request.note,
            "execution_mode": "connector_pending" if status == "approved" else "not_executed",
        },
    ))

    sig = _sign_approval(action_id, status, request.reviewer, now)
    return ActionReviewResponse(
        action_id=proposal.action_id,
        incident_id=proposal.incident_id,
        status=status,  # type: ignore[arg-type]
        reviewer=request.reviewer,
        note=request.note,
        reviewed_at=now,
        signature=sig,
    )


@app.post("/api/actions/{action_id}/approve", response_model=ActionReviewResponse)
def approve_action(action_id: str, request: ActionReviewRequest) -> ActionReviewResponse:
    return _review_action(action_id, request, "approved")


@app.post("/api/actions/{action_id}/reject", response_model=ActionReviewResponse)
def reject_action(action_id: str, request: ActionReviewRequest) -> ActionReviewResponse:
    return _review_action(action_id, request, "rejected")


def _build_policy_list() -> list[PolicySummary]:
    engine = PolicyEngine.from_file("policies/default.yaml")
    names = {
        "broad-index-search": "Block Broad Index Searches",
        "risky-spl-command": "Block Destructive SPL",
        "prompt-injection-content": "Block Prompt Injection",
        "destructive-action-approval": "Require Approval for Disruptive Actions",
        "low-risk-diagnostic-action": "Allow Read-Only Diagnostics",
    }
    result = [
        PolicySummary(
            policy_id=_demo_policy_id(rule["id"]),
            name=names.get(rule["id"], rule["id"].replace("-", " ").title()),
            description=rule.get("reason", "Policy rule loaded from the safety gateway."),
            status=rule.get("status", "block"),
            risk_level=rule.get("risk_level", "high"),
            splunk_source="mock_splunk",
            original_rule_id=rule["id"],
        )
        for rule in engine.rules
    ]
    for policy in result:
        if policy.policy_id in _POLICY_ENABLED:
            policy.enabled = _POLICY_ENABLED[policy.policy_id]
    return result


@app.get("/api/policies", response_model=list[PolicySummary])
def policies() -> list[PolicySummary]:
    return _build_policy_list()


class PolicyPatchRequest(BaseModel):
    enabled: bool


@app.patch("/api/policies/{policy_id}", response_model=PolicySummary)
def patch_policy(policy_id: str, request: PolicyPatchRequest) -> PolicySummary:
    _POLICY_ENABLED[policy_id] = request.enabled
    for policy in _build_policy_list():
        if policy.policy_id == policy_id:
            return policy
    raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")


@app.post("/api/policy/evaluate-query", response_model=PolicyDecision)
@app.post("/policy/evaluate-query", response_model=PolicyDecision)
def evaluate_query(request: QueryRequest) -> PolicyDecision:
    return PolicyEngine.from_file("policies/default.yaml").evaluate_query(request.query, request.time_range)


@app.post("/api/policy/evaluate-action", response_model=PolicyDecision)
@app.post("/policy/evaluate-action", response_model=PolicyDecision)
def evaluate_action(request: ActionRequest) -> PolicyDecision:
    return PolicyEngine.from_file("policies/default.yaml").evaluate_action(request.action_type, request.target, request.evidence_refs)


_dist_dir = Path("dist")
_index_html = _dist_dir / "index.html"

if _dist_dir.exists():
    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_react_app(full_path: str) -> FileResponse:
        requested = (_dist_dir / full_path).resolve()
        dist_root = _dist_dir.resolve()
        if requested.is_file() and requested.is_relative_to(dist_root):
            return FileResponse(requested)
        if _index_html.exists():
            return FileResponse(_index_html)
        raise HTTPException(status_code=404, detail="React build artifact not found")
