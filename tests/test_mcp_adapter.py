import json
from types import SimpleNamespace

from app.splunk_adapter import (
    SplunkAdapter,
    _build_search_args,
    _content_rows,
    _pick_search_tool,
)


def _tool(name, schema=None):
    return SimpleNamespace(name=name, inputSchema=schema or {})


def test_pick_search_tool_prefers_known_names():
    tools = [_tool("explain_spl"), _tool("run_splunk_search"), _tool("list_indexes")]
    assert _pick_search_tool(tools).name == "run_splunk_search"


def test_pick_search_tool_falls_back_to_name_match():
    tools = [_tool("list_indexes"), _tool("spl_search_runner")]
    assert _pick_search_tool(tools).name == "spl_search_runner"


def test_pick_search_tool_returns_none_when_absent():
    assert _pick_search_tool([_tool("list_indexes")]) is None


def test_build_search_args_maps_schema_properties():
    schema = {"properties": {"search": {}, "earliest_time": {}, "latest_time": {}}}
    args = _build_search_args(schema, "index=checkout | head 5")
    assert args == {"search": "index=checkout | head 5", "earliest_time": "-15m", "latest_time": "now"}


def test_build_search_args_defaults_to_query_key():
    args = _build_search_args({}, "index=main")
    assert args == {"query": "index=main"}


def test_content_rows_parses_json_text_blocks():
    payload = {"results": [{"host": "web-1"}, {"host": "web-2"}]}
    result = SimpleNamespace(content=[SimpleNamespace(text=json.dumps(payload))], structuredContent=None)
    assert _content_rows(result) == [{"host": "web-1"}, {"host": "web-2"}]


def test_content_rows_prefers_structured_content():
    result = SimpleNamespace(content=[], structuredContent={"results": [{"a": 1}]})
    assert _content_rows(result) == [{"a": 1}]


def test_content_rows_wraps_plain_text():
    result = SimpleNamespace(content=[SimpleNamespace(text="not json")], structuredContent=None)
    assert _content_rows(result) == [{"raw": "not json"}]


def test_search_routes_to_mcp_when_enabled(monkeypatch):
    adapter = SplunkAdapter(use_mock=False, use_mcp=True)
    sentinel = [object()]
    monkeypatch.setattr(adapter, "mcp_search", lambda query, time_range="-15m to now": sentinel)
    assert adapter.search("index=checkout") is sentinel


def test_mcp_search_returns_error_evidence_when_unreachable(monkeypatch):
    monkeypatch.setenv("SPLUNK_MCP_URL", "https://127.0.0.1:9/services/mcp/")
    monkeypatch.setenv("SPLUNK_MCP_TOKEN", "not-a-real-token")
    adapter = SplunkAdapter(use_mock=False, use_mcp=True)
    evidence = adapter.mcp_search("index=checkout | head 1")
    assert len(evidence) == 1
    assert evidence[0].source == "splunk_mcp"
    assert "splunk-mcp-error" in evidence[0].risk_flags
    assert evidence[0].confidence == 0.2
