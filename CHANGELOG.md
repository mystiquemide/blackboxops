# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-06-11

### Added

- Splunk Cloud Platform integration: MCP Server over streamable HTTP at `/en-US/splunkd/__raw/services/mcp`, verified end-to-end against a live Splunk Cloud instance
- HEC ingestion script (`scripts/load_splunk_data.py`) for seeding demo events with current timestamps before each demo run
- MCP end-to-end test script (`scripts/test_mcp.py`): runs a live SPL query, evaluates results through the policy engine, reports injection detections

### Changed

- `splunk_adapter.py`: appends `| spath` to all MCP queries for JSON `_raw` field extraction; passes `earliest`/`latest` time params; falls back to regex and JSON parsing for non-KV `_raw` values
- UI polish: removed gradient fills from all card components, replaced with flat surfaces; fixed run-button hover color (indigo, not green); removed Unicode symbol from dashboard status text
- `.env.example`: added `SESSION_SECRET`, `AUTH_PROVIDER`, `SPLUNK_HEC_URL`; corrected `SPLUNK_MCP_VERIFY_TLS` default for Splunk Cloud
- `scripts/test_mcp.py` and `scripts/load_splunk_data.py`: removed hardcoded tokens, now read exclusively from environment variables

## [1.0.0] - 2026-06-10

### Added

- Initial public release
- Deterministic incident replay: agent event chain, evidence cards, policy decisions, postmortem export
- Fail-closed policy engine (YAML rules): block, warn, allow, approval_required outcomes
- Prompt-injection detection on Splunk log evidence with replayable block decisions
- Human approval workflow: propose remediation, policy gate, signed approve/reject recorded in replay
- Splunk MCP Server client (`USE_SPLUNK_MCP=true`): streamable-HTTP tool calls with defensive tool discovery
- Splunk REST search and HEC ingestion hooks behind the same adapter boundary
- React + TypeScript UI: landing, auth (local, Google OAuth, free workspace), replay room, incident directory, policy gateway
- FastAPI backend serving the built React app and `/api/*` routes
- Streamlit fallback UI
- CI (pytest + lint + build), CodeQL analysis, Dependabot updates
- Deployment docs, Dockerfile, docker-compose
