from app.models import AgentEvent, EvidenceRef


def test_agent_event_requires_evidence_for_evidence_claims():
    evidence = EvidenceRef(
        evidence_id="ev_1",
        query='index=main sourcetype=app_logs error | head 5',
        time_range="-15m to now",
        source="mock_splunk",
        sample_event={"message": "checkout errors spiking"},
        confidence=0.92,
        risk_flags=["service-degradation"],
    )

    event = AgentEvent(
        incident_id="inc_1",
        session_id="sess_1",
        event_type="evidence",
        actor="demo_agent",
        risk_score=0.4,
        summary="Agent found checkout error spike",
        payload={"claim": "checkout errors are rising"},
        evidence_refs=[evidence],
    )

    assert event.event_id.startswith("evt_")
    assert event.evidence_refs[0].evidence_id == "ev_1"
