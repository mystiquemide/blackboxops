# Architecture - BlackBoxOps

## System Overview

BlackBoxOps sits between AI operations agents and Splunk. It records agent actions, validates Splunk MCP/SPL interactions, enforces policies, stores evidence, and provides a replay and postmortem UI.

**Actors:**
- Platform Engineer: configures policies and reviews agent behavior
- SRE / SOC Analyst: replays incidents and reads evidence-backed postmortems
- AI Ops Agent: investigates incidents and proposes remediation actions
- Splunk: operational evidence store and query engine

## Components

| Component | Responsibility |
|---|---|
| React UI | Landing, auth, incident directory, replay room, policy gateway |
| FastAPI Backend | API routes, event recording, postmortem generation |
| Policy Engine | YAML-driven safety rules: block, warn, allow, approval_required |
| Splunk Adapter | Unified interface for MCP, REST, and offline mode |
| Event Store | Local JSONL in offline mode, Splunk index in live mode |
| Agent Scenario | Deterministic incident scenario for replay demonstration |

## Tech Stack

- Python 3.11+ with FastAPI
- React 19 + TypeScript + Vite
- Pydantic for strict event schema validation
- PyYAML for readable, operator-editable policy rules
- JSONL for lightweight offline event store
- Splunk MCP Server (streamable-HTTP), Splunk REST API, Splunk HEC
- pytest

## Folder Structure

```
blackboxops/
  app/
    main.py            FastAPI routes
    models.py          Pydantic event/evidence/policy models
    recorder.py        JSONL event recorder
    splunk_adapter.py  Mock + MCP + REST Splunk adapter
    policy_engine.py   YAML-driven safety rules
    demo_agent.py      Deterministic incident scenario runner
    postmortem.py      Evidence-backed postmortem generator
    auth.py            Local email/password auth
    auth_google.py     Google OAuth flow
    ui.py              Streamlit fallback UI
  src/                 React + TypeScript frontend
  policies/
    default.yaml       Default safety rules
  data/
    sample_incidents.jsonl
    sample_splunk_events.jsonl
  scripts/
    run_demo.py        CLI demo runner
    seed_splunk.py     Splunk data seeding via REST
  tests/               pytest suite
  docs/                Architecture, deployment, security
```

## Data Models

**AgentEvent** - one recorded step in the agent's operation chain:
- `event_id`, `incident_id`, `session_id`, `timestamp`
- `event_type`: prompt | spl_query | evidence | policy_check | action_proposal | approval
- `actor`, `risk_score`, `summary`, `payload`, `evidence_refs`

**EvidenceRef** - a Splunk query result bound to an agent claim:
- `evidence_id`, `query`, `time_range`
- `source`: offline | splunk_mcp | splunk_search_api
- `sample_event`, `confidence`, `risk_flags`

**PolicyDecision** - the safety gateway's verdict on an action or query:
- `decision_id`, `policy_id`
- `status`: allow | block | approval_required | warn
- `reason`, `risk_level`, `matched_rules`

## API Routes

```
GET  /api/health
POST /api/demo/run
GET  /api/incidents
GET  /api/incidents/{id}/replay
GET  /api/incidents/{id}/postmortem
POST /api/actions/propose
POST /api/actions/{id}/approve
POST /api/actions/{id}/reject
GET  /api/policies
PATCH /api/policies/{id}
POST /api/auth/signup
POST /api/auth/signin
POST /api/auth/demo
GET  /api/auth/me
GET  /api/auth/google/login
GET  /api/auth/google/callback
```

## Failure Design

- Splunk unavailable: `USE_MOCK_SPLUNK=true` falls back to local JSONL evidence dataset
- MCP unreachable: error degrades to a descriptive evidence card, replay continues
- Bad policy YAML: fail closed, block all high-risk actions
- Empty evidence: agent cannot propose remediation; postmortem records insufficient evidence

## Architecture Decisions

**ADR-001: Unified adapter boundary**
All Splunk access goes through `splunk_adapter.py`. MCP, REST, and offline mode are interchangeable behind the same interface. Callers never know which mode is active.

**ADR-002: Mock-first with live integration hooks**
The offline incident dataset makes the product evaluable without infrastructure. The same adapter connects to a real Splunk MCP Server when available.

**ADR-003: YAML policy engine**
Rules live in `policies/default.yaml`. Operators can read, audit, and modify them without touching code.

**ADR-004: Evidence-bound postmortems**
Every claim in a generated postmortem must reference a recorded `evidence_ref`. Unbound claims are not permitted.

**ADR-005: Fail-closed policy gateway**
If the policy engine cannot load or evaluate a rule, the default outcome is block. No action proceeds on uncertainty.
