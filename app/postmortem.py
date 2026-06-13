from __future__ import annotations

from app.llm import LLMAnalyzer
from app.models import IncidentReplay, Postmortem


def generate_postmortem(replay: IncidentReplay) -> Postmortem:
    llm = LLMAnalyzer()
    recommendation = llm.generate_recommendation(replay)

    lines: list[str] = [
        f"# BlackBoxOps Postmortem — {replay.title}",
        "",
        f"Incident ID: `{replay.incident_id}`",
        f"Status: `{replay.status}`",
        f"Outcome: `{replay.outcome}`",
        "",
        "## Executive Summary",
    ]

    # Use LLM analysis if it was generated during the demo run
    if replay.llm_analysis:
        lines.append(replay.llm_analysis)
    else:
        lines.append(
            "BlackBoxOps recorded the agent investigation, bound claims to Splunk evidence, "
            "and enforced policy before remediation."
        )

    lines.extend(["", "## Timeline"])
    for event in replay.events:
        lines.append(f"- `{event.timestamp.isoformat()}` **{event.event_type}** — {event.summary}")

    lines.extend(["", "## Evidence"])
    for evidence in replay.evidence:
        flags = ", ".join(evidence.risk_flags) or "none"
        message = evidence.sample_event.get("message", str(evidence.sample_event))
        lines.append(
            f"- `{evidence.evidence_id}` query=`{evidence.query}` "
            f"confidence={evidence.confidence:.2f} flags={flags}"
        )
        lines.append("  ```text")
        lines.append(f"  {message}")
        lines.append("  ```")

    lines.extend(["", "## Policy Decisions"])
    for decision in replay.policy_decisions:
        lines.append(
            f"- `{decision.policy_id}` → **{decision.status}** ({decision.risk_level}): {decision.reason}"
        )

    lines.extend(["", "## Recommendation", recommendation])

    return Postmortem(incident_id=replay.incident_id, title=replay.title, markdown="\n".join(lines))
