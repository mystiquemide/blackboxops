from __future__ import annotations

# --- Antimetal-inspired BlackBoxOps brand tokens ---
# Warm near-black ground + glass surfaces + accent green/amber.
t = {
    "void": "#0A0C10",
    "bgBase": "#0E1016",
    "bgElevated": "#14171F",
    "surfaceGlass": "rgba(20, 23, 31, 0.82)",
    "cardFill": "rgba(16, 18, 24, 0.92)",
    "ink": "#EBEDF0",
    "inkSecondary": "#9599A0",
    "inkMuted": "#5F636E",
    "borderGlass": "rgba(255, 255, 255, 0.07)",
    "borderStrong": "rgba(255, 255, 255, 0.13)",
    "splunkGreen": "#65A637",
    "evidenceCyan": "#22D3EE",
    "amber": "#FBBF24",
    "criticalRed": "#EF4444",
    "orange": "#F97316",
    "violet": "#8B5CF6",
    "white": "#FFFFFF",
    # Preserve the original public token contract used by tests and extensions.
    "background": "#070A0F",
    "evidenceBlue": "#38BDF8",
    "blackboxOrange": "#FF6B2C",
}

BRAND_TOKENS: dict[str, str] = t


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
    return f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700;14..32,800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {{
  --bb-void: {t['void']};
  --bb-bg: {t['bgBase']};
  --bb-bg-elevated: {t['bgElevated']};
  --bb-glass: {t['surfaceGlass']};
  --bb-card: {t['cardFill']};
  --bb-ink: {t['ink']};
  --bb-ink-secondary: {t['inkSecondary']};
  --bb-ink-muted: {t['inkMuted']};
  --bb-border-glass: {t['borderGlass']};
  --bb-border-strong: {t['borderStrong']};
  --bb-green: {t['splunkGreen']};
  --bb-cyan: {t['evidenceCyan']};
  --bb-amber: {t['amber']};
  --bb-red: {t['criticalRed']};
  --bb-orange: {t['orange']};
  --bb-violet: {t['violet']};
  --bb-white: {t['white']};
  --bb-legacy-background: {t['background']};
  --font-serif: 'Source Serif 4', Georgia, serif;
  --font-sans: 'Inter', ui-sans-serif, system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
  --max-w: 1512px;
  --px: clamp(24px, 5vw, 120px);
  --py: clamp(60px, 9vw, 110px);
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}}

/* ═══════════════ RESET & BASE ═══════════════ */
.stApp {{
  background: radial-gradient(circle at 18% 0%, rgba(34,211,238,0.09), transparent 40%),
              radial-gradient(circle at 82% 100%, rgba(101,166,55,0.07), transparent 42%),
              var(--bb-void) !important;
  color: var(--bb-ink);
  font-family: var(--font-sans);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}}
.block-container {{
  padding: 0 !important;
  max-width: 100% !important;
}}
.stMain, .main > div:first-child {{ overflow-x: hidden; }}

/* hide Streamlit chrome */
[data-testid="stToolbar"] {{ display: none !important; }}
[data-testid="stDecoration"] {{ display: none !important; }}
[data-testid="stHeader"] {{ display: none !important; }}
#MainMenu {{ display: none !important; }}
footer {{ display: none !important; }}
.stDeployButton {{ display: none !important; }}

/* ═══════════════ TYPOGRAPHY ═══════════════ */
h1, h2, h3, h4, h5, h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
[data-testid="stHeading"] h1, [data-testid="stHeading"] h2, [data-testid="stHeading"] h3 {{
  font-family: var(--font-serif) !important;
  font-weight: 400 !important;
  color: var(--bb-ink) !important;
  letter-spacing: -0.03em !important;
  padding: 0 !important;
  margin: 0 !important;
}}
p, li, span, label, div:not([class*="bb-"]) {{
  font-family: var(--font-sans);
  color: var(--bb-ink-secondary);
}}
code, pre, .stCodeBlock, .stCodeBlock code, .stCodeBlock pre {{
  font-family: var(--font-mono) !important;
}}

/* ═══════════════ NAV ═══════════════ */
.bb-nav {{
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 24px var(--px) 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 76px;
  background: transparent;
  max-width: var(--max-w);
  margin: 0 auto;
}}
.bb-nav-logo {{
  font-family: var(--font-sans);
  font-size: 16px;
  font-weight: 500;
  color: var(--bb-ink);
  letter-spacing: -0.01em;
  text-decoration: none;
}}
.bb-nav-logo span {{ color: var(--bb-green); }}
.bb-nav-links {{
  display: flex;
  align-items: center;
  gap: 8px;
  list-style: none;
  margin: 0;
  padding: 0;
}}
.bb-nav-links li a {{
  padding: 6px 14px;
  font-size: 14px;
  font-weight: 500;
  color: var(--bb-ink-muted);
  text-decoration: none;
  border-radius: 9999px;
  transition: color 0.15s, background 0.15s;
}}
.bb-nav-links li a:hover {{ color: var(--bb-ink); background: rgba(255,255,255,0.04); }}
.bb-nav-cta {{
  background: var(--bb-ink) !important;
  color: var(--bb-void) !important;
  border-radius: 9999px !important;
  padding: 6px 14px !important;
  transition: opacity 0.15s !important;
}}
.bb-nav-cta:hover {{ opacity: 0.9; background: var(--bb-ink) !important; }}

/* ═══════════════ SECTIONS ═══════════════ */
.bb-section {{
  max-width: var(--max-w);
  margin: 0 auto;
  padding: var(--py) var(--px);
}}
.bb-section-hero {{
  max-width: var(--max-w);
  margin: 0 auto;
  padding: clamp(100px, 16vh, 180px) var(--px) clamp(60px, 10vh, 100px);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}}
.bb-section-dark {{
  background: radial-gradient(circle at 47% 56%, rgba(34,211,238,0.13), rgba(34,211,238,0.06) 30%, rgba(34,211,238,0.02) 55%, var(--bb-bg) 100%);
  border-radius: 32px;
  margin: 0 clamp(12px, 2vw, 40px);
  padding: clamp(48px, 8vw, 80px) clamp(32px, 5vw, 80px);
  position: relative;
  overflow: hidden;
  border: 1px solid var(--bb-border-glass);
}}
.bb-section-dark::before {{
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  background: linear-gradient(122deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.02) 40%, rgba(255,255,255,0.01) 78%);
  z-index: 1;
}}
.bb-section-dark > * {{ position: relative; z-index: 2; }}

/* ═══════════════ DIVIDERS ═══════════════ */
.bb-divider {{
  width: 100%;
  max-width: var(--max-w);
  margin: 0 auto;
  border: 0;
  border-top: 1px dashed var(--bb-border-glass);
}}

/* ═══════════════ HERO ═══════════════ */
.bb-hero {{
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 28px;
}}
.bb-kicker {{
  font-family: var(--font-sans) !important;
  font-size: 0.76rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.16em !important;
  text-transform: uppercase !important;
  color: var(--bb-green) !important;
}}
.bb-hero-title {{
  font-family: var(--font-serif) !important;
  font-size: clamp(38px, 5.8vw, 62px) !important;
  line-height: 1.05 !important;
  letter-spacing: -0.035em !important;
  font-weight: 400 !important;
  color: var(--bb-ink) !important;
  max-width: 820px;
  animation: bb-fade-up 0.8s var(--ease-out-expo) 0.1s forwards;
}}
.bb-hero-subtitle {{
  font-family: var(--font-serif) !important;
  font-size: clamp(17px, 2.1vw, 23px) !important;
  line-height: 1.45 !important;
  color: var(--bb-ink-secondary) !important;
  font-weight: 400 !important;
  max-width: 680px;
  animation: bb-fade-up 0.8s var(--ease-out-expo) 0.25s forwards;
}}
.bb-hero-actions {{
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 12px;
  animation: bb-fade-up 0.7s var(--ease-out-expo) 0.4s forwards;
}}

/* ═══════════════ BUTTONS ═══════════════ */
.bb-btn-primary {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--bb-ink);
  color: var(--bb-void) !important;
  font-family: var(--font-sans);
  font-size: 14px;
  font-weight: 500;
  border: none;
  border-radius: 9999px;
  padding: 12.5px 24.5px;
  cursor: pointer;
  text-decoration: none;
  transition: opacity 0.15s, transform 0.2s var(--ease-spring);
}}
.bb-btn-primary:hover {{
  opacity: 0.9;
  transform: scale(1.03);
}}
.bb-btn-ghost {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-sans);
  font-size: 16px;
  font-weight: 400;
  color: var(--bb-ink);
  background: transparent;
  border: none;
  cursor: pointer;
  text-decoration: none;
  padding: 0;
  transition: opacity 0.15s;
}}
.bb-btn-ghost:hover {{ opacity: 0.7; }}

/* ═══════════════ CARDS ═══════════════ */
.bb-card {{
  background: var(--bb-card);
  border: 1px solid var(--bb-border-glass);
  border-radius: 16px;
  padding: 20px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  transition: border-color 0.25s, box-shadow 0.25s;
}}
.bb-card:hover {{
  border-color: var(--bb-border-strong);
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
}}
.bb-card-glass {{
  background: linear-gradient(122deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 40%, rgba(255,255,255,0) 78%);
  border: 1px solid var(--bb-border-glass);
  border-radius: 20px;
  padding: 32px;
}}
.bb-card-title {{
  font-family: var(--font-serif) !important;
  font-size: 18px !important;
  font-weight: 400 !important;
  color: var(--bb-ink) !important;
  margin: 0 0 6px !important;
  padding: 0 !important;
}}
.bb-meta {{
  font-family: var(--font-mono) !important;
  font-size: 0.72rem !important;
  color: var(--bb-ink-muted) !important;
}}

/* ═══════════════ CHIPS ═══════════════ */
.bb-chip {{
  display: inline-flex;
  align-items: center;
  font-family: var(--font-sans);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  border: 1px solid var(--bb-border-strong);
  border-radius: 999px;
  padding: 3px 10px;
  margin: 2px 5px 2px 0;
  color: var(--bb-ink-secondary);
  background: rgba(255,255,255,0.02);
}}
.bb-chip-sm {{ font-size: 0.68rem; padding: 2px 8px; }}
.bb-chip--risk-low, .bb-risk-low {{ color: var(--bb-green); border-color: rgba(101,166,55,0.45); }}
.bb-chip--risk-medium, .bb-risk-medium {{ color: var(--bb-cyan); border-color: rgba(34,211,238,0.45); }}
.bb-chip--risk-high, .bb-risk-high {{ color: var(--bb-amber); border-color: rgba(251,191,36,0.55); }}
.bb-chip--risk-critical, .bb-risk-critical {{ color: var(--bb-red); border-color: rgba(239,68,68,0.6); }}

/* ═══════════════ SECTION HEADERS ═══════════════ */
.bb-section-kicker {{
  font-family: var(--font-sans) !important;
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
  color: var(--bb-ink-muted) !important;
  margin-bottom: 8px !important;
  padding: 0 !important;
}}
.bb-section-heading {{
  font-family: var(--font-serif) !important;
  font-size: clamp(30px, 4.2vw, 50px) !important;
  line-height: 1.1 !important;
  letter-spacing: -0.025em !important;
  font-weight: 400 !important;
  color: var(--bb-ink) !important;
  max-width: 720px;
  margin: 0 0 16px !important;
  padding: 0 !important;
}}
.bb-section-sub {{
  font-family: var(--font-sans) !important;
  font-size: 16px !important;
  color: var(--bb-ink-secondary) !important;
  max-width: 620px;
  line-height: 1.5 !important;
  margin: 0 0 40px !important;
}}

/* ═══════════════ TIMELINE ═══════════════ */
.bb-timeline {{
  position: relative;
  padding-left: 0;
}}
.bb-timeline::before {{
  content: '';
  position: absolute;
  left: 4.5px;
  top: 0;
  bottom: 0;
  width: 1px;
  background: var(--bb-border-glass);
}}
.bb-timeline-item {{
  display: flex;
  gap: 20px;
  align-items: flex-start;
  margin-bottom: 0;
  position: relative;
  padding-bottom: 20px;
}}
.bb-timeline-item:last-child {{ padding-bottom: 0; }}
.bb-timeline-dot {{
  flex-shrink: 0;
  width: 10px;
  height: 10px;
  border-radius: 999px;
  margin-top: 22px;
  background: var(--bb-border-strong);
  position: relative;
  z-index: 1;
}}
.bb-timeline-dot--critical {{ background: var(--bb-red); box-shadow: 0 0 8px var(--bb-red); }}
.bb-timeline-dot--high {{ background: var(--bb-amber); box-shadow: 0 0 6px var(--bb-amber); }}
.bb-timeline-dot--medium {{ background: var(--bb-cyan); }}
.bb-timeline-dot--low {{ background: var(--bb-green); }}

/* ═══════════════ EVIDENCE / POLICY CARDS ═══════════════ */
.bb-evidence-card {{
  border-left: 3px solid var(--bb-cyan);
  background: var(--bb-card);
  border-radius: 0 14px 14px 0;
  padding: 16px 20px;
  margin-bottom: 12px;
}}
.bb-policy-block {{ border-left-color: var(--bb-red); }}
.bb-policy-approval {{ border-left-color: var(--bb-amber); }}
.bb-policy-allow {{ border-left-color: var(--bb-green); }}
.bb-policy-warn {{ border-left-color: var(--bb-cyan); }}

/* ═══════════════ DASHBOARD METRICS ═══════════════ */
.bb-dash-metrics {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}}
.bb-dash-metric {{
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--bb-border-glass);
  border-radius: 12px;
  padding: 18px;
}}
.bb-dash-metric-value {{
  font-family: var(--font-serif) !important;
  font-size: 30px !important;
  font-weight: 400 !important;
  color: var(--bb-ink) !important;
  line-height: 1 !important;
}}
.bb-dash-metric-label {{
  font-family: var(--font-sans) !important;
  font-size: 11px !important;
  font-weight: 500 !important;
  color: var(--bb-ink-muted) !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 6px;
}}
.bb-dash-metric-delta {{
  font-family: var(--font-mono) !important;
  font-size: 11px !important;
  color: var(--bb-green) !important;
  margin-top: 6px;
}}
.bb-activity-item {{
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--bb-border-glass);
  font-size: 13px;
  color: var(--bb-ink-secondary);
}}
.bb-activity-badge {{
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 2px 8px;
  border-radius: 6px;
  color: var(--bb-ink-secondary);
  background: rgba(255,255,255,0.04);
  flex-shrink: 0;
}}
.bb-activity-time {{
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--bb-ink-muted);
  flex-shrink: 0;
  min-width: 56px;
}}

/* ═══════════════ CTA / FOOTER ═══════════════ */
.bb-cta {{
  max-width: var(--max-w);
  margin: 0 auto;
  padding: clamp(80px, 14vh, 140px) var(--px) clamp(80px, 14vh, 140px);
  text-align: center;
}}
.bb-cta-title {{
  font-family: var(--font-serif) !important;
  font-size: clamp(38px, 5.5vw, 60px) !important;
  line-height: 1.1 !important;
  letter-spacing: -0.035em !important;
  font-weight: 400 !important;
  color: var(--bb-ink) !important;
  max-width: 780px;
  margin: 0 auto 22px !important;
  padding: 0 !important;
}}
.bb-cta-sub {{
  font-family: var(--font-sans) !important;
  font-size: 16px !important;
  color: var(--bb-ink-secondary) !important;
  max-width: 520px;
  line-height: 1.5 !important;
  margin: 0 auto 32px !important;
}}
.bb-footer {{
  max-width: var(--max-w);
  margin: 0 auto;
  padding: 40px var(--px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid var(--bb-border-glass);
}}
.bb-footer-links {{
  display: flex;
  gap: 24px;
  list-style: none;
  margin: 0;
  padding: 0;
}}
.bb-footer-links a {{
  font-size: 14px;
  color: var(--bb-ink-muted);
  text-decoration: none;
  transition: color 0.15s;
}}
.bb-footer-links a:hover {{ color: var(--bb-ink); }}

/* ═══════════════ ANIMATIONS (CSS-only — works in Streamlit) ═══════════════ */
@keyframes bb-fade-up {{
  0%   {{ opacity: 0; transform: translateY(28px); }}
  100% {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes bb-fade-in {{
  0%   {{ opacity: 0; }}
  100% {{ opacity: 1; }}
}}
@keyframes bb-pulse-recording {{
  0%, 100% {{ opacity: 1; }}
  50%      {{ opacity: 0.4; }}
}}

/* stagger via nth-of-type on timeline items (Streamlit-safe — targets .bb-timeline-item directly) */
.bb-timeline-item:nth-of-type(1)  {{ animation: bb-fade-up 0.55s var(--ease-out-expo) 0.03s both; }}
.bb-timeline-item:nth-of-type(2)  {{ animation: bb-fade-up 0.55s var(--ease-out-expo) 0.09s both; }}
.bb-timeline-item:nth-of-type(3)  {{ animation: bb-fade-up 0.55s var(--ease-out-expo) 0.15s both; }}
.bb-timeline-item:nth-of-type(4)  {{ animation: bb-fade-up 0.55s var(--ease-out-expo) 0.21s both; }}
.bb-timeline-item:nth-of-type(5)  {{ animation: bb-fade-up 0.55s var(--ease-out-expo) 0.27s both; }}
.bb-timeline-item:nth-of-type(6)  {{ animation: bb-fade-up 0.55s var(--ease-out-expo) 0.33s both; }}
.bb-timeline-item:nth-of-type(7)  {{ animation: bb-fade-up 0.55s var(--ease-out-expo) 0.39s both; }}
.bb-timeline-item:nth-of-type(8)  {{ animation: bb-fade-up 0.55s var(--ease-out-expo) 0.45s both; }}
.bb-timeline-item:nth-of-type(9)  {{ animation: bb-fade-up 0.55s var(--ease-out-expo) 0.51s both; }}
.bb-timeline-item:nth-of-type(10) {{ animation: bb-fade-up 0.55s var(--ease-out-expo) 0.57s both; }}

.bb-recording-dot {{
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--bb-green);
  box-shadow: 0 0 8px var(--bb-green);
  animation: bb-pulse-recording 2s ease-in-out infinite;
}}

/* floating animation for the dark section */
@keyframes bb-float {{
  0%, 100% {{ transform: translateY(0px); }}
  50%      {{ transform: translateY(-6px); }}
}}

/* ═══════════════ TABS ═══════════════ */
div[data-testid="stTabs"] button {{
  font-family: var(--font-sans) !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  color: var(--bb-ink-muted) !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0 !important;
  transition: color 0.15s, border-color 0.15s;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
  color: var(--bb-ink) !important;
  border-bottom-color: var(--bb-green) !important;
}}
div[data-testid="stTabs"] button:hover {{
  color: var(--bb-ink) !important;
}}
div[data-testid="stTabs"] [data-testid="stTabContent"] {{
  padding-top: 16px;
}}

/* ═══════════════ CODE BLOCKS ═══════════════ */
.stCodeBlock {{
  border-radius: 12px !important;
  border: 1px solid var(--bb-border-glass) !important;
  background: var(--bb-bg-elevated) !important;
}}

/* ═══════════════ STREAMLIT OVERRIDES ═══════════════ */
div.stButton > button:first-child {{
  border-radius: 9999px !important;
  border: none !important;
  background: var(--bb-ink) !important;
  color: var(--bb-void) !important;
  font-family: var(--font-sans) !important;
  font-weight: 500 !important;
  font-size: 14px !important;
  padding: 12.5px 24.5px !important;
  transition: opacity 0.15s, transform 0.2s var(--ease-spring);
}}
div.stButton > button:first-child:hover {{
  opacity: 0.9 !important;
  transform: scale(1.03) !important;
  border: none !important;
  color: var(--bb-void) !important;
}}

/* ═══════════════ RESPONSIVE ═══════════════ */
@media (max-width: 900px) {{
  .bb-dash-metrics {{ grid-template-columns: repeat(2, 1fr); }}
}}
@media (max-width: 600px) {{
  .bb-dash-metrics {{ grid-template-columns: 1fr; }}
  .bb-nav {{ padding: 16px 20px 0; height: 60px; }}
  .bb-section-hero {{ padding: 60px 20px 40px; }}
}}
</style>
"""
