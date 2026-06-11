# Deployment — BlackBoxOps

BlackBoxOps serves the React frontend as a static build from FastAPI. The same process handles `/api/*` routes and serves `dist/` at `/`.

## Environment Variables

Required for offline/mock mode (no external services needed):

```bash
USE_MOCK_SPLUNK=true
USE_MOCK_AUTH=true
```

Required for production with real auth and Splunk:

```bash
USE_MOCK_SPLUNK=false
USE_MOCK_AUTH=false
FRONTEND_URL=https://your-domain.com
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=https://your-domain.com/api/auth/google/callback
SESSION_SECRET=<random 64-char hex>
```

Splunk MCP integration:

```bash
USE_SPLUNK_MCP=true

# Splunk Cloud
SPLUNK_MCP_URL=https://your-host.splunkcloud.com:443/en-US/splunkd/__raw/services/mcp
SPLUNK_MCP_TOKEN=<MCP encrypted token from the Splunk MCP Server app>
SPLUNK_MCP_VERIFY_TLS=true

# HEC ingestion (Splunk Cloud uses port 8088 on inputs. subdomain)
SPLUNK_HEC_TOKEN=<HEC token>
SPLUNK_HEC_URL=https://inputs.your-host.splunkcloud.com:8088/services/collector/event
```

See `.env.example` for the full list.

## Local Build

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
npm install
npm run build
USE_MOCK_SPLUNK=true USE_MOCK_AUTH=true uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open `http://127.0.0.1:8000`.

## Railway / Render

Build command:
```bash
pip install -r requirements.txt && npm ci && npm run build
```

Start command (or use the included `Procfile`):
```bash
uvicorn app.main:app --host 0.0.0.0 --port=${PORT:-8000}
```

Set `USE_MOCK_SPLUNK=true` and `USE_MOCK_AUTH=true` in the service environment for the public instance.

## Docker

```bash
docker build -t blackboxops .
docker run --rm -p 8000:8000 \
  -e USE_MOCK_SPLUNK=true \
  -e USE_MOCK_AUTH=true \
  blackboxops
```

Or with Compose:

```bash
docker compose up --build
```

## Verification

```bash
python -m pytest tests/ -q
python -m compileall app scripts tests -q
npm run lint
npm run build
curl http://localhost:8000/api/health
```

## Streamlit Fallback

The original Streamlit UI is available for local inspection:

```bash
USE_MOCK_SPLUNK=true streamlit run app/ui.py
```

Not recommended as the primary public URL when the React/FastAPI deployment is stable.
