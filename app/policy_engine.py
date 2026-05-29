from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from app.models import PolicyDecision


class PolicyEngine:
    def __init__(self, rules: list[dict[str, Any]]):
        self.rules = rules

    @classmethod
    def from_file(cls, path: str | Path) -> "PolicyEngine":
        try:
            with Path(path).open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
            return cls(data.get("rules", []))
        except Exception as exc:
            return cls([
                {
                    "id": "policy-load-fail-closed",
                    "type": "query",
                    "status": "block",
                    "risk_level": "critical",
                    "reason": f"Policy file could not be loaded; failing closed: {exc}",
                    "patterns": [""],
                }
            ])

    def evaluate_query(self, query: str, time_range: str = "-15m to now") -> PolicyDecision:
        normalized = query.lower()
        for rule in self._rules_of_type("query"):
            if self._matches_patterns(normalized, rule.get("patterns", [])):
                return self._decision(rule)
        return PolicyDecision(
            policy_id="query-default-allow",
            status="allow",
            reason=f"Scoped diagnostic query allowed for time range {time_range}.",
            risk_level="low",
            matched_rules=[],
        )

    def evaluate_content(self, content: str) -> PolicyDecision:
        normalized = content.lower()
        for rule in self._rules_of_type("content"):
            if self._matches_patterns(normalized, rule.get("patterns", [])):
                return self._decision(rule)
        return PolicyDecision(
            policy_id="content-default-allow",
            status="allow",
            reason="No prompt-injection or unsafe content pattern detected.",
            risk_level="low",
            matched_rules=[],
        )

    def evaluate_action(self, action_type: str, target: str, evidence_refs: list[str] | None = None) -> PolicyDecision:
        if not evidence_refs:
            return PolicyDecision(
                policy_id="action-requires-evidence",
                status="block",
                reason=f"Action {action_type} on {target} is blocked because it has no evidence_refs.",
                risk_level="high",
                matched_rules=["action-requires-evidence"],
            )
        for rule in self._rules_of_type("action"):
            if action_type in rule.get("action_types", []):
                return self._decision(rule)
        return PolicyDecision(
            policy_id="action-default-warn",
            status="warn",
            reason=f"Unknown action {action_type} on {target}; warn and record for review.",
            risk_level="medium",
            matched_rules=[],
        )

    def _rules_of_type(self, rule_type: str) -> list[dict[str, Any]]:
        return [rule for rule in self.rules if rule.get("type") == rule_type]

    @staticmethod
    def _matches_patterns(value: str, patterns: list[str]) -> bool:
        return any(pattern.lower() in value for pattern in patterns)

    @staticmethod
    def _decision(rule: dict[str, Any]) -> PolicyDecision:
        return PolicyDecision(
            policy_id=rule["id"],
            status=rule.get("status", "block"),
            reason=rule.get("reason", "Policy matched."),
            risk_level=rule.get("risk_level", "high"),
            matched_rules=[rule["id"]],
            required_approval=rule.get("status") == "approval_required",
        )
