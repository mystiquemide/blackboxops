# ARCHITECTURE — BlackBoxOps

## 1. System Architecture

BlackBoxOps sits between AI operations agents and Splunk. It records agent actions, validates Splunk MCP/SPL interactions, enforces policies, stores evidence, and provides replay/postmortem UI.

Actors:
- Platform Engineer: configures policies and reviews agent behavior.
- SRE/SOC Analyst: replays incidents and reads evidence-backed postmortems.
- AI Ops Agent: investigates incidents and proposes actions.
- Splunk: operational evidence store and query engine.

Containers:
- Streamlit UI: dashboard, incident replay, evidence cards, postmortem viewer.
- FastAPI Backend: API endpoints, event recording, demo runner, postmortem generation.
- Policy Engine: YAML-driven safety rules for SPL queries, log-content risks, and action approvals.
- Splunk Adapter: mock mode plus real Splunk HEC/search/MCP integration hooks.
- Event Store: local JSONL in mock mode, Splunk index in Splunk mode.
- Demo Agent: deterministic agent scenario for hackathon demo.

Components:
- models.py: Pydantic models.
- recorder.py: writes AgentEvent records.
- splunk_adapter.py: mock and real Splunk query/ingest interface.
- policy_engine.py: evaluates query/content/action rules.
- demo_agent.py: runs full incident scenario.
- postmortem.py: builds markdown summary from replay events.
- main.py: FastAPI routes.
- ui.py: Streamlit UI.

## 2. Tech Stack

- Python 3.11+: fastest solo implementation.
- FastAPI: simple JSON API and future extensibility.
- Streamlit: fastest polished dashboard for hackathon demo.
- Pydantic: strict event schema validation.
- PyYAML: readable policy rules.
- JSONL: lightweight mock event store.
- Splunk HEC/Search/MCP: real integration path; mock fallback protects demo schedule.
- pytest: quick policy and end-to-end tests.

## 3. Folder Structure

blackboxops/
  README.md
  LICENSE
  .env.example
  requirements.txt
  architecture_diagram.md
  AGENTS.md
  memory.md
  app/
    __init__.py
    main.py
    ui.py
    models.py
    recorder.py
    splunk_adapter.py
    policy_engine.py
    demo_agent.py
    postmortem.py
  data/
    sample_incidents.jsonl
    sample_splunk_events.jsonl
    blackbox_events.jsonl
  policies/
    default.yaml
  scripts/
    run_demo.py
    seed_data.py
  tests/
    test_policy_engine.py
    test_demo_flow.py
  docs/
    PRD.md
    COMPETITOR_RESEARCH.md
    TASKS.md
    ARCHITECTURE.md
    DESIGN.md
    ANALYTICS.md
    DEVPOST_SUBMISSION.md
    DEMO_SCRIPT.md

## 4. Data Models

AgentEvent:
- event_id
- incident_id
- session_id
- timestamp
- event_type: prompt | response | spl_query | evidence | policy_check | action_proposal | approval | remediation_result
- actor
- risk_score
- summary
- payload
- evidence_refs

EvidenceRef:
- evidence_id
- query
- time_range
- source: mock_splunk | splunk_mcp | splunk_search_api
- sample_event
- confidence
- risk_flags

PolicyDecision:
- decision_id
- policy_id
- status: allow | block | approval_required | warn
- reason
- risk_level: low | medium | high | critical
- matched_rules
- required_approval

IncidentReplay:
- incident_id
- title
- status
- events
- evidence
- policy_decisions

## 5. API Contracts

GET /health
- Returns service status.

POST /demo/run
- Runs deterministic demo scenario.
- Returns IncidentReplay JSON.

GET /incidents
- Returns list of incidents.

GET /incidents/{incident_id}/replay
- Returns full replay timeline.

GET /incidents/{incident_id}/postmortem
- Returns markdown postmortem.

POST /policy/evaluate-query
- Request: query + time_range.
- Response: PolicyDecision.

POST /policy/evaluate-action
- Request: action_type + target + evidence_refs.
- Response: PolicyDecision.

## 6. Failure Design

- Splunk unavailable: use USE_MOCK_SPLUNK=true and local JSONL sample data.
- LLM unavailable: deterministic template summary fallback.
- MCP unavailable: use Splunk adapter interface with mock query results.
- Bad policy YAML: fail closed and block high-risk action.
- Empty evidence: agent cannot propose remediation; postmortem says insufficient evidence.

## 7. ADRs

ADR-001: Use Python + FastAPI + Streamlit
Decision: Use Python stack for speed.
Consequence: Faster solo build; less custom UI polish than Next.js but enough for demo.

ADR-002: Mock-first Splunk adapter with real integration hooks
Decision: Build mock mode first, then connect real Splunk if setup is stable.
Consequence: Demo is reliable; still shows credible Splunk integration path.

ADR-003: YAML policy engine
Decision: Store rules in policies/default.yaml.
Consequence: Easy for judges to read and modify; avoids overbuilding.

ADR-004: Evidence-bound postmortems
Decision: Every postmortem claim must link to evidence_refs.
Consequence: Strong differentiation from generic incident copilots.

ADR-005: Submit under Platform & Developer Experience
Decision: Position as infrastructure for safe Splunk-powered agents.
Consequence: Avoids crowded generic SOC/observability copilot track while still supporting those use cases.
