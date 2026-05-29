from __future__ import annotations

BRAND_TOKENS: dict[str, str] = {
    "void": "#05070B",
    "background": "#070A0F",
    "surface": "#0D1320",
    "surfaceElevated": "#111827",
    "surfaceGlass": "#101826",
    "border": "#233044",
    "borderStrong": "#334155",
    "textPrimary": "#F8FAFC",
    "textSecondary": "#94A3B8",
    "textMuted": "#64748B",
    "splunkGreen": "#65A637",
    "evidenceBlue": "#38BDF8",
    "flightAmber": "#F59E0B",
    "criticalRed": "#EF4444",
    "successGreen": "#22C55E",
    "forensicViolet": "#8B5CF6",
    "blackboxOrange": "#FF6B2C",
    "white": "#FFFFFF",
}


def risk_label(score: float) -> dict[str, str]:
    if score >= 0.8:
        return {"level": "critical", "icon": "●", "text": "Critical risk"}
    if score >= 0.55:
        return {"level": "high", "icon": "▲", "text": "High risk"}
    if score >= 0.35:
        return {"level": "medium", "icon": "◆", "text": "Medium risk"}
    return {"level": "low", "icon": "●", "text": "Low risk"}


def policy_label(status: str) -> dict[str, str]:
    labels = {
        "allow": {"level": "allow", "icon": "✓", "text": "Allowed"},
        "warn": {"level": "warn", "icon": "!", "text": "Warning"},
        "approval_required": {"level": "approval", "icon": "◈", "text": "Approval required"},
        "block": {"level": "block", "icon": "✕", "text": "Blocked"},
    }
    return labels.get(status, {"level": "warn", "icon": "!", "text": status.replace("_", " ").title()})


def build_brand_css() -> str:
    t = BRAND_TOKENS
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {{
  --bb-void: {t['void']};
  --bb-bg: {t['background']};
  --bb-surface: {t['surface']};
  --bb-surface-elevated: {t['surfaceElevated']};
  --bb-border: {t['border']};
  --bb-border-strong: {t['borderStrong']};
  --bb-text: {t['textPrimary']};
  --bb-muted: {t['textSecondary']};
  --bb-splunk: {t['splunkGreen']};
  --bb-evidence: {t['evidenceBlue']};
  --bb-warning: {t['flightAmber']};
  --bb-critical: {t['criticalRed']};
  --bb-orange: {t['blackboxOrange']};
  --bb-violet: {t['forensicViolet']};
}}

.stApp {{
  background:
    radial-gradient(circle at 12% 8%, rgba(56, 189, 248, 0.13), transparent 28%),
    radial-gradient(circle at 85% 10%, rgba(255, 107, 44, 0.12), transparent 28%),
    linear-gradient(135deg, var(--bb-void), var(--bb-bg) 42%, #09111f 100%);
  color: var(--bb-text);
  font-family: Inter, system-ui, sans-serif;
}}

.block-container {{
  padding-top: 2rem;
  max-width: 1480px;
}}

h1, h2, h3, .stMarkdown {{
  font-family: Inter, system-ui, sans-serif;
}}

code, pre, .stCodeBlock {{
  font-family: 'JetBrains Mono', monospace !important;
}}

.bb-hero {{
  border: 1px solid rgba(56, 189, 248, 0.28);
  border-radius: 24px;
  padding: 28px;
  margin-bottom: 22px;
  background:
    linear-gradient(135deg, rgba(13, 19, 32, 0.96), rgba(17, 24, 39, 0.78)),
    repeating-linear-gradient(90deg, rgba(148, 163, 184, 0.04) 0 1px, transparent 1px 72px);
  box-shadow: 0 0 60px rgba(56, 189, 248, 0.08);
}}

.bb-kicker {{
  color: var(--bb-splunk);
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-size: 0.76rem;
}}

.bb-title {{
  font-size: clamp(2.4rem, 6vw, 4.4rem);
  line-height: 0.95;
  letter-spacing: -0.06em;
  font-weight: 800;
  margin: 6px 0 12px;
}}

.bb-subtitle {{
  color: var(--bb-muted);
  max-width: 820px;
  font-size: 1.04rem;
}}

.bb-logo {{
  display: inline-flex;
  align-items: center;
  gap: 10px;
  border: 1px solid rgba(255, 107, 44, 0.38);
  border-radius: 16px;
  padding: 8px 12px;
  background: rgba(5, 7, 11, 0.55);
  color: var(--bb-text);
  font-weight: 800;
}}

.bb-recorder {{
  width: 42px;
  height: 22px;
  border-radius: 7px;
  border: 1px solid var(--bb-border-strong);
  background: linear-gradient(90deg, #111827 0 68%, var(--bb-orange) 68% 100%);
  position: relative;
}}

.bb-recorder:before {{
  content: '';
  position: absolute;
  left: 8px;
  right: 13px;
  top: 10px;
  height: 2px;
  background: var(--bb-evidence);
  box-shadow: 8px -4px 0 -1px var(--bb-evidence), 16px 4px 0 -1px var(--bb-evidence);
}}

.bb-recorder:after {{
  content: '';
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 999px;
  right: 5px;
  top: 8px;
  background: var(--bb-splunk);
  box-shadow: 0 0 12px var(--bb-splunk);
}}

.bb-card {{
  border: 1px solid var(--bb-border);
  border-radius: 16px;
  padding: 16px;
  background: rgba(13, 19, 32, 0.86);
  margin-bottom: 12px;
}}

.bb-card-title {{
  font-weight: 800;
  margin-bottom: 6px;
}}

.bb-meta {{
  color: var(--bb-muted);
  font-size: 0.78rem;
  font-family: 'JetBrains Mono', monospace;
}}

.bb-chip {{
  display: inline-block;
  border: 1px solid var(--bb-border-strong);
  border-radius: 999px;
  padding: 3px 9px;
  margin: 3px 4px 3px 0;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}}

.bb-risk-low {{ color: var(--bb-splunk); border-color: rgba(101, 166, 55, 0.55); }}
.bb-risk-medium {{ color: var(--bb-evidence); border-color: rgba(56, 189, 248, 0.55); }}
.bb-risk-high {{ color: var(--bb-warning); border-color: rgba(245, 158, 11, 0.65); }}
.bb-risk-critical {{ color: var(--bb-critical); border-color: rgba(239, 68, 68, 0.75); }}

.bb-policy-block {{ border-left: 4px solid var(--bb-critical); }}
.bb-policy-approval {{ border-left: 4px solid var(--bb-warning); }}
.bb-policy-allow {{ border-left: 4px solid var(--bb-splunk); }}
.bb-policy-warn {{ border-left: 4px solid var(--bb-evidence); }}

.bb-evidence {{
  border-left: 4px solid var(--bb-evidence);
}}

div.stButton > button:first-child {{
  border-radius: 10px;
  border: 1px solid rgba(101, 166, 55, 0.65);
  background: linear-gradient(135deg, var(--bb-splunk), #4b8529);
  color: white;
  font-weight: 800;
}}

[data-testid="stMetricValue"] {{ color: var(--bb-text); }}
[data-testid="stMetricLabel"] {{ color: var(--bb-muted); }}
</style>
"""
