"""End-to-end test: real Splunk MCP -> policy engine -> injection detection.

Set the following environment variables (or add them to .env) before running:

  USE_SPLUNK_MCP=true
  USE_MOCK_SPLUNK=false
  SPLUNK_MCP_URL=https://your-host.splunkcloud.com:443/en-US/splunkd/__raw/services/mcp
  SPLUNK_MCP_TOKEN=<your MCP token>
  SPLUNK_MCP_VERIFY_TLS=true
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Load .env if present so you can run this without exporting vars manually
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except ImportError:
    pass

# Validate required vars
for var in ("SPLUNK_MCP_URL", "SPLUNK_MCP_TOKEN"):
    if not os.environ.get(var):
        sys.exit(f"Missing required env var: {var}. Set it in .env or export it.")

os.environ.setdefault("USE_SPLUNK_MCP", "true")
os.environ.setdefault("USE_MOCK_SPLUNK", "false")
os.environ.setdefault("SPLUNK_MCP_VERIFY_TLS", "true")

from app.splunk_adapter import SplunkAdapter
from app.policy_engine import PolicyEngine

print("=" * 60)
print("BlackBoxOps - Real Splunk MCP end-to-end test")
print("=" * 60)

adapter = SplunkAdapter(use_mock=False, use_mcp=True)
policy = PolicyEngine.from_file("policies/default.yaml")

query = "index=main sourcetype=app_logs service=checkout (error OR warn) | head 5"
print(f"\nQuery: {query}")
print(f"Time range: -15m to now")
print("-" * 60)

evidence = adapter.search(query, "-15m to now", "inc_prompt_injection_checkout")
print(f"Evidence items returned: {len(evidence)}")

injections_found = 0
for i, ev in enumerate(evidence, 1):
    msg = ev.sample_event.get("message", ev.sample_event.get("raw", ""))
    svc = ev.sample_event.get("service", "?")
    sev = ev.sample_event.get("severity", "?")
    tool = ev.sample_event.get("mcp_tool", "?")
    note = ev.sample_event.get("note", "")

    if note:
        print(f"\n  [{i}] NOTE: {note}")
        continue

    print(f"\n  [{i}] source={ev.source} tool={tool}")
    print(f"       service={svc} severity={sev}")
    print(f"       message={msg[:80]}")

    decision = policy.evaluate_content(msg)
    if decision.status != "allow":
        injections_found += 1
        print(f"       >>> BLOCKED by {decision.policy_id}")
        print(f"           {decision.reason}")
    else:
        print(f"       policy: allowed")

print("\n" + "=" * 60)
if injections_found > 0:
    print(f"SUCCESS: {injections_found} injection(s) detected from REAL Splunk MCP data")
    print("BlackBoxOps is using live Splunk via MCP - not mock data.")
else:
    print("WARNING: No injections detected.")
print("=" * 60)
