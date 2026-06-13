"""LLM analysis layer for BlackBoxOps.

Priority chain per call:
  1. Splunk hosted model via | ai provider=splunk (USE_SPLUNK_AI=true + REST creds)
  2. Groq (GROQ_API_KEY set) - uses OpenAI-compatible API, no extra SDK
  3. Template fallback (always works, no external calls)
"""
from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import EvidenceRef, IncidentReplay


class LLMAnalyzer:
    """Stateless analyzer. Instantiate once per request or reuse across a demo run."""

    last_source: str = "template"

    # ── public API ────────────────────────────────────────────────────────────

    def analyze_evidence(self, evidence_items: list["EvidenceRef"], incident_title: str) -> str:
        prompt = self._evidence_prompt(evidence_items, incident_title)
        result = self._splunk_ai(prompt)
        if result:
            self.last_source = "splunk-ai"
            return result.strip()
        result = self._groq(prompt)
        if result:
            self.last_source = "groq"
            return result.strip()
        self.last_source = "template"
        return self._template_analysis(evidence_items)

    def generate_recommendation(self, replay: "IncidentReplay") -> str:
        prompt = self._recommendation_prompt(replay)
        result = self._splunk_ai(prompt)
        if result:
            self.last_source = "splunk-ai"
            return result.strip()
        result = self._groq(prompt)
        if result:
            self.last_source = "groq"
            return result.strip()
        self.last_source = "template"
        return self._template_recommendation(replay)

    # ── prompt builders ───────────────────────────────────────────────────────

    def _evidence_prompt(self, evidence_items: list["EvidenceRef"], incident_title: str) -> str:
        lines = []
        for item in evidence_items[:3]:
            msg = item.sample_event.get("message", str(item.sample_event))[:200]
            flags = ", ".join(item.risk_flags) or "none"
            lines.append(
                f"- SPL: {item.query}\n"
                f"  log: {msg}\n"
                f"  risk_flags: {flags}  confidence: {item.confidence:.2f}"
            )
        return (
            f"You are a senior SRE reviewing an ops incident. Be concise and direct.\n\n"
            f"Incident: {incident_title}\n\n"
            f"Splunk evidence:\n" + "\n".join(lines) + "\n\n"
            f"Write a 3-sentence risk assessment:\n"
            f"1. What the evidence shows\n"
            f"2. Key risk factors identified\n"
            f"3. Recommended immediate action\n\n"
            f"No preamble. Start directly with the finding."
        )

    def _recommendation_prompt(self, replay: "IncidentReplay") -> str:
        blocks = sum(1 for d in replay.policy_decisions if d.status == "block")
        approvals = sum(1 for d in replay.policy_decisions if d.required_approval)
        return (
            f"Incident: {replay.title}\n"
            f"Policy blocks: {blocks}, approval gates: {approvals}, "
            f"evidence items: {len(replay.evidence)}, outcome: {replay.outcome}\n\n"
            f"Write a 2-sentence post-incident recommendation for the ops team. "
            f"Be specific and actionable. No preamble."
        )

    # ── Splunk hosted model via | ai provider=splunk ──────────────────────────

    def _splunk_ai(self, prompt: str) -> str | None:
        if os.getenv("USE_SPLUNK_AI", "false").lower() != "true":
            return None
        host = os.getenv("SPLUNK_HOST", "")
        token = os.getenv("SPLUNK_TOKEN", "")
        if not host or not token:
            return None

        import requests
        from requests.packages.urllib3.exceptions import InsecureRequestWarning  # type: ignore[attr-defined]
        import warnings

        verify = os.getenv("SPLUNK_VERIFY_TLS", "true").strip().lower() not in {"0", "false", "no", "off"}
        if not verify:
            warnings.filterwarnings("ignore", category=InsecureRequestWarning)

        model = os.getenv("SPLUNK_AI_MODEL", "gpt-oss-20b")
        safe = prompt.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", "")
        spl = f'| makeresults | eval prompt="{safe}" | ai prompt=prompt provider=splunk model={model} | table ai_response'
        base = f"https://{host}:{os.getenv('SPLUNK_PORT', '8089')}"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            # Submit async job
            create_r = requests.post(
                f"{base}/services/search/jobs",
                headers=headers,
                data={"search": spl, "output_mode": "json", "count": 1},
                verify=verify,
                timeout=30,
            )
            if not create_r.ok:
                return None
            sid = create_r.json()["sid"]

            # Poll up to 90s - LLM calls can be slow
            for _ in range(45):
                time.sleep(2)
                poll_r = requests.get(
                    f"{base}/services/search/jobs/{sid}",
                    headers=headers,
                    params={"output_mode": "json"},
                    verify=verify,
                    timeout=10,
                )
                if poll_r.ok and poll_r.json()["entry"][0]["content"].get("isDone"):
                    break

            results_r = requests.get(
                f"{base}/services/search/jobs/{sid}/results",
                headers=headers,
                params={"output_mode": "json", "count": 1},
                verify=verify,
                timeout=15,
            )
            rows = results_r.json().get("results", [])
            if rows:
                text = str(rows[0].get("ai_response", "")).strip()
                return text or None
        except Exception:
            pass
        return None

    # ── Groq (OpenAI-compatible, no extra SDK needed) ─────────────────────────

    def _groq(self, prompt: str) -> str | None:
        key = os.getenv("GROQ_API_KEY", "")
        if not key:
            return None
        import httpx
        try:
            r = httpx.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 256,
                },
                timeout=30.0,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except Exception:
            return None

    # ── template fallbacks (always work) ─────────────────────────────────────

    def _template_analysis(self, evidence_items: list["EvidenceRef"]) -> str:
        injection = any(
            "prompt-injection" in flag
            for item in evidence_items
            for flag in item.risk_flags
        )
        if injection:
            return (
                "Splunk evidence shows malicious content embedded in retrieved log payloads, "
                "consistent with a prompt-injection attempt targeting the ops agent. "
                "The injected instructions attempted to redirect agent behavior toward unauthorized data deletion. "
                "BlackBoxOps policy gateway intercepted the payload before it could influence downstream decisions."
            )
        high_risk = any(item.confidence >= 0.8 and item.risk_flags for item in evidence_items)
        if high_risk:
            return (
                "Splunk evidence indicates elevated risk signals across retrieved operational logs. "
                "Risk flags suggest anomalous patterns that warrant human review before automated remediation. "
                "BlackBoxOps has bound all claims to evidence refs and paused high-risk actions pending approval."
            )
        return (
            "Splunk evidence was retrieved and bound to the incident context for audit. "
            "Evidence confidence levels are within normal operational bounds with no injection patterns detected. "
            "BlackBoxOps recorded all agent queries and proposed actions in the replay timeline for review."
        )

    def _template_recommendation(self, replay: "IncidentReplay") -> str:
        if any(d.status == "block" for d in replay.policy_decisions):
            return (
                "Keep the agent in approval-gated mode for disruptive actions and investigate "
                "the malicious trace payload separately as a prompt-injection attempt against the ops workflow. "
                "Review SPL query scope policies and tighten index access to prevent future broad searches."
            )
        return (
            "Continue monitoring the affected service with scoped Splunk queries and verify "
            "that the ticket created captures all evidence refs for downstream investigation. "
            "Consider adding a watchdog alert for the same error pattern to detect recurrence automatically."
        )
