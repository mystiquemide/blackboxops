from __future__ import annotations

import html

import streamlit as st

from app.brand import build_brand_css, policy_label, risk_label
from app.demo_agent import run_demo_incident
from app.postmortem import generate_postmortem

st.set_page_config(page_title="BlackBoxOps", layout="wide", page_icon="▰")
st.markdown(build_brand_css(), unsafe_allow_html=True)

if "replay" not in st.session_state:
    st.session_state.replay = run_demo_incident()

replay = st.session_state.replay

st.markdown(
    """
    <section class="bb-hero">
      <div class="bb-logo"><span class="bb-recorder"></span><span>BlackBox<span style="color:#65A637">Ops</span></span></div>
      <div class="bb-kicker">Splunk-native safety layer</div>
      <div class="bb-title">The flight recorder for agentic operations.</div>
      <div class="bb-subtitle">
        Record every AI decision, Splunk query, evidence reference, policy check, and remediation attempt —
        then replay incidents with proof instead of vibes.
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

command_col, timeline_col, evidence_col = st.columns([0.9, 1.45, 1.1], gap="large")

with command_col:
    st.markdown("<div class='bb-kicker'>Incident Command Rail</div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="bb-card">
          <div class="bb-card-title">Checkout prompt-injection incident</div>
          <div class="bb-meta">incident_id={html.escape(replay.incident_id)}</div>
          <p style="color:#94A3B8;margin-top:10px;">
            A deterministic agentic ops incident where malicious log content tries to hijack the AI agent.
          </p>
          <span class="bb-chip bb-risk-medium">● MCP-ready</span>
          <span class="bb-chip bb-risk-low">● Mock mode safe</span>
          <span class="bb-chip bb-risk-critical">● Injection demo</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Run Agentic Incident Demo", type="primary", use_container_width=True):
        st.session_state.replay = run_demo_incident()
        replay = st.session_state.replay
        st.toast("Replay recorded. Evidence and policy decisions are ready.", icon="▰")

    metric_a, metric_b = st.columns(2)
    metric_a.metric("Events", len(replay.events))
    metric_b.metric("Evidence", len(replay.evidence))
    st.metric("Policy decisions", len(replay.policy_decisions))

    st.markdown(
        """
        <div class="bb-card">
          <div class="bb-card-title">BB-0 says</div>
          <div style="color:#94A3B8;">Evidence required. Policy checked. Replay ready.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with timeline_col:
    st.markdown("<div class='bb-kicker'>Replay Timeline</div>", unsafe_allow_html=True)
    for index, event in enumerate(replay.events, start=1):
        risk = risk_label(event.risk_score)
        event_type = html.escape(event.event_type.replace("_", " ").title())
        summary = html.escape(event.summary)
        actor = html.escape(event.actor)
        evidence_refs = ", ".join(e.evidence_id for e in event.evidence_refs) or "none"
        st.markdown(
            f"""
            <div class="bb-card">
              <span class="bb-chip bb-risk-{risk['level']}">{risk['icon']} {risk['text']}</span>
              <span class="bb-chip">#{index:02d} {event_type}</span>
              <div class="bb-card-title">{summary}</div>
              <div class="bb-meta">actor={actor} · event_id={html.escape(event.event_id)}</div>
              <div class="bb-meta">evidence_refs={html.escape(evidence_refs)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if event.policy_decision:
            st.code(event.policy_decision.model_dump_json(indent=2), language="json")

with evidence_col:
    tab_evidence, tab_policy, tab_postmortem = st.tabs(["Evidence", "Policy", "Postmortem"])

    with tab_evidence:
        st.markdown("<div class='bb-kicker'>Splunk Evidence Plane</div>", unsafe_allow_html=True)
        for evidence in replay.evidence:
            flags = ", ".join(evidence.risk_flags) or "none"
            message = evidence.sample_event.get("message", "")
            st.markdown(
                f"""
                <div class="bb-card bb-evidence">
                  <div class="bb-card-title">{html.escape(evidence.evidence_id)}</div>
                  <div class="bb-meta">confidence={evidence.confidence:.2f} · source={html.escape(evidence.source)}</div>
                  <span class="bb-chip bb-risk-medium">Evidence</span>
                  <span class="bb-chip">flags={html.escape(flags)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.code(evidence.query, language="sql")
            st.code(message, language="text")

    with tab_policy:
        st.markdown("<div class='bb-kicker'>Safety Gateway</div>", unsafe_allow_html=True)
        for decision in replay.policy_decisions:
            label = policy_label(decision.status)
            st.markdown(
                f"""
                <div class="bb-card bb-policy-{label['level']}">
                  <span class="bb-chip bb-risk-{('critical' if decision.status == 'block' else 'high' if decision.status == 'approval_required' else 'low')}">{label['icon']} {label['text']}</span>
                  <div class="bb-card-title">{html.escape(decision.policy_id)}</div>
                  <div style="color:#94A3B8;">{html.escape(decision.reason)}</div>
                  <div class="bb-meta">risk={html.escape(decision.risk_level)} · matched={html.escape(', '.join(decision.matched_rules) or 'default')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tab_postmortem:
        st.markdown("<div class='bb-kicker'>Evidence-backed report</div>", unsafe_allow_html=True)
        postmortem = generate_postmortem(replay)
        st.download_button(
            "Download postmortem.md",
            postmortem.markdown,
            file_name=f"{replay.incident_id}_postmortem.md",
            mime="text/markdown",
            use_container_width=True,
        )
        st.markdown(postmortem.markdown)
