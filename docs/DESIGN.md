# DESIGN — BlackBoxOps

## Design Direction
Dark, forensic, operational. The UI should feel like a production incident command center plus aircraft black box replay.

## Design System

Colors:
- Background: #070A0F
- Surface: #0F172A
- Surface elevated: #111827
- Border: #233044
- Text primary: #F8FAFC
- Text secondary: #94A3B8
- Splunk green accent: #65A637
- Evidence blue: #38BDF8
- Warning amber: #F59E0B
- Critical red: #EF4444
- Success green: #22C55E
- Muted purple: #8B5CF6

Typography:
- Title: 28-36px, bold
- Section header: 18-22px, semibold
- Body: 14-16px
- Mono/event text: 12-14px monospace

Spacing:
- Page padding: 24px
- Card padding: 16px
- Grid gap: 16px
- Timeline gap: 12px

Radius:
- Cards: 14px
- Pills: 999px
- Buttons: 10px

## Component Library

IncidentSelector:
- Props: incidents, selected_id, on_select
- States: loading, empty, selected, error
- Purpose: choose demo incident.

DemoRunButton:
- Props: on_run, loading
- States: idle, running, completed, failed
- Copy: “Run Agentic Incident Demo”

RiskBadge:
- Props: level = low | medium | high | critical
- Variants: low green, medium blue/amber, high amber, critical red

PolicyDecisionCard:
- Props: status, reason, matched_rules, required_approval
- Variants: allow, warn, approval_required, block

EvidenceCard:
- Props: query, time_range, sample_event, confidence, risk_flags
- Behavior: collapsed by default, expand to show raw event JSON.

ReplayTimeline:
- Props: events[]
- Renders chronological event cards with icons for prompt, SPL query, evidence, policy check, action proposal, approval, remediation result.

PostmortemPanel:
- Props: markdown
- Actions: copy, download .md

## Screen Specs

Screen 1: Dashboard / Replay
- Top header: BlackBoxOps + tagline + status pills.
- Left sidebar: IncidentSelector + DemoRunButton + key metrics.
- Main area: ReplayTimeline.
- Right panel: PolicyDecisionCard stack + EvidenceCard stack.
- Bottom/tab area: PostmortemPanel.

Header copy:
“Flight recorder for agentic operations. Every AI decision. Every Splunk query. Every policy check. Replayed with evidence.”

Screen 2: Postmortem View
- Incident summary card
- Timeline summary
- Evidence-backed claims
- Policy decisions
- Recommended controls

## User Flows

Judge live demo flow:
1. User clicks “Run Agentic Incident Demo.”
2. Timeline populates step-by-step.
3. Risky log/prompt-injection event is highlighted.
4. Policy engine blocks/approval-gates unsafe action.
5. User opens evidence card showing Splunk query + event.
6. User opens postmortem.

Platform engineer audit flow:
1. Select incident.
2. Filter timeline by policy_check/action_proposal.
3. Inspect blocked decision.
4. Copy postmortem.

## Responsive Rules

Desktop:
- 3-column layout: sidebar / timeline / evidence.

Tablet:
- 2-column layout: sidebar top, timeline main, evidence below.

Mobile:
- Single column.
- Timeline first, evidence cards accordion.

## Accessibility

- Do not rely on color only; include text labels.
- Ensure contrast for red/green badges.
- Keyboard focus on buttons and expandable cards.
- All raw event JSON in readable monospace blocks.
