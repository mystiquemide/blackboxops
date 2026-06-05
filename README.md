# BlackBoxOps

Splunk-native flight recorder and safety layer for agentic operations.

BlackBoxOps records every AI ops decision, Splunk-style query, evidence reference, policy check, approval gate, and remediation proposal. It then replays the incident as a forensic timeline and generates an evidence-backed postmortem.

Important: this project does not claim to be the first AI-agent flight recorder. The hackathon wedge is Splunk-native operational evidence + MCP/SPL safety gateway + policy-gated remediation + replay UX.

## Hackathon Positioning

- Hackathon: Splunk Agentic Ops Hackathon
- Main track: Platform & Developer Experience
- Bonus target: Best Use of Splunk MCP Server
- Tagline: The flight recorder for agentic operations.

## What the demo shows

1. An AI ops agent investigates a checkout latency incident.
2. The agent queries Splunk-style logs through BlackBoxOps.
3. The retrieved evidence includes malicious prompt-injection text embedded in logs.
4. BlackBoxOps detects the injection and blocks it from steering the agent.
5. The agent attempts a risky broad/destructive SPL query; BlackBoxOps blocks it.
6. The agent proposes a disruptive remediation; BlackBoxOps requires human approval.
7. The UI replays the whole incident with evidence cards and policy decisions.
8. A postmortem is generated with evidence-bound claims.

## Quickstart

```bash
cd C:/Users/Prince/Projects/hackathons/blackboxops
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
npm install
python -m pytest tests/ -q
python scripts/run_demo.py
```

Run the React demo locally:

```bash
# Terminal 1 — API
USE_MOCK_SPLUNK=true USE_MOCK_AUTH=true uvicorn app.main:app --reload --port 8000

# Terminal 2 — React app
npm run dev
```

Open the Vite URL, click `Enter judge demo`, then open the replay dashboard.

Build and serve the production React UI from FastAPI:

```bash
npm run build
USE_MOCK_SPLUNK=true USE_MOCK_AUTH=true uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then open `http://127.0.0.1:8000`.

Streamlit fallback UI:

```bash
streamlit run app/ui.py
```

## Mock-first reliability

The demo works offline with:

```bash
export USE_MOCK_SPLUNK=true
```

Or run one command with mock mode explicitly:

```bash
USE_MOCK_SPLUNK=true python scripts/run_demo.py
```

Sample data lives in:

- data/sample_incidents.jsonl
- data/sample_splunk_events.jsonl
- policies/default.yaml

## Splunk integration path

BlackBoxOps is structured around an adapter boundary:

- app/splunk_adapter.py
- mock_search(...) for deterministic judging demo
- real_search_stub(...) for Splunk Search/MCP integration
- send_hec_event(...) hook for Splunk HEC ingestion

For the hackathon MVP, the live demo uses deterministic mock mode so judges can run it without a Splunk account. The MCP/Search/HEC boundary is isolated in `app/splunk_adapter.py` so a real Splunk MCP Server tool call can replace `mock_search(...)` without changing the recorder, policy engine, API, or UI.

## Architecture

See:

- architecture_diagram.md
- docs/ARCHITECTURE.md

## Test suite

```bash
python -m pytest tests/ -q
python -m compileall app scripts tests -q
python scripts/run_demo_checks.py
npm run lint
npm run build
```

Current coverage focus:

- policy engine allow/block/approval behavior
- prompt-injection detection
- deterministic demo flow
- basic API health and demo endpoint

## Deployment

See `docs/DEPLOYMENT.md`.

React-first Docker deployment:

```bash
docker build -t blackboxops .
docker run --rm -p 8000:8000 blackboxops
```

Docker Compose:

```bash
docker compose up --build
```

The Streamlit UI remains available as a local fallback with `streamlit run app/ui.py`.

## React demo UI

For development, run FastAPI and the Vite frontend in separate terminals:

```bash
USE_MOCK_SPLUNK=true USE_MOCK_AUTH=*** uvicorn app.main:app --reload --port 8000
npm install
npm run dev
```

Vite proxies `/api` requests to `http://127.0.0.1:8000` by default. Set
`BLACKBOXOPS_API_URL` before `npm run dev` when the API uses another port.

For deployment, run `npm run build`; FastAPI serves the generated `dist/` app at `/` while keeping `/api/*` routes available.

## Project structure

```text
app/
  main.py              FastAPI routes
  ui.py                Streamlit replay UI
  models.py            Pydantic event/evidence/policy models
  policy_engine.py     YAML-driven safety rules
  splunk_adapter.py    Mock-first Splunk adapter + real hooks
  recorder.py          JSONL event recorder
  demo_agent.py        Deterministic demo scenario
  postmortem.py        Evidence-backed postmortem generator
src/                   React + TypeScript demo UI
policies/default.yaml  Policy rules
data/*.jsonl           Demo incidents and mock Splunk events
tests/                 Pytest suite
docs/                  PRD, architecture, design, analytics, submission docs
```

## License

MIT
