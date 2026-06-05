# BlackBoxOps Deployment Notes

## Recommended hackathon deployment

Use the React/Vite UI served by FastAPI for the public demo URL. Build the frontend once, then run `app.main:app`; FastAPI keeps `/api/*` routes available and serves the compiled React app from `dist/` at `/`.

The public demo should run in mock mode so judges are not blocked by Splunk or Google credentials.

## Environment

Set:

```bash
USE_MOCK_SPLUNK=true
USE_MOCK_AUTH=true
BLACKBOXOPS_EVENT_STORE=data/blackbox_events.jsonl
BLACKBOXOPS_POLICY_FILE=policies/default.yaml
BLACKBOXOPS_AUTH_STORE=data/auth_users.jsonl
```

Optional production OAuth values:

```bash
FRONTEND_URL=https://<your-demo-host>
GOOGLE_REDIRECT_URI=https://<your-demo-host>/api/auth/google/callback
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

Optional real Splunk integration keys are documented in `.env.example`; do not set them for the default public demo unless a real Splunk instance is ready.

## Local production smoke run

```bash
npm install
npm run build
USE_MOCK_SPLUNK=true USE_MOCK_AUTH=true uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open `http://127.0.0.1:8000`, click `Enter judge demo`, then run the replay dashboard.

## Railway / Render style deployment

Use the included `Procfile`:

```bash
web: uvicorn app.main:app --host 0.0.0.0 --port=${PORT:-8000}
```

Build command:

```bash
pip install -r requirements.txt && npm ci && npm run build
```

Start command comes from the Procfile.

## Docker

```bash
docker build -t blackboxops .
docker run --rm -p 8000:8000 blackboxops
```

Or:

```bash
docker compose up --build
```

## Streamlit fallback

The original Streamlit UI remains available for local fallback demos:

```bash
USE_MOCK_SPLUNK=true streamlit run app/ui.py
```

Do not use Streamlit as the preferred public URL if the React/FastAPI deployment is stable.

## Pre-submission checks

Run:

```bash
python -m pytest tests/ -q
python -m compileall app scripts tests -q
python scripts/run_demo_checks.py
npm run lint
npm run build
npx -y @google/design.md lint DESIGN.md
```

## Public demo video path

Record the React UI path:
1. Landing page: position as Splunk-native evidence and safety layer, not a chatbot.
2. Click `Enter judge demo`.
3. Open the replay dashboard and click `Run incident replay`.
4. Show Splunk evidence cards with evidence_refs.
5. Show prompt-injection block and unsafe action policy decision.
6. Show approval-required remediation gate.
7. Export/show the evidence-backed postmortem.
