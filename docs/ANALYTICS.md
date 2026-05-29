# ANALYTICS — BlackBoxOps

## Event Taxonomy

blackbox.agent_event_recorded
- Fires whenever an AgentEvent is recorded.
- Properties: event_id, incident_id, session_id, event_type, actor, risk_score, evidence_count.

blackbox.query_evaluated
- Fires when SPL/MCP query is evaluated.
- Properties: incident_id, query_hash, time_range, status, matched_rules, estimated_risk.

blackbox.prompt_injection_detected
- Fires when retrieved content includes instruction-hijack patterns.
- Properties: incident_id, evidence_id, pattern_type, severity.

blackbox.action_evaluated
- Fires when agent proposes an operational action.
- Properties: incident_id, action_type, target, status, risk_level, required_approval.

blackbox.replay_viewed
- Fires when a user views an incident replay.
- Properties: incident_id, event_count, evidence_count, blocked_actions_count.

blackbox.postmortem_generated
- Fires when postmortem is generated.
- Properties: incident_id, evidence_claim_count, missing_data_count, policy_decision_count.

## Operational Metrics

- Total agent events recorded
- Queries allowed/warned/blocked
- Unsafe actions blocked
- Approval-required actions
- Prompt-injection detections
- Evidence coverage ratio = claims_with_evidence / total_claims
- Mean replay generation time
- Demo scenario completion rate

## Dashboard Specs

KPI Row:
- Incidents recorded
- Agent decisions captured
- Queries blocked
- Unsafe actions prevented
- Evidence coverage

Policy Safety Panel:
- Bar chart: allow vs warn vs approval_required vs block
- Table: latest blocked queries/actions

Evidence Quality Panel:
- Evidence coverage ratio
- Missing evidence warnings
- Confidence distribution

Replay Activity Panel:
- Latest incidents
- Event counts by type
- Postmortem generation count

## KPI Definitions

Every agent claim has evidence attached:
- evidence_coverage_ratio >= 0.90 for demo incidents.

Unsafe query/action is blocked or approval-gated:
- unsafe_action_prevention_rate = blocked_or_approval_required / unsafe_actions_detected.
- target: 100% in demo.

Incident replay under 60 seconds:
- replay_render_time_seconds measured from /demo/run response to UI render.
- target: under 5 seconds locally, under 60 seconds in presentation.

## Privacy / Safety

- Do not store real secrets in event payloads.
- Redact bearer tokens, emails, API keys, and passwords in sample events.
- Hash raw query text for analytics when possible, but keep query visible in demo evidence cards.
