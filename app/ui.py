from __future__ import annotations

import html

import streamlit as st

from app.brand import BRAND_TOKENS, build_brand_css, policy_label, risk_label
from app.demo_agent import run_demo_incident
from app.postmortem import generate_postmortem

st.set_page_config(page_title="BlackBoxOps", layout="wide", page_icon="▰")
st.markdown(build_brand_css(), unsafe_allow_html=True)

# ── Init replay ──
if "replay" not in st.session_state:
    st.session_state.replay = run_demo_incident()

replay = st.session_state.replay
t = BRAND_TOKENS


# ═══════════════════════════════════════════
# NAV
# ═══════════════════════════════════════════
st.markdown(
    f"""
    <nav class="bb-nav">
      <a href="/" class="bb-nav-logo">BlackBox<span>Ops</span></a>
      <ul class="bb-nav-links">
        <li><a href="https://github.com/olamide203" target="_blank">GitHub</a></li>
        <li><a class="bb-nav-cta" href="https://splunk.com" target="_blank">Splunk</a></li>
      </ul>
    </nav>
    """,
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════
st.markdown(
    """
    <section class="bb-section-hero">
      <div class="bb-hero">
        <p class="bb-kicker">SPLUNK-NATIVE SAFETY LAYER</p>
        <h1 class="bb-hero-title">The flight recorder for<br/>agentic operations.</h1>
        <p class="bb-hero-subtitle">
          Record every AI decision, Splunk query, evidence reference, policy check, and remediation
          attempt — then replay incidents with proof instead of vibes.
        </p>
      </div>
    </section>
    <hr class="bb-divider"/>
    """,
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════
# DARK SECTION — Safety Plane Dashboard
# ═══════════════════════════════════════════
st.markdown(f"""
<div class="bb-section-dark" id="demo">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:32px;">
    <span style="font-family:var(--font-sans);font-size:12px;font-weight:600;color:var(--bb-ink-muted);letter-spacing:0.08em;">BLACKBOXOPS · SAFETY PLANE</span>
    <span style="display:flex;align-items:center;gap:6px;font-family:var(--font-sans);font-size:12px;font-weight:500;color:var(--bb-green);">
      <span class="bb-recording-dot"></span> RECORDING
    </span>
  </div>
  <h2 style="font-family:var(--font-serif)!important;font-size:clamp(26px,3.5vw,40px)!important;font-weight:400!important;color:var(--bb-ink)!important;margin:0 0 32px!important;letter-spacing:-0.025em!important;padding:0!important;">
    Agentic session guarded.
  </h2>
  <div class="bb-dash-metrics">
    <div class="bb-dash-metric">
      <div class="bb-dash-metric-label">Events</div>
      <div class="bb-dash-metric-value">{len(replay.events)}</div>
    </div>
    <div class="bb-dash-metric">
      <div class="bb-dash-metric-label">Evidence Refs</div>
      <div class="bb-dash-metric-value">{len(replay.evidence)}</div>
    </div>
    <div class="bb-dash-metric">
      <div class="bb-dash-metric-label">Policy Decisions</div>
      <div class="bb-dash-metric-value">{len(replay.policy_decisions)}</div>
      <div class="bb-dash-metric-delta">{sum(1 for d in replay.policy_decisions if d.status == 'block')} blocked</div>
    </div>
    <div class="bb-dash-metric">
      <div class="bb-dash-metric-label">Approvals Needed</div>
      <div class="bb-dash-metric-value">{sum(1 for d in replay.policy_decisions if d.required_approval)}</div>
    </div>
  </div>
</div>
<hr class="bb-divider"/>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════
# INCIDENT COMMAND RAIL
# ═══════════════════════════════════════════
st.markdown(
    '<div style="max-width:var(--max-w);margin:40px auto 0;padding:0 var(--px);"><p class="bb-section-kicker">Incident Command Rail</p></div>',
    unsafe_allow_html=True,
)

cmd_col1, cmd_col2 = st.columns([3, 1], gap="large")
with cmd_col1:
    st.markdown(
        f"""
        <div class="bb-card" style="animation:bb-fade-up 0.6s var(--ease-out-expo) both;">
          <div class="bb-card-title">Checkout prompt-injection incident</div>
          <div class="bb-meta">incident_id={html.escape(replay.incident_id)}</div>
          <p style="font-family:var(--font-sans);color:var(--bb-ink-secondary);margin-top:12px;font-size:15px;line-height:1.55;">
            A deterministic agentic ops incident where malicious log content tries to hijack the AI agent.
          </p>
          <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:14px;">
            <span class="bb-chip bb-chip-sm bb-chip--risk-medium">&bullet; MCP-ready</span>
            <span class="bb-chip bb-chip-sm bb-chip--risk-low">&bullet; Mock mode safe</span>
            <span class="bb-chip bb-chip-sm bb-chip--risk-critical">&bullet; Injection demo</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with cmd_col2:
    if st.button("Run Demo", type="primary", use_container_width=True):
        st.session_state.replay = run_demo_incident()
        replay = st.session_state.replay
        st.toast("Replay recorded. Evidence and policy decisions are ready.", icon="▰")
    st.markdown(
        """
        <div class="bb-card" style="margin-top:16px;text-align:center;animation:bb-fade-up 0.6s var(--ease-out-expo) 0.15s both;">
          <div style="font-family:var(--font-sans);font-size:13px;color:var(--bb-ink-muted);">BB-0 says</div>
          <div style="font-family:var(--font-serif);font-size:18px;color:var(--bb-ink);margin-top:4px;line-height:1.3;">
            Evidence bound.<br>Replay ready.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════
# REPLAY TIMELINE + EVIDENCE/POLICY
# ═══════════════════════════════════════════
st.markdown('<hr class="bb-divider" style="margin-top:40px;"/>', unsafe_allow_html=True)
st.markdown(
    '<div style="max-width:var(--max-w);margin:40px auto 0;padding:0 var(--px);"><p class="bb-section-kicker">Replay Timeline</p></div>',
    unsafe_allow_html=True,
)

tl_col, ev_col = st.columns([1.2, 1], gap="large")

with tl_col:
    st.markdown('<div class="bb-timeline">', unsafe_allow_html=True)
    for index, event in enumerate(replay.events, start=1):
        risk = risk_label(event.risk_score)
        event_type = html.escape(event.event_type.replace("_", " ").title())
        summary = html.escape(event.summary)
        actor = html.escape(event.actor)
        evidence_refs = ", ".join(e.evidence_id for e in event.evidence_refs) or "none"
        dot_class = f"bb-timeline-dot--{risk['level']}"
        st.markdown(
            f"""
            <div class="bb-timeline-item">
              <div class="bb-timeline-dot {dot_class}"></div>
              <div class="bb-card" style="flex:1;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap;">
                  <span class="bb-chip bb-chip-sm bb-chip--risk-{risk['level']}">{risk['icon']} {risk['text']}</span>
                  <span class="bb-chip bb-chip-sm">#{index:02d} {event_type}</span>
                </div>
                <div class="bb-card-title">{summary}</div>
                <div class="bb-meta">actor={actor} · event_id={html.escape(event.event_id)}</div>
                <div class="bb-meta">evidence_refs={html.escape(evidence_refs)}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if event.policy_decision:
            st.caption("_policy decision_")
            st.code(event.policy_decision.model_dump_json(indent=2), language="json")
    st.markdown('</div>', unsafe_allow_html=True)

with ev_col:
    tab_evidence, tab_policy, tab_postmortem = st.tabs(["Evidence", "Policy", "Postmortem"])

    with tab_evidence:
        st.markdown('<p class="bb-section-kicker">Splunk Evidence Plane</p>', unsafe_allow_html=True)
        for evidence in replay.evidence:
            flags = ", ".join(evidence.risk_flags) or "none"
            message = evidence.sample_event.get("message", "")
            is_injection = "prompt-injection" in evidence.risk_flags
            border = "bb-policy-block" if is_injection else ""
            st.markdown(
                f"""
                <div class="bb-evidence-card {border}">
                  <div class="bb-card-title">{html.escape(evidence.evidence_id)}</div>
                  <div class="bb-meta">confidence={evidence.confidence:.2f} &middot; source={html.escape(evidence.source)}</div>
                  <div style="display:flex;gap:6px;margin-top:10px;flex-wrap:wrap;">
                    <span class="bb-chip bb-chip-sm bb-chip--risk-medium">Evidence</span>
                    <span class="bb-chip bb-chip-sm">flags={html.escape(flags)}</span>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.code(evidence.query, language="sql")
            st.code(message, language="text")

    with tab_policy:
        st.markdown('<p class="bb-section-kicker">Safety Gateway</p>', unsafe_allow_html=True)
        for decision in replay.policy_decisions:
            label = policy_label(decision.status)
            border_map = {
                "allow": "bb-policy-allow",
                "block": "bb-policy-block",
                "warn": "bb-policy-warn",
                "approval_required": "bb-policy-approval",
            }
            border_cls = border_map.get(decision.status, "")
            risk_cls_map = {"block": "critical", "approval_required": "high", "warn": "medium", "allow": "low"}
            risk_cls = risk_cls_map.get(decision.status, "low")
            st.markdown(
                f"""
                <div class="bb-evidence-card {border_cls}">
                  <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                    <span class="bb-chip bb-chip-sm bb-chip--risk-{risk_cls}">{label['icon']} {label['text']}</span>
                  </div>
                  <div class="bb-card-title">{html.escape(decision.policy_id)}</div>
                  <div style="font-size:14px;color:var(--bb-ink-secondary);line-height:1.55;margin:6px 0;">
                    {html.escape(decision.reason)}
                  </div>
                  <div class="bb-meta" style="margin-top:8px;">
                    risk={html.escape(decision.risk_level)} &middot; matched={html.escape(', '.join(decision.matched_rules) or 'default')}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tab_postmortem:
        st.markdown('<p class="bb-section-kicker">Evidence-Backed Report</p>', unsafe_allow_html=True)
        postmortem = generate_postmortem(replay)
        st.download_button(
            "Download postmortem.md",
            postmortem.markdown,
            file_name=f"{replay.incident_id}_postmortem.md",
            mime="text/markdown",
            use_container_width=True,
        )
        st.markdown(postmortem.markdown)


# ═══════════════════════════════════════════
# CTA
# ═══════════════════════════════════════════
st.markdown('<hr class="bb-divider"/>', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="bb-cta">
      <h2 class="bb-cta-title">The flight recorder for<br/>agentic operations.</h2>
      <p class="bb-cta-sub">
        BlackBoxOps captures every decision, every query, and every policy check &mdash; so your AI ops
        leave proof, not vibes.
      </p>
      <a class="bb-btn-primary" href="https://github.com/olamide203" target="_blank" style="text-decoration:none;">
        View on GitHub
      </a>
    </div>
    """,
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════
st.markdown(
    """
    <footer class="bb-footer">
      <span style="font-family:var(--font-sans);font-size:14px;color:var(--bb-ink-muted);">BlackBoxOps &mdash; Splunk Agentic Ops Hackathon</span>
      <ul class="bb-footer-links">
        <li><a href="https://splunk.com" target="_blank">Splunk</a></li>
        <li><a href="https://github.com/olamide203" target="_blank">GitHub</a></li>
      </ul>
    </footer>
    """,
    unsafe_allow_html=True,
)
