# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
