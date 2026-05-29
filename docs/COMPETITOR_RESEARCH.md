# Competitor Research — BlackBoxOps

Date: 2026-05-28
Hackathon: Splunk Agentic Ops Hackathon
Goal: Validate whether “flight recorder for AI agents / agentic operations” already exists, and define how BlackBoxOps must differ.

## Key Findings

### 1. The phrase “AI agent flight recorder” already exists
GitHub search found multiple small projects using similar language:

- whitepaper27/Flight-Recorder
  - “Replay debugger for AI agents — fix failures and replay from the exact failure point”
  - Focus: agent debugging/replay
  - Stars at time checked: 3

- zistica/korveo
  - “open-source firewall & flight recorder for AI agents”
  - Focus: local-first firewall/recording for agents
  - Stars at time checked: 5

- MLaminekane/hawkeye
  - “flight recorder for AI agents - observability and security for Claude Code, Aider, AutoGPT and more”
  - Focus: local agent observability/security
  - Stars at time checked: 5

- DilawarShafiq/unworldly
  - “tamper-proof, ISO 42001 + HIPAA-compliant audit trails for everything AI agents do on your system”
  - Focus: compliance/audit trails for file changes, shell commands, PHI detection, agent identity
  - Stars at time checked: 7

- areeb24111/Ai-Agent-flight-recorder
  - “Record AI agent runs, detect failures, run batch simulations, and inspect everything in one dashboard”
  - Focus: agent run recording/failure inspection
  - Stars at time checked: 1

Conclusion: The name/concept is not completely untouched. We should not claim “first flight recorder for AI agents.” We should claim “Splunk-native evidence and safety layer for agentic operations.”

---

### 2. Agent observability is a crowded category
Representative products/projects:

- AgentOps
  - README positioning: “Observability and DevTool platform for AI Agents”
  - Focus: agent tracing, debugging, sessions, devtool workflow

- LangSmith
  - README positioning: helps teams “debug, evaluate, and monitor language models and intelligent agents”
  - Focus: LangChain-native tracing, evals, monitoring

- Langfuse
  - Open-source LLM engineering/observability platform
  - Focus: traces, prompts, evals, datasets, analytics

- Arize Phoenix
  - LLM observability/evaluation/tracing platform
  - Focus: evals, traces, retrieval/LLM troubleshooting

- Helicone
  - README categories: “Observability”, “Agent Tracing”, “LLM Routing”, cost/latency tracking, datasets/fine-tuning, fallbacks
  - Focus: LLM gateway/observability/routing

- OpenLIT
  - README positioning: “Observability, Evaluations, Rule Engine, Guardrails, Prompts, Vault, Playground, FleetHub”
  - Focus: AI engineering observability/guardrails stack

Conclusion: Generic agent tracing, cost, latency, evals, and dashboards are overdone. BlackBoxOps must not compete as another LangSmith/Langfuse clone.

---

### 3. AI agent governance / runtime control is also emerging
GitHub search found:

- Justin0504/Aegis
  - “Runtime policy enforcement for AI agents. Cryptographic audit trail, human-in-the-loop approvals, kill switch. Zero code changes.”
  - Stars at time checked: 360

- cordum-io/cordum
  - “The open agent control plane. Govern autonomous AI agents with pre-execution policy enforcement, approval gates, and audit trails.”
  - Works with LangChain, CrewAI, MCP, and any framework
  - Stars at time checked: 481

- kontext-security/kontext-cli
  - Runtime security for tool-using AI agents: permissions, credentials, policy enforcement, audit trails
  - Stars at time checked: 199

- jagmarques/asqav-sdk
  - AI agent governance SDK with audit trails, policy enforcement, quantum-safe signatures
  - Works with LangChain, CrewAI, MCP
  - Stars at time checked: 148

Conclusion: Policy enforcement + audit trails already exist. BlackBoxOps must differentiate by being operational-data-aware, Splunk-backed, and evidence-bound.

---

### 4. Splunk MCP projects exist, but mostly as query/chat/SOC assistants
GitHub search found:

- splunk/splunk-mcp-server2
  - “Unofficial. Splunk MCP server. Implemented in Python and TypeScript/JS. Runs searches, queries Splunk, and outputs data as JSON, CSV, or Markdown for agentic LLM workflows.”
  - Includes input SPL validation and output sanitization
  - Stars at time checked: 32

- chalithah/splunk-claude-mcp-agent
  - “Agentic SOC Analyst: A secure, local MCP server connecting Claude AI to Splunk Enterprise. Natural language threat hunting without data leaving your network.”
  - Stars at time checked: 6

- justinsiowqi/splunk-agent
  - “Multi-agent integration for querying Splunk and Jira via the Model Context Protocol.”
  - Stars at time checked: 4

- rsfl/agentic-llm-mcp-threat-emulator
  - “Agentic LLM MCP Threat Emulator companion for Splunk MCP LLM SIEMulator”
  - Stars at time checked: 4

- splunk/ai_agent_splunk_mcp_langgraph
  - Splunk + MCP + LangGraph example
  - Stars at time checked: 2

Conclusion: Splunk MCP usage exists, but most examples are “connect AI to Splunk and query data.” The gap is a production-grade safety/replay/evidence layer around agentic operations.

---

## What Is Overdone

Avoid building:

1. “Chat with Splunk”
   - Natural language question -> SPL -> answer.
   - Too close to Splunk AI Assistant and common MCP demos.

2. Generic SOC copilot
   - Alert summary, MITRE mapping, remediation steps.
   - Very likely many hackathon teams will build this.

3. Basic incident report generator
   - Detect anomaly -> summarize root cause -> generate report.
   - Useful, but not differentiated.

4. Generic agent observability dashboard
   - Trace tool calls, tokens, latency, costs.
   - LangSmith/Langfuse/AgentOps/Helicone already own this space.

5. Simple MCP wrapper
   - Calling splunk_run_query once or twice is not enough.

---

## BlackBoxOps Differentiation

BlackBoxOps should be positioned as:

“Splunk-native evidence and safety layer for agentic operations.”

Not:
- another LLM observability dashboard
- another AI incident chatbot
- another SOC analyst copilot
- another LangSmith clone

### Differentiators

1. Splunk as trusted operational evidence plane
   - Every agent claim is backed by exact Splunk searches, event samples, time ranges, and evidence IDs.

2. MCP safety gateway
   - Agent cannot freely query everything.
   - Queries are checked for scope, cost, sensitivity, prompt-injection, and risky SPL patterns before execution.

3. Agentic operations replay
   - Reconstructs an incident from detection -> query -> reasoning -> policy decision -> approval -> remediation -> verification.

4. Policy-gated remediation
   - High-risk actions require approval.
   - Low-risk actions can execute automatically.
   - All actions require evidence and rollback plan.

5. Operational, not just LLM-centric
   - Ties agent behavior to logs, metrics, incidents, deploy events, user impact, and security signals.

6. Hackathon-native Splunk depth
   - Uses Splunk MCP Server, HEC/Splunk SDK, SPL queries, dashboards, and architecture diagram.

---

## Competitor Comparison

| Category | Examples | What they do | BlackBoxOps difference |
|---|---|---|---|
| LLM observability | LangSmith, Langfuse, Phoenix, Helicone, AgentOps | Trace LLM calls, costs, latency, evals | BlackBoxOps focuses on operational incidents, Splunk evidence, MCP query safety, and remediation audit |
| Agent governance | Aegis, Cordum, Kontext, ASQAV | Policy enforcement, approvals, permissions, audit trails | BlackBoxOps connects policies to live Splunk operational evidence and incident replay |
| Agent flight recorder OSS | Flight-Recorder, Korveo, Hawkeye, Unworldly | Record/replay/debug agent actions | BlackBoxOps is Splunk-native and built for enterprise Ops/SecOps evidence, not only local agent debugging |
| Splunk MCP demos | splunk-mcp-server2, splunk-claude-mcp-agent, Splunk LangGraph examples | Let AI query Splunk | BlackBoxOps wraps MCP with governance, evidence binding, replay, and action safety |
| SOC copilots | Many SIEM AI demos | Alert triage and threat summaries | BlackBoxOps records and governs the agent itself; SOC is one use case, not the whole product |

---

## Recommended Wording for Devpost

Use:
“BlackBoxOps is a Splunk-native flight recorder and safety layer for agentic operations. It records every AI decision, Splunk MCP query, tool call, policy check, human approval, and remediation attempt, then replays incidents with evidence-backed explanations.”

Avoid:
“The first flight recorder for AI agents.”

Use:
“Unlike generic LLM observability tools, BlackBoxOps treats Splunk as the trusted operational evidence layer and focuses on safe autonomous operations.”

---

## Risk Flags

1. The phrase “flight recorder for AI agents” is not unique.
   - Mitigation: differentiate around Splunk-native operational evidence and MCP safety.

2. LLM observability is crowded.
   - Mitigation: do not build generic traces/cost dashboards.

3. Agent governance exists.
   - Mitigation: emphasize real operational data, Splunk queries, incident replay, and remediation validation.

4. Demo must be concrete.
   - Mitigation: show a risky AI ops action blocked by policy, then replay the exact evidence chain.

---

## Final Recommendation

Proceed with BlackBoxOps, but sharpen positioning:

Best category:
Splunk-native agentic operations safety + replay.

Best track:
Platform & Developer Experience.

Bonus target:
Best Use of Splunk MCP Server.

Potential Grand Prize hook:
“As autonomous agents enter production operations, Splunk should become the black box that proves what happened, why it happened, and whether the agent was allowed to act.”
