# Security Policy

## Reporting a vulnerability

Do not open a public issue for security vulnerabilities. Email mide27145@gmail.com with a description of the issue, reproduction steps, and impact. You will get an acknowledgement within 72 hours.

## Scope

BlackBoxOps is a safety layer for agentic operations. Findings of particular interest:

- Policy engine bypasses (actions executing despite block or approval_required decisions)
- Prompt-injection detection evasion in evidence handling
- Authentication or session weaknesses in the API
- Evidence or replay tampering (claims not bound to recorded evidence)

## Design posture

- Fail-closed: when a policy file fails to load or a rule errors, actions are blocked, not allowed.
- Approval-gated: disruptive remediations require a recorded human decision before any connector executes.
- Evidence-bound: replay claims reference recorded evidence IDs, not free text.

See [docs/SECURITY.md](docs/SECURITY.md) for the threat model and full security review.
