# AGENTS.md — BlackBoxOps

## Project
BlackBoxOps: Splunk-native flight recorder and safety layer for agentic operations.

## Goal
Win the Splunk Agentic Ops Hackathon Grand Prize with a solo-buildable lightweight MVP.

## Stack
- Python 3.11+
- FastAPI backend
- Streamlit frontend
- Pydantic models
- YAML policy rules
- JSONL mock store
- Splunk HEC/Search/MCP integration hooks
- pytest tests

## Core Rules
1. Demo reliability beats overbuilt integrations.
2. Always support USE_MOCK_SPLUNK=true.
3. Every agent claim must reference evidence_refs.
4. Unsafe actions must be blocked or approval-gated.
5. Policy engine must fail closed.
6. Do not build a generic chatbot.
7. Do not claim we are the first AI-agent flight recorder.
8. Position as Splunk-native evidence and safety layer for agentic operations.
9. Keep the demo deterministic and runnable without internet.
10. Prioritize judge-visible value over hidden complexity.

## Required Files for Devpost
- README.md
- LICENSE
- architecture_diagram.md at repo root
- public source code
- setup/run instructions
- sample data/configs

## Code Conventions
- Keep modules small and readable.
- Pydantic models in app/models.py.
- No hardcoded secrets.
- All config via .env or safe defaults.
- Deterministic demo path must work without network.
- Use clear names: incident_id, session_id, evidence_id, policy_id.

## Test Requirements
- Policy engine tests for allow/block/warn/approval_required.
- Demo flow test that completes using mock data.
- Basic API health test.

## Build Priority
1. Working deterministic demo
2. Replay UI
3. Evidence cards
4. Policy safety gateway
5. Splunk integration hooks
6. Devpost polish
