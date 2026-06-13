"""Index demo events into Splunk Cloud via HEC (HTTP Event Collector).

Set SPLUNK_HEC_TOKEN and SPLUNK_HEC_URL in .env or as environment variables
before running. These are required, there is no hardcoded fallback.

Example:
  SPLUNK_HEC_TOKEN=your-hec-token
  SPLUNK_HEC_URL=https://inputs.your-host.splunkcloud.com:8088/services/collector/event
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error
import ssl
from datetime import datetime, timezone
from pathlib import Path

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except ImportError:
    pass

HEC_TOKEN = os.environ.get("SPLUNK_HEC_TOKEN", "")
HEC_URL = os.environ.get("SPLUNK_HEC_URL", "")

if not HEC_TOKEN:
    sys.exit("Set SPLUNK_HEC_TOKEN in .env or as an environment variable before running this script.")
if not HEC_URL:
    sys.exit("Set SPLUNK_HEC_URL in .env or as an environment variable before running this script.")

INDEX = "main"
SOURCETYPE = "app_logs"

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "sample_splunk_events.jsonl"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def post_hec(event_body: dict, epoch: float) -> tuple[int, str]:
    payload = json.dumps({
        "time": epoch,
        "index": INDEX,
        "sourcetype": SOURCETYPE,
        "event": event_body,
    }).encode()
    req = urllib.request.Request(HEC_URL, data=payload, method="POST", headers={
        "Authorization": f"Splunk {HEC_TOKEN}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()


def main() -> None:
    raw_events = [json.loads(ln) for ln in DATA_FILE.read_text(encoding="utf-8").splitlines() if ln.strip()]
    now = datetime.now(timezone.utc)
    print(f"Indexing {len(raw_events)} events into Splunk Cloud index={INDEX} sourcetype={SOURCETYPE}")

    ok = 0
    for i, event in enumerate(raw_events):
        # stagger timestamps so events fall within the -15m search window
        epoch = now.timestamp() - (len(raw_events) - i) * 60
        status, resp = post_hec(event, epoch)
        if status in (200, 201):
            ok += 1
            print(f"  OK  {event.get('event_id', '?')} - {event.get('message', '')[:60]}")
        else:
            print(f"  ERR {event.get('event_id', '?')} - HTTP {status}: {resp[:120]}")

    print(f"\nDone: {ok}/{len(raw_events)} events indexed.")
    if ok < len(raw_events):
        print("Some events failed. Check HEC token and URL.")
        sys.exit(1)


if __name__ == "__main__":
    main()
