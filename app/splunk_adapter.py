from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from app.models import EvidenceRef

_MCP_SEARCH_TOOL_PRIORITY = ("run_splunk_search", "run_search", "search", "run_spl_search", "splunk_search")


def _pick_search_tool(tools: list[Any]) -> Any | None:
    """Pick the SPL search tool from the Splunk MCP server's tool listing."""
    by_name = {tool.name.lower(): tool for tool in tools}
    for name in _MCP_SEARCH_TOOL_PRIORITY:
        if name in by_name:
            return by_name[name]
    for tool in tools:
        if "search" in tool.name.lower():
            return tool
    return None


def _build_search_args(schema: dict[str, Any] | None, query: str, earliest: str = "-15m", latest: str = "now") -> dict[str, Any]:
    """Map our SPL query onto whatever argument names the MCP tool's schema declares."""
    props = schema.get("properties", {}) if isinstance(schema, dict) else {}
    args: dict[str, Any] = {}
    for key in ("query", "search", "spl", "search_query", "spl_query"):
        if key in props:
            args[key] = query
            break
    else:
        args["query"] = query
    if "earliest_time" in props:
        args["earliest_time"] = earliest
    if "latest_time" in props:
        args["latest_time"] = latest
    return args


def _content_rows(result: Any) -> list[Any]:
    """Flatten an MCP tool result into result rows, tolerating text or structured output."""
    structured = getattr(result, "structuredContent", None)
    if isinstance(structured, dict):
        for key in ("results", "rows", "events"):
            value = structured.get(key)
            if isinstance(value, list):
                return value
    rows: list[Any] = []
    for block in getattr(result, "content", None) or []:
        text = getattr(block, "text", None)
        if not text:
            continue
        try:
            parsed = json.loads(text)
        except ValueError:
            rows.append({"raw": text})
            continue
        if isinstance(parsed, list):
            rows.extend(parsed)
        elif isinstance(parsed, dict):
            inner = parsed.get("results") or parsed.get("rows") or parsed.get("events")
            rows.extend(inner if isinstance(inner, list) else [parsed])
    return rows


def _content_text(result: Any) -> str:
    return " ".join(str(getattr(block, "text", "")) for block in (getattr(result, "content", None) or []))


def _httpx_factory(verify: bool):
    def factory(headers: dict[str, str] | None = None, timeout: Any = None, auth: Any = None):
        import httpx

        return httpx.AsyncClient(verify=verify, follow_redirects=True, headers=headers, timeout=timeout, auth=auth)

    return factory


class SplunkAdapter:
    def __init__(
        self,
        sample_path: str | Path = "data/sample_splunk_events.jsonl",
        use_mock: bool | None = None,
        use_mcp: bool | None = None,
    ):
        self.sample_path = Path(sample_path)
        self.use_mock = use_mock if use_mock is not None else os.getenv("USE_MOCK_SPLUNK", "true").lower() == "true"
        self.use_mcp = use_mcp if use_mcp is not None else os.getenv("USE_SPLUNK_MCP", "false").lower() == "true"

    def search(self, query: str, time_range: str = "-15m to now", incident_id: str | None = None) -> list[EvidenceRef]:
        if self.use_mock:
            return self.mock_search(query, time_range, incident_id)
        if self.use_mcp:
            return self.mcp_search(query, time_range)
        return self.real_search_stub(query, time_range)

    def mcp_search(self, query: str, time_range: str = "-15m to now") -> list[EvidenceRef]:
        """Run the SPL query through the official Splunk MCP Server tool call."""
        import asyncio

        try:
            rows, tool_name = asyncio.run(self._mcp_search_async(query))
        except Exception as exc:
            return [
                EvidenceRef(
                    query=query,
                    time_range=time_range,
                    source="splunk_mcp",
                    sample_event={"error": str(exc), "note": "Splunk MCP tool call failed."},
                    confidence=0.2,
                    risk_flags=["splunk-mcp-error"],
                )
            ]
        if not rows:
            return [
                EvidenceRef(
                    query=query,
                    time_range=time_range,
                    source="splunk_mcp",
                    sample_event={"note": "Splunk MCP search returned 0 results.", "mcp_tool": tool_name},
                    confidence=0.5,
                    risk_flags=[],
                )
            ]
        evidence: list[EvidenceRef] = []
        for row in rows[:3]:
            sample = (
                {key: str(value) for key, value in row.items() if not key.startswith("_")}
                if isinstance(row, dict)
                else {"raw": str(row)}
            )
            sample["mcp_tool"] = tool_name
            evidence.append(
                EvidenceRef(
                    query=query,
                    time_range=time_range,
                    source="splunk_mcp",
                    sample_event=sample,
                    confidence=0.9,
                    risk_flags=["splunk-mcp-live"],
                )
            )
        return evidence

    async def _mcp_search_async(self, query: str) -> tuple[list[Any], str]:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client

        host = os.getenv("SPLUNK_HOST", "localhost")
        port = os.getenv("SPLUNK_PORT", "8089")
        url = os.getenv("SPLUNK_MCP_URL") or f"https://{host}:{port}/services/mcp/"
        token = os.getenv("SPLUNK_MCP_TOKEN", "")
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        verify = os.getenv("SPLUNK_MCP_VERIFY_TLS", "false").lower() == "true"

        async with streamablehttp_client(url, headers=headers, httpx_client_factory=_httpx_factory(verify)) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                listing = await session.list_tools()
                tool = _pick_search_tool(listing.tools)
                if tool is None:
                    raise RuntimeError("Splunk MCP server exposed no search tool")
                args = _build_search_args(getattr(tool, "inputSchema", None), query)
                result = await session.call_tool(tool.name, args)
                if getattr(result, "isError", False):
                    raise RuntimeError(f"MCP tool {tool.name} errored: {_content_text(result)[:300]}")
                return _content_rows(result), tool.name

    def mock_search(self, query: str, time_range: str = "-15m to now", incident_id: str | None = None) -> list[EvidenceRef]:
        rows = self._load_sample_events()
        if incident_id:
            rows = [row for row in rows if row.get("incident_id") == incident_id]
        query_lower = query.lower()
        if "checkout" in query_lower:
            rows = [row for row in rows if row.get("service") == "checkout"]
        elif "cache" in query_lower:
            rows = [row for row in rows if row.get("service") == "cache"]
        if not rows:
            return []
        evidence: list[EvidenceRef] = []
        for row in rows[:3]:
            confidence = 0.95 if row.get("severity") in {"error", "warn"} else 0.75
            evidence.append(
                EvidenceRef(
                    evidence_id=f"EVD-{100 + len(evidence)}",
                    query=query,
                    time_range=time_range,
                    source="mock_splunk",
                    sample_event=row,
                    confidence=confidence,
                    risk_flags=row.get("risk_flags", []),
                )
            )
        return evidence

    def real_search_stub(self, query: str, time_range: str = "-15m to now") -> list[EvidenceRef]:
        import time as _time
        import warnings

        import requests
        from requests.packages.urllib3.exceptions import InsecureRequestWarning  # type: ignore[attr-defined]

        warnings.filterwarnings("ignore", category=InsecureRequestWarning)

        host = os.getenv("SPLUNK_HOST", "localhost")
        port = int(os.getenv("SPLUNK_PORT", "8089"))
        token = os.getenv("SPLUNK_TOKEN", "")
        base = f"https://{host}:{port}"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            create = requests.post(
                f"{base}/services/search/jobs",
                headers=headers,
                data={
                    "search": f"search {query}",
                    "output_mode": "json",
                    "earliest_time": "-15m",
                    "latest_time": "now",
                    "count": 10,
                },
                verify=False,
                timeout=30,
            )
            create.raise_for_status()
            sid = create.json()["sid"]

            for _ in range(30):
                poll = requests.get(
                    f"{base}/services/search/jobs/{sid}",
                    headers=headers,
                    params={"output_mode": "json"},
                    verify=False,
                    timeout=10,
                )
                if poll.json()["entry"][0]["content"]["isDone"]:
                    break
                _time.sleep(1)

            results_resp = requests.get(
                f"{base}/services/search/jobs/{sid}/results",
                headers=headers,
                params={"output_mode": "json", "count": 10},
                verify=False,
                timeout=10,
            )
            rows = results_resp.json().get("results", [])

            if rows:
                return [
                    EvidenceRef(
                        query=query,
                        time_range=time_range,
                        source="splunk_search_api",
                        sample_event={k: str(v) for k, v in row.items() if not k.startswith("_")},
                        confidence=0.9,
                        risk_flags=["splunk-live"],
                    )
                    for row in rows[:3]
                ]
        except Exception as exc:
            return [
                EvidenceRef(
                    query=query,
                    time_range=time_range,
                    source="splunk_search_api",
                    sample_event={"error": str(exc), "note": "Splunk REST API call failed."},
                    confidence=0.2,
                    risk_flags=["splunk-error"],
                )
            ]

        return [
            EvidenceRef(
                query=query,
                time_range=time_range,
                source="splunk_search_api",
                sample_event={"note": "Splunk search returned 0 results."},
                confidence=0.5,
                risk_flags=[],
            )
        ]

    def send_hec_event(self, event: dict[str, Any]) -> bool:
        if self.use_mock:
            return True
        import warnings

        import requests
        from requests.packages.urllib3.exceptions import InsecureRequestWarning  # type: ignore[attr-defined]

        warnings.filterwarnings("ignore", category=InsecureRequestWarning)

        host = os.getenv("SPLUNK_HOST", "localhost")
        hec_port = int(os.getenv("SPLUNK_HEC_PORT", "8088"))
        token = os.getenv("SPLUNK_HEC_TOKEN", "")
        if not token:
            return False
        try:
            resp = requests.post(
                f"https://{host}:{hec_port}/services/collector",
                headers={"Authorization": f"Splunk {token}"},
                json={"event": event, "sourcetype": "blackboxops:agent_event"},
                verify=False,
                timeout=5,
            )
            return resp.status_code == 200
        except Exception:
            return False

    def _load_sample_events(self) -> list[dict[str, Any]]:
        if not self.sample_path.exists():
            return []
        with self.sample_path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
