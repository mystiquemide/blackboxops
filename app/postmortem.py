from __future__ import annotations

from datetime import datetime, timezone

from app.llm import LLMAnalyzer
from app.models import IncidentReplay, Postmortem


def generate_postmortem(replay: IncidentReplay) -> Postmortem:
    llm = LLMAnalyzer()
    recommendation = llm.generate_recommendation(replay)

    lines: list[str] = [
        f"# BlackBoxOps Postmortem - {replay.title}",
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
        lines.append(f"- `{event.timestamp.isoformat()}` **{event.event_type}** - {event.summary}")

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


def generate_postmortem_html(replay: IncidentReplay, signature: str | None = None) -> str:
    """Print-ready HTML postmortem. Open in browser, Ctrl+P to export PDF."""
    llm = LLMAnalyzer()
    recommendation = llm.generate_recommendation(replay)
    analysis = replay.llm_analysis or "AI analysis was not available for this incident run."

    blocks = sum(1 for d in replay.policy_decisions if d.status == "block")
    outcome_label = "BLOCKED" if blocks else "RECORDED"
    outcome_color = "#f44336" if blocks else "#00c853"
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    def risk_class(score: float) -> str:
        if score >= 0.9: return "critical"
        if score >= 0.65: return "high"
        if score >= 0.35: return "medium"
        return "low"

    event_rows = ""
    for ev in replay.events:
        rc = risk_class(ev.risk_score)
        ts = ev.timestamp.isoformat() if hasattr(ev.timestamp, "isoformat") else str(ev.timestamp)
        event_rows += (
            f"<tr>"
            f"<td class='mono'>{ts}</td>"
            f"<td><span class='etype'>{ev.event_type}</span></td>"
            f"<td>{ev.summary}</td>"
            f"<td class='mono dim'>{ev.actor}</td>"
            f"<td><span class='risk {rc}'>{rc}</span></td>"
            f"</tr>"
        )

    evidence_html = ""
    for ev in replay.evidence:
        flags_html = "".join(f"<span class='flag'>{f}</span>" for f in ev.risk_flags)
        msg = ev.sample_event.get("message", str(ev.sample_event))[:400]
        safe_q = ev.query.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        evidence_html += (
            f"<div class='ev-item'>"
            f"<div class='ev-head'>"
            f"<span class='mono bold'>{ev.evidence_id}</span>"
            f"<span class='dim'>conf: {ev.confidence:.0%}</span>"
            f"<span class='source-tag'>{ev.source}</span>"
            f"</div>"
            f"<pre class='query-block'>{safe_q}</pre>"
            f"<div class='ev-msg'>{msg}</div>"
            f"{'<div class=ev-flags>' + flags_html + '</div>' if ev.risk_flags else ''}"
            f"</div>"
        )

    policy_html = ""
    for p in replay.policy_decisions:
        sc = "badge-block" if p.status == "block" else "badge-allow" if p.status == "allow" else "badge-warn"
        rules_html = "".join(f"<code>{r}</code>" for r in p.matched_rules)
        policy_html += (
            f"<div class='pol-item'>"
            f"<div class='pol-head'>"
            f"<span class='mono bold'>{p.policy_id}</span>"
            f"<span class='{sc}'>{p.status.upper()}</span>"
            f"<span class='risk {p.risk_level}'>{p.risk_level}</span>"
            f"</div>"
            f"<div class='pol-reason'>{p.reason}</div>"
            f"<div class='pol-rules'>{rules_html}</div>"
            f"</div>"
        )

    sig_section = ""
    if signature:
        sig_section = (
            f"<section>"
            f"<h2>Signed Decision Record</h2>"
            f"<div class='sig-block'>"
            f"<div class='sig-label'>HMAC-SHA256 - Tamper-proof cryptographic approval record</div>"
            f"<code class='sig-code'>{signature}</code>"
            f"</div>"
            f"</section>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BlackBoxOps - {replay.title}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 13px; line-height: 1.6; background: #fff; color: #0f172a; padding: 32px; max-width: 900px; margin: 0 auto; }}
  .print-btn {{ display: flex; align-items: center; gap: 8px; margin-bottom: 24px; padding: 10px 18px; background: #0f172a; color: #fff; border: 0; border-radius: 7px; cursor: pointer; font-size: 13px; font-weight: 700; }}
  .print-btn:hover {{ background: #1e293b; }}
  @media print {{ .print-btn, .no-print {{ display: none !important; }} body {{ padding: 0; }} }}
  h1 {{ font-size: 22px; font-weight: 800; letter-spacing: -.03em; margin-bottom: 4px; }}
  h2 {{ font-size: 13px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: #475569; margin: 28px 0 12px; padding-bottom: 6px; border-bottom: 1px solid #e2e8f0; }}
  .brand {{ display: flex; align-items: center; gap: 10px; margin-bottom: 20px; padding-bottom: 20px; border-bottom: 2px solid #0f172a; }}
  .brand-mark {{ display: inline-flex; align-items: center; gap: 5px; font-size: 13px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }}
  .brand-dot {{ width: 8px; height: 8px; border-radius: 50%; background: #00c853; }}
  .meta-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }}
  .meta-cell {{ padding: 10px 12px; border: 1px solid #e2e8f0; border-radius: 7px; background: #f8fafc; }}
  .meta-label {{ font-size: 10px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: #94a3b8; margin-bottom: 3px; }}
  .meta-value {{ font-size: 14px; font-weight: 800; }}
  .outcome {{ color: {outcome_color}; }}
  section {{ margin-bottom: 24px; }}
  .analysis-box {{ padding: 14px 16px; background: #f0f4ff; border-left: 3px solid #6366f1; border-radius: 0 7px 7px 0; font-size: 13px; line-height: 1.7; color: #1e293b; }}
  .rec-box {{ padding: 14px 16px; background: #f0fdf4; border-left: 3px solid #00c853; border-radius: 0 7px 7px 0; font-size: 13px; line-height: 1.7; color: #1e293b; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  th {{ padding: 7px 10px; background: #f1f5f9; text-align: left; font-size: 10px; font-weight: 700; letter-spacing: .07em; text-transform: uppercase; color: #64748b; border-bottom: 1px solid #e2e8f0; }}
  td {{ padding: 7px 10px; border-bottom: 1px solid #f1f5f9; vertical-align: top; }}
  .mono {{ font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 11px; }}
  .bold {{ font-weight: 700; }}
  .dim {{ color: #94a3b8; }}
  .etype {{ display: inline-block; padding: 2px 7px; background: #f1f5f9; border-radius: 4px; font-size: 10px; font-weight: 700; letter-spacing: .06em; color: #475569; }}
  .risk {{ display: inline-block; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-weight: 700; }}
  .risk.critical {{ background: #fef2f2; color: #dc2626; }}
  .risk.high {{ background: #fff7ed; color: #ea580c; }}
  .risk.medium {{ background: #fefce8; color: #ca8a04; }}
  .risk.low {{ background: #f0fdf4; color: #16a34a; }}
  .ev-item {{ padding: 12px; margin-bottom: 10px; border: 1px solid #e2e8f0; border-radius: 8px; background: #fafbfc; }}
  .ev-head {{ display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }}
  .source-tag {{ padding: 2px 8px; background: #eff6ff; color: #3b82f6; border-radius: 4px; font-size: 10px; font-weight: 700; }}
  .query-block {{ padding: 8px 10px; background: #0f172a; color: #94a3b8; border-radius: 6px; font-family: monospace; font-size: 11px; white-space: pre-wrap; overflow-wrap: break-word; margin-bottom: 8px; }}
  .ev-msg {{ font-size: 12px; color: #1e293b; padding: 6px 8px; background: #f8fafc; border-radius: 4px; border-left: 2px solid #e2e8f0; }}
  .ev-flags {{ display: flex; gap: 6px; flex-wrap: wrap; margin-top: 7px; }}
  .flag {{ padding: 2px 8px; background: #fef2f2; color: #dc2626; border-radius: 4px; font-size: 10px; font-weight: 700; }}
  .pol-item {{ padding: 12px; margin-bottom: 10px; border: 1px solid #e2e8f0; border-radius: 8px; }}
  .pol-head {{ display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }}
  .badge-block {{ padding: 2px 8px; background: #fef2f2; color: #dc2626; border-radius: 4px; font-size: 10px; font-weight: 700; }}
  .badge-allow {{ padding: 2px 8px; background: #f0fdf4; color: #16a34a; border-radius: 4px; font-size: 10px; font-weight: 700; }}
  .badge-warn {{ padding: 2px 8px; background: #fff7ed; color: #ea580c; border-radius: 4px; font-size: 10px; font-weight: 700; }}
  .pol-reason {{ font-size: 12px; color: #475569; margin-bottom: 6px; }}
  .pol-rules {{ display: flex; gap: 5px; flex-wrap: wrap; }}
  .pol-rules code {{ padding: 2px 7px; background: #f1f5f9; border-radius: 4px; font-size: 10px; color: #64748b; }}
  .sig-block {{ padding: 14px 16px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; }}
  .sig-label {{ font-size: 11px; font-weight: 700; color: #15803d; margin-bottom: 8px; }}
  .sig-code {{ display: block; word-break: break-all; font-family: monospace; font-size: 11px; color: #1e293b; background: #fff; padding: 8px 10px; border-radius: 5px; border: 1px solid #d1fae5; }}
  footer {{ margin-top: 32px; padding-top: 16px; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-between; color: #94a3b8; font-size: 11px; }}
</style>
</head>
<body>
<button class="print-btn no-print" onclick="window.print()">&#128438; Export as PDF</button>
<div class="brand">
  <div class="brand-mark"><span class="brand-dot"></span>BLACKBOXOPS</div>
  <span style="color:#94a3b8;font-size:11px;font-weight:600;">Incident Postmortem Report</span>
</div>
<h1>{replay.title}</h1>
<div class="meta-grid">
  <div class="meta-cell"><div class="meta-label">Incident ID</div><div class="meta-value mono" style="font-size:11px">{replay.incident_id}</div></div>
  <div class="meta-cell"><div class="meta-label">Status</div><div class="meta-value">{replay.status}</div></div>
  <div class="meta-cell"><div class="meta-label">Outcome</div><div class="meta-value outcome">{outcome_label}</div></div>
  <div class="meta-cell"><div class="meta-label">Generated</div><div class="meta-value mono" style="font-size:11px">{generated_at}</div></div>
</div>

<section>
  <h2>Executive Summary</h2>
  <div class="analysis-box">{analysis}</div>
</section>

<section>
  <h2>Agent Event Timeline</h2>
  <table>
    <thead><tr><th>Timestamp</th><th>Event Type</th><th>Summary</th><th>Actor</th><th>Risk</th></tr></thead>
    <tbody>{event_rows}</tbody>
  </table>
</section>

<section>
  <h2>Evidence Chain ({len(replay.evidence)} refs)</h2>
  {evidence_html or '<p style="color:#94a3b8">No evidence refs recorded.</p>'}
</section>

<section>
  <h2>Policy Decisions ({len(replay.policy_decisions)})</h2>
  {policy_html or '<p style="color:#94a3b8">No policy decisions recorded.</p>'}
</section>

<section>
  <h2>Recommendation</h2>
  <div class="rec-box">{recommendation}</div>
</section>

{sig_section}

<footer>
  <span>BlackBoxOps - Splunk-native flight recorder for agentic operations</span>
  <span>incident_id: {replay.incident_id} &middot; {generated_at}</span>
</footer>
</body>
</html>"""
