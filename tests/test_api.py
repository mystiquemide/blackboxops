from fastapi.testclient import TestClient

from app.main import app


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
    assert body["incident_id"] == "inc_prompt_injection_checkout"
    assert body["events"]
    assert body["policy_decisions"]


def test_incidents_only_lists_supported_replay():
    client = TestClient(app)

    response = client.get("/incidents")

    assert response.status_code == 200
    incident_ids = [incident["incident_id"] for incident in response.json()]
    assert incident_ids == ["inc_prompt_injection_checkout"]


def test_unknown_incident_replay_returns_404():
    client = TestClient(app)

    response = client.get("/incidents/inc_safe_remediation_cache/replay")

    assert response.status_code == 404
