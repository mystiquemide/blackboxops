"""Seed Splunk with synthetic checkout/cache events so live MCP queries return real data."""
from __future__ import annotations

import os
import sys
import time
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env", override=True)

warnings.filterwarnings("ignore")
import requests  # noqa: E402

BASE = "https://localhost:8089"
TOKEN = os.getenv("SPLUNK_MCP_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

EVENTS = [
    {
        "search": (
            '| makeresults count=1'
            ' | eval service="checkout", severity="error", host="checkout-api-01",'
            ' message="checkout timeout rate jumped to 18 percent after deploy sha abc123",'
            ' sourcetype="app_logs", index="main"'
            ' | collect index=main sourcetype=app_logs'
        ),
        "label": "checkout error event",
    },
    {
        "search": (
            '| makeresults count=1'
            ' | eval service="checkout", severity="warn", host="checkout-api-02",'
            ' message="checkout p99 latency 4200ms exceeds SLO threshold of 2000ms",'
            ' sourcetype="app_logs", index="main"'
            ' | collect index=main sourcetype=app_logs'
        ),
        "label": "checkout latency warn",
    },
    {
        "search": (
            '| makeresults count=1'
            ' | eval service="checkout", severity="error", host="checkout-api-01",'
            ' message="payment gateway connection refused after 3 retries",'
            ' sourcetype="app_logs", index="main"'
            ' | collect index=main sourcetype=app_logs'
        ),
        "label": "payment gateway error",
    },
    {
        "search": (
            '| makeresults count=1'
            ' | eval service="cache", severity="warn", host="redis-01",'
            ' message="cache miss rate 67 percent on checkout session keys",'
            ' sourcetype="app_logs", index="main"'
            ' | collect index=main sourcetype=app_logs'
        ),
        "label": "cache miss warn",
    },
]


def run_search(spl: str, label: str) -> None:
    resp = requests.post(
        f"{BASE}/services/search/jobs",
        headers=HEADERS,
        data={"search": spl, "output_mode": "json", "exec_mode": "normal"},
        verify=False,
        timeout=30,
    )
    if not resp.ok:
        print(f"  FAIL {label}: {resp.status_code} {resp.text[:200]}")
        return
    sid = resp.json()["sid"]
    for _ in range(30):
        poll = requests.get(
            f"{BASE}/services/search/jobs/{sid}",
            headers=HEADERS,
            params={"output_mode": "json"},
            verify=False,
            timeout=10,
        )
        content = poll.json()["entry"][0]["content"]
        if content["isDone"]:
            print(f"  OK   {label}")
            return
        time.sleep(1)
    print(f"  TIMEOUT {label}")


if __name__ == "__main__":
    if not TOKEN:
        print("SPLUNK_MCP_TOKEN not set in .env")
        sys.exit(1)
    print("Seeding Splunk with synthetic checkout events...")
    for event in EVENTS:
        run_search(event["search"], event["label"])
    print("\nDone. Run the demo to verify live MCP results:")
    print("  python scripts/run_demo.py")
