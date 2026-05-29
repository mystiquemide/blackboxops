# BlackBoxOps Security Notes

## Threat model covered by MVP

- Prompt injection embedded in operational logs.
- Broad all-index SPL queries that expose unrelated data.
- Destructive SPL command patterns.
- Disruptive remediation actions attempted without approval.
- Missing evidence for operational actions.

## Current controls

- YAML policy engine fails closed on policy load errors.
- Destructive and broad SPL patterns are blocked.
- Prompt-injection content is blocked and attached to evidence.
- Disruptive actions require approval and evidence_refs.
- No secrets are committed; `.env.example` includes key names only.

## Known limitations

- Real Splunk MCP integration is an adapter hook in this MVP.
- Policy matching is deterministic substring matching, not full SPL parsing.
- Approval is modeled as a policy decision, not signed workflow state.
