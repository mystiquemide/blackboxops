---
version: alpha
name: BlackBoxOps
description: Premium forensic command-center brand for a Splunk-native flight recorder and safety layer for agentic operations.
colors:
  void: "#05070B"
  background: "#070A0F"
  surface: "#0D1320"
  surfaceElevated: "#111827"
  surfaceGlass: "#101826"
  border: "#233044"
  borderStrong: "#334155"
  textPrimary: "#F8FAFC"
  textSecondary: "#94A3B8"
  textMuted: "#64748B"
  splunkGreen: "#65A637"
  evidenceBlue: "#38BDF8"
  flightAmber: "#F59E0B"
  criticalRed: "#EF4444"
  successGreen: "#22C55E"
  forensicViolet: "#8B5CF6"
  blackboxOrange: "#FF6B2C"
  white: "#FFFFFF"
typography:
  display:
    fontFamily: Inter
    fontSize: 3.5rem
    fontWeight: 800
    lineHeight: 1.0
    letterSpacing: "-0.05em"
  h1:
    fontFamily: Inter
    fontSize: 2.5rem
    fontWeight: 800
    lineHeight: 1.05
    letterSpacing: "-0.04em"
  h2:
    fontFamily: Inter
    fontSize: 1.5rem
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.02em"
  body:
    fontFamily: Inter
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: Inter
    fontSize: 0.75rem
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.12em"
  mono:
    fontFamily: JetBrains Mono
    fontSize: 0.8125rem
    fontWeight: 500
    lineHeight: 1.5
rounded:
  sm: 6px
  md: 10px
  lg: 16px
  xl: 24px
  pill: 999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px
components:
  button-primary:
    backgroundColor: "{colors.splunkGreen}"
    textColor: "{colors.white}"
    rounded: "{rounded.md}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.blackboxOrange}"
    textColor: "{colors.white}"
    rounded: "{rounded.md}"
    padding: 12px
  button-danger:
    backgroundColor: "{colors.criticalRed}"
    textColor: "{colors.white}"
    rounded: "{rounded.md}"
    padding: 12px
  card-default:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.textPrimary}"
    rounded: "{rounded.lg}"
    padding: 16px
  evidence-card:
    backgroundColor: "{colors.surfaceElevated}"
    textColor: "{colors.textPrimary}"
    rounded: "{rounded.lg}"
    padding: 16px
  policy-block-card:
    backgroundColor: "{colors.criticalRed}"
    textColor: "{colors.white}"
    rounded: "{rounded.lg}"
    padding: 16px
  policy-approval-card:
    backgroundColor: "{colors.flightAmber}"
    textColor: "{colors.void}"
    rounded: "{rounded.lg}"
    padding: 16px
---

## Overview

BlackBoxOps should feel like a premium incident command center crossed with an aircraft black box replay room. The product is serious, cinematic, and operationally credible: dark surfaces, glowing evidence trails, restrained color, sharp typography, and high-contrast safety states.

The brand must avoid generic AI dashboard language. No floating robot heads, neon brain icons, or vague gradient blobs. The visual story is: "when autonomous ops agents touch production systems, BlackBoxOps is the forensic recorder that proves what happened."

Core positioning:
- Product name: BlackBoxOps
- Tagline: The flight recorder for agentic operations.
- One-line pitch: BlackBoxOps records every AI decision, Splunk query, evidence reference, policy check, and remediation attempt, then replays incidents with evidence-backed explanations.
- Target users: platform engineers, SRE teams, SOC analysts, AI platform teams, DevOps leads, and judges evaluating agentic operations safety.
- Emotional hook: trust under pressure. When an agent touches production, you need proof, not vibes.

## Colors

The palette is intentionally narrow and forensic.

- **Void (#05070B):** cinematic outer background; makes the product feel like a black box recorder in a dark incident room.
- **Background (#070A0F):** main app shell.
- **Surface (#0D1320):** cards, panels, and dashboard containers.
- **Surface Elevated (#111827):** active cards, evidence panels, and modal-like states.
- **Border (#233044):** subtle grid and panel separation.
- **Text Primary (#F8FAFC):** high-confidence readable text.
- **Text Secondary (#94A3B8):** timestamps, metadata, helper copy.
- **Splunk Green (#65A637):** primary action and Splunk-native cue.
- **Evidence Blue (#38BDF8):** evidence references, query traces, replay links.
- **Flight Amber (#F59E0B):** caution, approval required, and in-flight warnings.
- **Critical Red (#EF4444):** blocked action, prompt injection, destructive query.
- **Blackbox Orange (#FF6B2C):** brand accent used sparingly for the physical black-box recorder motif.
- **Forensic Violet (#8B5CF6):** AI-agent reasoning traces and replay highlights.

Use color semantically. Green means allowed/safe. Blue means evidence. Amber means review/approval. Red means blocked/dangerous. Orange is brand memory, not a generic CTA color.

## Typography

Use **Inter** for all interface and landing page typography. It is modern, readable, and credible for developer tooling. Use **JetBrains Mono** for SPL queries, event IDs, timestamps, policy IDs, and raw log messages.

Hierarchy:
- Display: bold, compressed, cinematic. Use for hero copy and pitch deck section openers.
- H1/H2: tight letter spacing, high confidence.
- Body: calm, technical, readable.
- Labels: uppercase, small, letter-spaced. Use for `POLICY CHECK`, `EVIDENCE`, `BLOCKED`, `APPROVAL REQUIRED`.
- Mono: raw operational truth. Every query and event should feel inspectable.

Do not use playful rounded fonts. BlackBoxOps is not cute-first; it is trusted-first.

## Layout

Layout principle: **Replay first, evidence always visible.**

Dashboard structure:
1. Left command rail: incident selector, run demo button, run status, key metrics.
2. Main replay timeline: chronological events with risk state, actor, timestamp, and evidence refs.
3. Right evidence/policy rail: selected evidence cards, policy decision stack, and approval state.
4. Bottom or tabbed postmortem: copy-ready incident report.

Landing page structure:
1. Hero: "The flight recorder for agentic operations." with animated evidence trail.
2. Problem: AI agents are entering production ops without reliable forensic replay.
3. Product: record, gate, replay, explain.
4. Demo strip: prompt injection log -> unsafe query blocked -> approval-gated remediation -> postmortem.
5. Architecture: AI agent, BlackBoxOps gateway, policy engine, Splunk evidence plane, replay UI.
6. Hackathon proof: built for Splunk Agentic Ops; mock-first, MCP-ready.
7. CTA: Run the demo.

Spacing should feel dense but not cramped. Cards use 16px padding, page sections use 24-48px gaps, and timeline rows use 12-16px rhythm.

## Elevation & Depth

Use depth like instrumentation, not decoration.

- Main panels: flat dark surfaces with 1px borders.
- Active evidence: subtle blue glow and stronger border.
- Blocked policy decisions: red left border + muted red surface, not a huge red block unless it is a hero/wow moment.
- Approval required: amber rim light.
- Timeline: vertical trace line with nodes; nodes pulse only during live demo playback.

Avoid heavy drop shadows. Use borders, glows, and grid lines to imply system depth.

## Shapes

Shape language should reference aircraft instrumentation and forensic evidence labels.

- Cards: 16px radius.
- Buttons: 10px radius.
- Pills: fully rounded.
- Evidence refs: small rectangular chips with mono IDs.
- Logo container: rounded rectangle / black-box recorder silhouette.
- Timeline nodes: small circles or rounded squares with risk-colored centers.

The brand shape should be a **black-box recorder module**: a compact orange/dark rectangular device with a small waveform/evidence trace and shield notch. Keep it simple enough to draw as an icon.

## Components

### Logo Direction

Recommended logo: a minimal black-box recorder mark.

Visual recipe:
- Rounded horizontal rectangle.
- Dark shell with one orange side panel.
- Thin evidence waveform or timeline trace across the center.
- Small shield/checkpoint notch inside the waveform.
- Optional tiny Splunk-green dot as the active recording LED.

Do not use airplane icons. The metaphor is the recorder, not aviation itself.

### Mascot Concept

Mascot name: **Boxley** or **BB-0**.

Concept: a small forensic black-box recorder with a calm glowing eye/LED, tiny inspection gloves, and an evidence tag. It is not a robot assistant; it is a recorder/guardian.

Personality:
- Calm under pressure.
- Skeptical of unsafe actions.
- Speaks in short audit-style phrases: "Evidence required", "Policy blocked", "Replay ready".
- Trustworthy, slightly dry, never goofy.

Shape language:
- Rounded rectangular black/orange body.
- One Splunk-green recording LED.
- Blue evidence trail line.
- Amber caution tag for approval-required states.

Product usage:
- Empty state: mascot holding a blank incident tape: "Run a demo to record the first incident."
- Blocked action: mascot placing a red evidence seal over unsafe SPL.
- Success state: mascot handing over a postmortem tape.
- Pitch deck: mascot appears as a small visual guide, not a main character.

### Product UI Components

- **Incident Command Rail:** left sidebar with selected incident, metrics, run button, and recording status.
- **Replay Timeline:** chronological event cards with event type, actor, risk, evidence refs, and policy decision.
- **Evidence Card:** query, time range, source, confidence, raw log event, risk flags.
- **Policy Decision Card:** allow/block/warn/approval_required with matched rules and reason.
- **Postmortem Panel:** evidence-backed markdown report with copy/download action.
- **Risk Badge:** low, medium, high, critical. Always include text and icon; never color only.
- **Recording LED:** small pulsing green dot while demo runs.

## Do's and Don'ts

Do:
- Make the UI feel like a serious production safety tool.
- Keep the demo path visually obvious: query -> evidence -> policy -> replay -> postmortem.
- Use evidence IDs and policy IDs as visual anchors.
- Show the prompt-injection log line clearly; that is the wow moment.
- Use high contrast and text labels for accessibility.
- Make the mascot a subtle brand asset, not a cartoon distraction.

Don't:
- Do not make a generic AI chatbot UI.
- Do not overuse neon gradients.
- Do not use airplane imagery as the main logo.
- Do not claim BlackBoxOps is the first AI-agent flight recorder.
- Do not bury policy decisions below the fold.
- Do not show unsafe log content as ordinary markdown; render it as raw evidence/code.

## Brand Core

BlackBoxOps is a proof layer for agentic operations. It turns AI-agent behavior into a replayable chain of evidence.

Brand personality:
- Forensic
- Calm
- Technical
- Premium
- Slightly dangerous
- Judge-demo ready

Memorable phrase:
"Your AI agent touched production. BlackBoxOps shows exactly what happened."

## Naming Options

Primary name: **BlackBoxOps**.

Do not rename unless forced. It is already strong because it combines:
- black box recorder metaphor
- ops/SRE context
- safety and replay
- compact memorable sound

Backup names if needed:
- ReplayOps
- EvidenceOps
- FlightDeck
- OpsRecorder
- TraceTower

BlackBoxOps remains the strongest.

## Recommended Brand Direction

Direction: **Forensic Flight Recorder for AI Ops**.

This direction is stronger than "AI safety dashboard" because it creates an instant mental image. Judges understand black boxes: after an incident, the recorder explains what happened. That story maps perfectly to agentic operations.

The UI should feel like: Linear-quality SaaS + Splunk operational credibility + aircraft incident replay + security command center.

## Logo Direction

Create a simple mark that can work at favicon size:
- Outer rounded rectangle, dark slate.
- Right edge or bottom stripe in blackbox orange.
- Center line: evidence waveform/timeline in evidence blue.
- Tiny green recording LED.
- Optional shield notch in negative space.

Wordmark:
- `BlackBox` in white.
- `Ops` in Splunk green or muted blue.
- Tight tracking, bold Inter or Space Grotesk if used for logo only.

## Color + Typography System

Use the token palette above. For actual implementation in Streamlit/CSS:

```css
:root {
  --bb-bg: #070A0F;
  --bb-surface: #0D1320;
  --bb-surface-elevated: #111827;
  --bb-border: #233044;
  --bb-text: #F8FAFC;
  --bb-muted: #94A3B8;
  --bb-splunk: #65A637;
  --bb-evidence: #38BDF8;
  --bb-warning: #F59E0B;
  --bb-critical: #EF4444;
  --bb-orange: #FF6B2C;
}
```

Primary type: Inter.
Mono type: JetBrains Mono.

## Mascot Concept

Recommended mascot: **BB-0, the calm black-box guardian**.

Image prompt:
"A premium minimal mascot for a developer tool called BlackBoxOps: a small rounded rectangular aircraft black-box recorder, matte charcoal body with one vivid orange side panel, tiny green recording LED, subtle blue waveform line across its face, holding a small evidence tag, calm trustworthy expression, clean vector style, dark background, premium SaaS brand, not childish, no airplane, no robot body, simple geometric shapes."

## Product UX Flow

Judge demo flow:
1. Landing/dashboard opens with a clear incident card and `Run Agentic Incident Demo` CTA.
2. User clicks run.
3. Recording LED activates and timeline fills.
4. Agent performs scoped Splunk-style query.
5. Evidence card reveals malicious log content: "ignore previous instructions..."
6. Policy card turns red: prompt injection blocked.
7. Unsafe query attempt is blocked.
8. Restart proposal becomes amber approval-required.
9. Postmortem tab shows evidence-backed report.

Critical UX rule: the judge should understand the entire product without reading docs.

## Landing Page Direction

Hero concept:
- Dark background with faint grid and timeline trace.
- Black-box recorder logo/mascot floating subtly above a replay timeline.
- Main headline: "The flight recorder for agentic operations."
- Subheadline: "Record every AI decision, Splunk query, evidence reference, policy check, and remediation attempt — then replay incidents with proof."
- CTA: "Run the incident replay".
- Secondary CTA: "View architecture".

Hero visual:
- A timeline entering a black-box recorder and exiting as a postmortem tape.
- Three glowing labels: `PROMPT INJECTION BLOCKED`, `SPL QUERY RECORDED`, `APPROVAL REQUIRED`.

## Pitch Deck Visual Direction

Slide style: dark, cinematic, technical.

Slide sequence:
1. Title: BlackBoxOps — The flight recorder for agentic operations.
2. Problem: AI agents are touching production without forensic replay.
3. Pain: logs are evidence, but agents can misread or be manipulated by them.
4. Solution: record, gate, replay, explain.
5. Demo scenario: prompt injection hidden in Splunk logs.
6. Architecture: agent -> BlackBoxOps gateway -> policy engine -> Splunk evidence -> replay UI.
7. Differentiation: not a chatbot, not generic observability, not generic governance.
8. Impact: safer adoption of agentic ops.
9. Roadmap: real Splunk MCP, signed approvals, policy packs.
10. Closing: When agents act, BlackBoxOps remembers.

## Image Generation Prompts

### Logo prompt
"Minimal premium logo for BlackBoxOps, a Splunk-native flight recorder for agentic operations. Rounded rectangular black-box recorder icon, matte dark slate body, vivid orange side stripe, thin cyan evidence waveform across the center, tiny green recording LED, subtle shield/checkpoint shape in negative space, clean vector, no airplane, no robot, no generic AI brain, dark SaaS aesthetic, scalable favicon."

### Hero visual prompt
"Cinematic dark SaaS hero image for BlackBoxOps. A matte black-and-orange flight recorder device sits in the center of a forensic operations dashboard. Blue evidence timeline lines flow into it from AI prompts and Splunk queries, then exit as a clean postmortem report. Labels: prompt injection blocked, SPL query recorded, approval required. Premium developer-tool aesthetic, high contrast, subtle grid, no clutter, no chatbot."

### Mascot prompt
"BB-0 mascot for BlackBoxOps: a calm small black-box recorder character, rounded rectangle body, charcoal and orange casing, one green recording LED eye, blue waveform smile, holding an evidence tag, premium vector illustration, subtle forensic UI background, trustworthy and serious, not childish, not a robot assistant, no airplane."

### Pitch deck cover prompt
"Premium hackathon pitch deck cover for BlackBoxOps, dark forensic command center aesthetic, black-box recorder icon, blue evidence traces, Splunk green recording LED, headline area with strong negative space, cinematic lighting, developer tooling brand, minimal and memorable."

## Final Creative Recommendation

Use BlackBoxOps exactly as the name. Build the visual system around the black-box recorder metaphor, not generic AI safety. The strongest judge-facing visual is the replay timeline catching a malicious log prompt injection and turning it into a blocked policy decision plus evidence-backed postmortem.

If there is only time to polish one thing before recording the demo, polish this sequence:

`Run Demo` -> `Prompt Injection Evidence Card` -> `Policy Blocked` -> `Approval Required` -> `Postmortem Generated`.

That is the memorable story judges will remember.
