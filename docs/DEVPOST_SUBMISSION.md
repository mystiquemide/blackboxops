# Devpost Submission Draft — BlackBoxOps

## Project name
BlackBoxOps

## One-liner
The flight recorder for agentic operations.

## Short pitch
BlackBoxOps is a Splunk-native flight recorder and safety layer for agentic operations. It records AI decisions, Splunk-style queries, tool calls, evidence references, policy checks, approval gates, and remediation proposals, then replays the incident with evidence-backed explanations.

## Inspiration
AI operations agents are becoming powerful enough to query production systems and propose remediation. But when an agent acts on bad evidence, prompt-injected logs, or unsafe SPL, teams need more than a chatbot transcript. They need a forensic record: what did the agent see, why did it believe it, which policy allowed or blocked it, and what evidence supports the conclusion?

## What it does
- Records agent prompts, responses, Splunk queries, evidence, policy checks, approvals, and remediation attempts.
- Wraps Splunk-style searches with a YAML policy gateway.
- Detects prompt-injection text inside retrieved operational logs.
- Blocks broad/destructive SPL before it reaches Splunk.
- Requires approval for disruptive actions like service restarts.
- Generates incident replay timelines and evidence-backed postmortems.

## How we built it
- Python + FastAPI backend
- Streamlit incident replay UI
- Pydantic event/evidence/policy models
- YAML safety policies
- JSONL event recorder
- Mock-first Splunk adapter with hooks for Splunk Search/MCP/HEC
- pytest test suite

## How Splunk is used
The MVP uses Splunk-shaped evidence and a mock-first adapter to keep the live demo reliable. The architecture includes adapter hooks for Splunk MCP Server tools, Splunk Search API, and HEC ingestion. The key product idea is that Splunk becomes the evidence plane for safe agentic operations.

## Tracks
Primary: Platform & Developer Experience
Bonus: Best Use of Splunk MCP Server

## Differentiation
BlackBoxOps is not a generic AI observability dashboard and not a simple Splunk chatbot. It focuses on the operational safety layer between AI agents and Splunk: evidence binding, policy-gated queries/actions, prompt-injection detection from logs, and incident replay.

## What is next
- Wire app/splunk_adapter.py to real Splunk MCP Server tools.
- Add signed approvals.
- Add richer policy packs for SOC/SRE workflows.
- Export replay bundles into Splunk dashboards.
