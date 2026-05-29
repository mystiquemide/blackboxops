from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from app.brand import build_brand_css
from app.demo_agent import run_demo_incident
from app.main import app
from app.postmortem import generate_postmortem

REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    ".env.example",
    "DESIGN.md",
    "architecture_diagram.md",
    "docs/DEVPOST_SUBMISSION.md",
    "docs/DEMO_SCRIPT.md",
    "docs/SECURITY.md",
    "policies/default.yaml",
    "data/sample_incidents.jsonl",
    "data/sample_splunk_events.jsonl",
]


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        raise SystemExit(f"Missing required files: {missing}")

    replay = run_demo_incident(event_store_path=ROOT / "data" / "blackbox_events.jsonl")
    if not replay.events or not replay.evidence or not replay.policy_decisions:
        raise SystemExit("Demo replay did not produce events, evidence, and policy decisions")

    postmortem = generate_postmortem(replay).markdown
    if "Prompt injection" not in postmortem and "prompt injection" not in postmortem:
        raise SystemExit("Postmortem does not mention prompt injection")

    css = build_brand_css()
    if ".bb-hero" not in css or "#070A0F" not in css:
        raise SystemExit("Brand CSS is incomplete")

    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.get("/incidents").status_code == 200
    assert client.post("/demo/run").status_code == 200
    assert client.get("/incidents/inc_prompt_injection_checkout/postmortem").status_code == 200

    print("BlackBoxOps demo readiness checks passed.")


if __name__ == "__main__":
    main()
