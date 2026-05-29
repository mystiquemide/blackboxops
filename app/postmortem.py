from __future__ import annotations

from app.models import IncidentReplay, Postmortem


def generate_postmortem(replay: IncidentReplay) -> Postmortem:
    lines: list[str] = [
        f"# BlackBoxOps Postmortem — {replay.title}",
        "",
        f"Incident ID: `{replay.incident_id}`",
        f"Status: `{replay.status}`",
        "",
        "## Executive Summary",
        "BlackBoxOps recorded the agent investigation, bound claims to Splunk evidence, and enforced policy before remediation.",
        "",
        "## Timeline",
    ]
    for event in replay.events:
        lines.append(f"- `{event.timestamp.isoformat()}` **{event.event_type}** — {event.summary}")
    lines.extend(["", "## Evidence"])
    for evidence in replay.evidence:
        flags = ", ".join(evidence.risk_flags) or "none"
        message = evidence.sample_event.get("message", str(evidence.sample_event))
        lines.append(f"- `{evidence.evidence_id}` query=`{evidence.query}` confidence={evidence.confidence:.2f} flags={flags}")
        lines.append("  ```text")
        lines.append(f"  {message}")
        lines.append("  ```")
    lines.extend(["", "## Policy Decisions"])
    for decision in replay.policy_decisions:
        lines.append(f"- `{decision.policy_id}` → **{decision.status}** ({decision.risk_level}): {decision.reason}")
    lines.extend([
        "",
        "## Recommendation",
        "Keep the agent in approval-gated mode for disruptive actions. Investigate the malicious trace payload separately as a prompt-injection attempt against the ops workflow.",
    ])
    return Postmortem(incident_id=replay.incident_id, title=replay.title, markdown="\n".join(lines))
