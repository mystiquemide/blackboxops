FROM python:3.11-slim AS backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    USE_MOCK_SPLUNK=true \
    USE_MOCK_AUTH=true \
    BLACKBOXOPS_EVENT_STORE=data/blackbox_events.jsonl \
    BLACKBOXOPS_POLICY_FILE=policies/default.yaml \
    BLACKBOXOPS_AUTH_STORE=data/auth_users.jsonl

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl nodejs npm \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt package.json package-lock.json ./
RUN pip install --no-cache-dir -r requirements.txt \
    && npm ci

COPY . .
RUN npm run build

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
