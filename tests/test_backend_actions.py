from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_remediation_proposal_is_recorded_as_pending_approval():
    replay = client.post("/api/demo/run").json()
    evidence_ids = [item["evidence_id"] for item in replay["evidence"]]

    response = client.post(
        "/api/actions/propose",
        json={
            "incident_id": replay["incident_id"],
            "action_type": "restart_service",
            "target": "checkout-api",
            "evidence_refs": evidence_ids,
            "requested_by": "sre-lead@example.com",
            "reason": "Restart checkout-api after prompt injection containment.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["action_id"].startswith("act_")
    assert body["incident_id"] == replay["incident_id"]
    assert body["status"] == "pending_approval"
    assert body["decision"]["status"] == "approval_required"
    assert body["evidence_refs"] == evidence_ids

    replay_after = client.get(f"/api/incidents/{replay['incident_id']}/replay").json()
    proposal_events = [event for event in replay_after["events"] if event["event_type"] == "approval"]
    assert proposal_events
    assert proposal_events[-1]["policy_decision"]["status"] == "approval_required"
    assert proposal_events[-1]["payload"]["action_id"] == body["action_id"]


def test_dashboard_can_propose_remediation_before_replay_run():
    response = client.post(
        "/api/actions/propose",
        json={
            "incident_id": "inc_prompt_injection_checkout",
            "action_type": "restart_service",
            "target": "checkout-api",
            "evidence_refs": ["EVD-100", "EVD-101"],
            "requested_by": "judge@blackboxops.demo",
            "reason": "Restart checkout-api after evidence review from dashboard.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["incident_id"] == "inc_prompt_injection_checkout"
    assert body["status"] == "pending_approval"


def test_remediation_proposal_without_evidence_is_blocked_and_recorded():
    replay = client.post("/api/demo/run").json()

    response = client.post(
        "/api/actions/propose",
        json={
            "incident_id": replay["incident_id"],
            "action_type": "restart_service",
            "target": "checkout-api",
            "evidence_refs": [],
            "requested_by": "sre-lead@example.com",
            "reason": "Try a restart without evidence.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "blocked"
    assert body["decision"]["status"] == "block"
    assert body["decision"]["policy_id"] == "action-requires-evidence"

    replay_after = client.get(f"/api/incidents/{replay['incident_id']}/replay").json()
    blocked_events = [event for event in replay_after["events"] if event["event_type"] == "approval"]
    assert blocked_events
    assert blocked_events[-1]["summary"].startswith("Remediation proposal blocked")


def _pending_action() -> tuple[dict, dict]:
    replay = client.post("/api/demo/run").json()
    evidence_ids = [item["evidence_id"] for item in replay["evidence"]]
    proposal = client.post(
        "/api/actions/propose",
        json={
            "incident_id": replay["incident_id"],
            "action_type": "restart_service",
            "target": "checkout-api",
            "evidence_refs": evidence_ids,
            "requested_by": "sre-lead@example.com",
            "reason": "Restart checkout-api after prompt injection containment.",
        },
    ).json()
    return replay, proposal


def test_pending_remediation_can_be_approved_and_records_signed_event():
    replay, proposal = _pending_action()

    response = client.post(
        f"/api/actions/{proposal['action_id']}/approve",
        json={"reviewer": "sre-lead@example.com", "note": "Approved after evidence review."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "approved"
    assert body["reviewer"] == "sre-lead@example.com"
    assert body["action_id"] == proposal["action_id"]

    actions = client.get(f"/api/actions?incident_id={replay['incident_id']}").json()
    assert actions[-1]["status"] == "approved"
    assert actions[-1]["approved_by"] == "sre-lead@example.com"

    replay_after = client.get(f"/api/incidents/{replay['incident_id']}/replay").json()
    approval_events = [event for event in replay_after["events"] if event["event_type"] == "approval"]
    assert approval_events[-1]["summary"] == "Human approved pending remediation; execution handed to configured connector."
    assert approval_events[-1]["payload"]["decision"] == "approved"
    assert approval_events[-1]["payload"]["reviewer"] == "sre-lead@example.com"
    assert approval_events[-1]["payload"]["execution_mode"] == "connector_pending"


def test_pending_remediation_can_be_rejected_and_records_signed_event():
    replay, proposal = _pending_action()

    response = client.post(
        f"/api/actions/{proposal['action_id']}/reject",
        json={"reviewer": "sre-lead@example.com", "note": "Reject until deploy rollback completes."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["reviewer"] == "sre-lead@example.com"

    actions = client.get(f"/api/actions?incident_id={replay['incident_id']}").json()
    assert actions[-1]["status"] == "rejected"
    assert actions[-1]["rejected_by"] == "sre-lead@example.com"

    replay_after = client.get(f"/api/incidents/{replay['incident_id']}/replay").json()
    approval_events = [event for event in replay_after["events"] if event["event_type"] == "approval"]
    assert approval_events[-1]["summary"] == "Human rejected pending remediation; no action executed."
    assert approval_events[-1]["payload"]["decision"] == "rejected"


def test_non_pending_action_cannot_be_approved():
    replay = client.post("/api/demo/run").json()
    blocked = client.post(
        "/api/actions/propose",
        json={
            "incident_id": replay["incident_id"],
            "action_type": "restart_service",
            "target": "checkout-api",
            "evidence_refs": [],
            "requested_by": "sre-lead@example.com",
            "reason": "Try a restart without evidence.",
        },
    ).json()

    response = client.post(
        f"/api/actions/{blocked['action_id']}/approve",
        json={"reviewer": "sre-lead@example.com", "note": "Should not approve blocked proposal."},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Only pending approval actions can be approved or rejected"
