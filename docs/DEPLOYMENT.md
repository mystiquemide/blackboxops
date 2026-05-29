# BlackBoxOps Deployment Notes

## Recommended hackathon deployment

Use Streamlit Community Cloud or Railway for the public demo URL. The live demo should run in mock mode so judges are not blocked by Splunk credentials.

## Environment

Set:

```bash
USE_MOCK_SPLUNK=true
BLACKBOXOPS_EVENT_STORE=data/blackbox_events.jsonl
BLACKBOXOPS_POLICY_FILE=policies/default.yaml
```

Optional real Splunk integration keys are documented in `.env.example`; do not set them for the default public demo unless a real Splunk instance is ready.

## Streamlit Community Cloud

1. Push this repo to GitHub.
2. Create a new Streamlit app.
3. Main file path: `app/ui.py`.
4. Python version: 3.11.
5. Add the environment values above in app secrets/settings.
6. Deploy.

## Railway / Render style deployment

Use the included `Procfile`:

```bash
web: streamlit run app/ui.py --server.address=0.0.0.0 --server.port=${PORT:-8501}
```

## Docker

```bash
docker build -t blackboxops .
docker run --rm -p 8501:8501 blackboxops
```

Or:

```bash
docker compose up --build
```

## Pre-submission checks

Run:

```bash
python -m pytest tests/ -q
python -m compileall app scripts tests -q
python scripts/run_demo_checks.py
npx -y @google/design.md lint DESIGN.md
```

## Public demo video path

Record the Streamlit UI path:
1. Hero + incident command rail.
2. Click `Run Agentic Incident Demo`.
3. Show prompt-injection evidence.
4. Show blocked unsafe SPL/prompt-injection policy.
5. Show approval-required remediation.
6. Download/show postmortem.
