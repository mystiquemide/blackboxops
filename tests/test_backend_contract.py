from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

CHECKOUT_ID = "inc_prompt_injection_checkout"
CACHE_ID = "inc_safe_remediation_cache"


def test_health_exposes_mock_and_splunk_readiness():
    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "blackboxops"
    assert "mock_splunk" in body
    assert "splunk_configured" in body
    assert "llm_configured" in body
    assert body["policy_mode"] == "fail_closed"


def test_incident_summary_contains_frontend_contract_fields():
    response = client.get("/api/incidents")

    assert response.status_code == 200
    incidents = response.json()
    assert incidents
    # checkout incident is always first (it's first in sample_incidents.jsonl)
    checkout = next(i for i in incidents if i["incident_id"] == CHECKOUT_ID)
    assert checkout["source"] == "mock_splunk"
    assert checkout["actor"] == "bb-agent/checkout-v2"
    assert checkout["evidence_refs"] == 3
    assert checkout["policy_id"] == "POL-INJ-01"
    assert checkout["policy_outcome"] == "BLOCKED"
    assert checkout["updated_at"].endswith("Z")


def test_cache_incident_summary_present():
    response = client.get("/api/incidents")

    assert response.status_code == 200
    incidents = response.json()
    cache = next((i for i in incidents if i["incident_id"] == CACHE_ID), None)
    assert cache is not None
    assert cache["policy_outcome"] == "ALLOWED"


def test_replay_contract_has_stable_fancy_ids_and_policy_metadata():
    response = client.post("/api/demo/run")

    assert response.status_code == 200
    replay = response.json()
    assert replay["incident_id"] == CHECKOUT_ID
    assert replay["session_id"].startswith("sess_")
    assert replay["started_at"].endswith("Z")
    assert replay["outcome"] == "blocked"
    assert replay["approval_required"] is True
    assert replay["evidence"]
    # At minimum the destructive SPL block fires regardless of evidence source
    assert any(d["status"] == "block" for d in replay["policy_decisions"])
    assert all(event["display_id"].startswith("EVT-") for event in replay["events"])
    # llm_analysis field is present (may be None or a string)
    assert "llm_analysis" in replay


def test_cache_replay_has_no_blocks():
    response = client.post("/api/demo/run-cache")

    assert response.status_code == 200
    replay = response.json()
    assert replay["incident_id"] == CACHE_ID
    assert replay["outcome"] in {"recorded", "blocked"}
    # cache incident should not block (no prompt injection)
    assert not any(d["status"] == "block" for d in replay["policy_decisions"])


def test_policy_catalog_uses_demo_visible_policy_ids_and_outcomes():
    response = client.get("/api/policies")

    assert response.status_code == 200
    policies = response.json()
    policy_ids = {policy["policy_id"] for policy in policies}
    assert {"POL-INJ-01", "POL-SPL-01", "POL-APPR-01", "POL-DIAG-01"}.issubset(policy_ids)
    injection = next(policy for policy in policies if policy["policy_id"] == "POL-INJ-01")
    assert injection["status"] == "block"
    assert injection["risk_level"] == "critical"
    assert injection["splunk_source"] == "mock_splunk"
    assert injection["enabled"] is True
