from fastapi.testclient import TestClient

from app.main import app

CHECKOUT_ID = "inc_prompt_injection_checkout"
CACHE_ID = "inc_safe_remediation_cache"


def test_health_endpoint():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_demo_run_endpoint_returns_replay():
    client = TestClient(app)

    response = client.post("/demo/run")

    assert response.status_code == 200
    body = response.json()
    assert body["incident_id"] == CHECKOUT_ID
    assert body["events"]
    assert body["policy_decisions"]


def test_incidents_lists_both_supported_scenarios():
    client = TestClient(app)

    response = client.get("/api/incidents")

    assert response.status_code == 200
    incident_ids = [incident["incident_id"] for incident in response.json()]
    assert CHECKOUT_ID in incident_ids
    assert CACHE_ID in incident_ids


def test_unknown_incident_replay_returns_404():
    client = TestClient(app)

    response = client.get("/incidents/inc_does_not_exist/replay")

    assert response.status_code == 404


def test_cache_incident_replay_returns_200():
    client = TestClient(app)

    response = client.get(f"/incidents/{CACHE_ID}/replay")

    assert response.status_code == 200
    body = response.json()
    assert body["incident_id"] == CACHE_ID
    assert body["events"]


def test_api_prefixed_demo_and_policy_catalog_are_available():
    client = TestClient(app)

    replay_response = client.post("/api/demo/run")
    policies_response = client.get("/api/policies")

    assert replay_response.status_code == 200
    assert replay_response.json()["evidence"]
    assert policies_response.status_code == 200
    assert any(policy["policy_id"] == "POL-INJ-01" for policy in policies_response.json())


def test_cache_demo_run_endpoint_returns_replay():
    client = TestClient(app)

    response = client.post("/api/demo/run-cache")

    assert response.status_code == 200
    body = response.json()
    assert body["incident_id"] == CACHE_ID
    assert body["events"]


def test_splunk_dashboard_export_returns_xml():
    client = TestClient(app)

    # ensure a replay exists first
    client.post("/api/demo/run")
    response = client.get(f"/api/incidents/{CHECKOUT_ID}/splunk-dashboard")

    assert response.status_code == 200
    assert "xml" in response.headers["content-type"]
    assert CHECKOUT_ID in response.text
    assert "<dashboard" in response.text
