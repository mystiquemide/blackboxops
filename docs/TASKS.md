# TASKS — BlackBoxOps

Ordered implementation plan for a solo lightweight build.

## Setup

Task 1: Initialize Python project structure
Owner: DEVOPS
Complexity: S
Depends on: none
Done when: folders app/, data/, policies/, tests/, scripts/ exist with placeholder __init__.py files where needed.

Task 2: Create dependency files
Owner: DEVOPS
Complexity: S
Depends on: Task 1
Done when requirements.txt and .env.example include FastAPI, Streamlit, Pydantic, PyYAML, HTTPX/Requests, pytest, python-dotenv.

Task 3: Add sample incident datasets
Owner: DATA_ANALYST
Complexity: S
Depends on: Task 1
Done when data/sample_incidents.jsonl and data/sample_splunk_events.jsonl contain outage, prompt-injection, blocked-query, and safe-remediation examples.

## Contracts / Data Models

Task 4: Implement Pydantic event models — CRITICAL PATH
Owner: BACKEND
Complexity: M
Depends on: Task 2
Done when AgentEvent, EvidenceRef, PolicyDecision, IncidentReplay, and Postmortem models validate sample data.

Task 5: Define policy YAML format
Owner: SECURITY
Complexity: S
Depends on: Task 4
Done when policies/default.yaml defines risky SPL, broad index search, prompt-injection, action-risk, and approval rules.

## Backend

Task 6: Build event recorder service — CRITICAL PATH
Owner: BACKEND
Complexity: M
Depends on: Task 4
Done when code can append events to local JSONL and optionally send to Splunk HEC.

Task 7: Build Splunk adapter with mock fallback — CRITICAL PATH
Owner: BACKEND
Complexity: M
Depends on: Task 4
Done when adapter supports mock_search(query, time_range) and real HEC/search stubs behind USE_MOCK_SPLUNK.

Task 8: Build MCP/query safety gateway — CRITICAL PATH
Owner: SECURITY/BACKEND
Complexity: M
Depends on: Task 5, Task 7
Done when risky queries are blocked/rewritten and every allow/block decision is recorded.

Task 9: Build prompt-injection detector
Owner: SECURITY
Complexity: S
Depends on: Task 8
Done when retrieved log content containing instruction hijacks is flagged and linked to evidence.

Task 10: Build demo agent runner — CRITICAL PATH
Owner: BACKEND
Complexity: M
Depends on: Task 6, Task 8, Task 9
Done when one command simulates full incident: anomaly -> query -> evidence -> risk -> policy -> action proposal -> postmortem.

Task 11: Build postmortem generator
Owner: BACKEND
Complexity: M
Depends on: Task 10
Done when incident replay produces a markdown report with timeline, evidence, policy decisions, and recommendation.

Task 12: Expose FastAPI endpoints
Owner: BACKEND
Complexity: M
Depends on: Task 10, Task 11
Done when /incidents, /incidents/{id}/replay, /incidents/{id}/postmortem, /demo/run return JSON.

## Frontend

Task 13: Build Streamlit dashboard shell
Owner: FRONTEND
Complexity: S
Depends on: Task 12
Done when app loads incident list, selected incident, and demo-run button.

Task 14: Build incident replay timeline — CRITICAL PATH
Owner: FRONTEND
Complexity: M
Depends on: Task 13
Done when agent prompts, SPL queries, evidence, policy checks, and action proposals render chronologically.

Task 15: Build evidence cards
Owner: FRONTEND
Complexity: S
Depends on: Task 14
Done when each agent claim displays query, time range, sample event, confidence, and risk labels.

Task 16: Build policy decision panel
Owner: FRONTEND/SECURITY
Complexity: S
Depends on: Task 14
Done when blocked/allowed/approval-required decisions are visually distinct.

Task 17: Build postmortem tab
Owner: FRONTEND
Complexity: S
Depends on: Task 11, Task 13
Done when postmortem markdown renders and can be copied.

## Documentation / Submission

Task 18: Create architecture_diagram.md — CRITICAL PATH
Owner: ARCHITECT
Complexity: S
Depends on: docs/ARCHITECTURE.md
Done when repo root contains architecture_diagram.md showing Splunk, MCP, AI agent, gateway, policy engine, and UI data flow.

Task 19: Write README.md
Owner: DEVOPS
Complexity: M
Depends on: Task 12, Task 17
Done when README explains setup, mock mode, Splunk mode, demo scenario, and Devpost positioning.

Task 20: Write Devpost submission draft
Owner: PRODUCT_MANAGER
Complexity: S
Depends on: Task 18, Task 19
Done when docs/DEVPOST_SUBMISSION.md includes pitch, features, how AI/Splunk are used, track, and differentiation.

Task 21: Write 3-minute demo script
Owner: PRODUCT_MANAGER/DESIGNER
Complexity: S
Depends on: Task 17
Done when docs/DEMO_SCRIPT.md has timestamps and narration.

## Testing

Task 22: Unit test policy engine
Owner: QA_TESTER
Complexity: S
Depends on: Task 8
Done when tests cover broad query block, safe query allow, prompt-injection flag, approval required.

Task 23: End-to-end demo test
Owner: QA_TESTER
Complexity: M
Depends on: Task 17
Done when one command starts backend/frontend and demo scenario completes without manual data edits.

Task 24: Submission readiness check
Owner: QA_TESTER/DEVOPS
Complexity: S
Depends on: Task 18, Task 19, Task 21, Task 23
Done when repo contains license, README, architecture_diagram.md, working demo, sample data, and clear instructions.
