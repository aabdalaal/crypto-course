---
description: PR1–PR14 — the 14 formal, falsifiable pedagogical requirements that drive every design decision. Do not remove a feature without checking which PR it satisfies.
alwaysApply: true
---

These are the formal specifications from Paper 3. **Do not remove a feature without checking which PR it satisfies.**

| PR | Cluster | Requirement | Acceptance Criterion | Implementation |
|----|---------|-------------|---------------------|----------------|
| PR1 | Instructional Structure | Modules completable in ≤20 min per session | Mean completion ≤20 min across ≥20 participants | 7-stage module structure; ~10–15 min design target |
| PR2 | Instructional Structure | 4-level difficulty taxonomy (Introductory→Advanced); strict ascending sequence; ≥1 scaffolding element per stage | All modules classified; scaffolding present at every stage | `level` field on every module; concept-boxes and worked examples in lesson HTML |
| PR3 | Instructional Structure | Identical 7-stage structure across all modules; NASA-TLX ≤50/100 | Consistent stage structure; empirical cognitive load testing | Every module: stage1–stage7 template; identical UI flow |
| PR4 | Feedback & Interaction | Every incorrect quiz response triggers: (a) why wrong, (b) correct answer, (c) concept reference | All three components present in every quiz item | `why` and `concept` fields on every quiz question |
| PR5 | Feedback & Interaction | All interactive components: ≤300MB active memory; initial load ≤3s on reference device | Verified by Chrome DevTools on 2GB RAM Android | Single HTML file; no heavy frameworks; Web Crypto API only |
| PR6 | Navigation & Independence | ≥80% of participants complete a full module without external help | Task completion rate in usability testing | Self-contained modules with full in-app explanations |
| PR7 | Accessibility & Inclusion | WCAG 2.1 AA compliance; TalkBack compatible | axe-core audit + manual TalkBack testing | ARIA labels, semantic HTML, focus management, role attributes |
| PR8 | Feedback & Interaction | ≥1 on-device cryptographic lab per module; no lab requires server contact | Zero server requests during offline lab execution | `renderLab()` uses Web Crypto API exclusively; no network calls |
| PR9 | Motivation & Continuity | No mechanic reduces XP/badges/streak due to connectivity/power outage; ≥1 freeze token per 7 days | Zero standing reductions from simulated outage events | `freezeTokens` in state; freeze token confirmation sheet; auto-award 1 token/7 days |
| PR10 | Motivation & Continuity | All state persisted after every interaction; exact position restored on relaunch | Correct restoration after simulated termination at all 7 stages | `saveState()` called after every XP award, quiz answer, lab completion, nav event |
| PR11 | Accessibility & Inclusion | Full interface renders correctly in Arabic (RTL) | Native Arabic-speaker review; automated bidirectional rendering tests | `dir="rtl"` on `<html>`; `setLanguage('ar')` flips nav labels; AI pipeline generates Arabic module translations |
| PR12 | Navigation & Independence | Diagnostic entry assessment (≤10 items); ≥70% score → bypass Introductory modules | Bypass offered correctly; beginners routed to Module 1 | `diagnosticQuestions` (10 items); `state.diagnosticDone`; 70% threshold → `startAtModule(2)` |
| PR13 | Privacy & Infrastructure | Sync payload ≤6 fields: XP delta, streak, badge timestamps, quiz outcome flags, lab completions, session duration. No free-text, device ID, geolocation, or behavioural sequences | Network traffic inspection confirms no prohibited fields | `triggerSync()` payload hardcoded to 6 fields; noted in code comment |
| PR14 | Privacy & Infrastructure | Content updates ≤500MB/sync window; incremental; no interruption of active sessions | Payload measurement across 3 update scenarios | Content registry (`CONTENT_REGISTRY_KEY`) enables incremental module updates |
