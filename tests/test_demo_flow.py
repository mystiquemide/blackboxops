from app.demo_agent import run_demo_incident
from app.postmortem import generate_postmortem


def test_demo_flow_records_evidence_policy_and_postmortem(tmp_path):
    replay = run_demo_incident(event_store_path=tmp_path / "events.jsonl", use_mock=True)

    assert replay.incident_id == "inc_prompt_injection_checkout"
    assert len(replay.events) >= 7
    assert replay.evidence
    assert any(decision.status in {"block", "approval_required"} for decision in replay.policy_decisions)
    assert any("prompt injection" in event.summary.lower() for event in replay.events)

    postmortem = generate_postmortem(replay)

    assert "# BlackBoxOps Postmortem" in postmortem.markdown
    assert "Evidence" in postmortem.markdown
    assert "Policy Decisions" in postmortem.markdown
    assert replay.incident_id in postmortem.markdown
