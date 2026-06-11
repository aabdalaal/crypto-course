# CLAUDE.md — Crypto-Course App

Engineer-facing reference. Terse and prescriptive. Read this before touching any code.

Detailed rule files live under `.claude/rules/` and are auto-loaded by Claude Code:

| Rule file | Contents |
|-----------|----------|
| `project-overview.md` | What the app is, target users, research paper context |
| `pedagogical-requirements.md` | PR1–PR14 with acceptance criteria and implementation notes |
| `technical-requirements.md` | R1–R17 grouped by 6 digital exclusion nexus dimensions |
| `pedagogical-theory.md` | Five learning theories underpinning all UX/content decisions |
| `gamification-rationale.md` | Seven gamification mechanics and the critical PR9 constraint |
| `architecture.md` | Single-file SPA+PWA structure, navigation, state, localStorage keys |
| `curriculum-structure.md` | 14 CyBOK-aligned modules and the 7-stage lesson template (PR3) |
| `phase-features.md` | Phase 2 tiered questions, Phase 3 spaced repetition, Phase 4 adaptive difficulty |
| `interactive-labs.md` | Lab IDs, modules, purposes, and the PR8 no-network constraint |
| `gamification-system.md` | XP levels, badges, streak/freeze tokens, CipherPulse daily challenge |
| `auth-rbac.md` | Roles, elevation codes, demo credentials, prototype security limitations |
| `admin-panel.md` | Admin/teacher panel tabs and role requirements |
| `ai-pipeline.md` | AI content automation job types and output shapes |
| `xapi-telemetry.md` | xAPI events and the PR13 6-field sync payload constraint |
| `css-design-system.md` | Design tokens, typography, reusable CSS classes |
| `key-functions.md` | Reference table of all key functions |
| `adding-content.md` | Checklist for adding modules and badges |
| `known-limitations.md` | Prototype limitations |
| `file-asset-map.md` | Complete file and asset map |

---

## CRITICAL TECHNICAL RULES

> These rules are hard constraints. Follow them exactly.

### 1. SINGLE FILE ONLY

Never suggest splitting `index.html`. The single-file architecture is a **deliberate offline-first design constraint**, not a limitation to work around. Target deployment is USB distribution, WhatsApp file sharing, and environments with no build toolchain. The file is currently ~21,712 lines / ~1.27 MB.

### 2. TEMPLATE LITERAL SAFETY

All lesson body strings (`MODULES[n].content.stage*.body`) are JavaScript template literals. Any backtick character inside lesson body content **MUST** use `<code>backtick</code>` HTML — **never a raw backtick**.

- The total backtick count in `index.html` must remain **even** at all times.
- Current count: **1,702 (even ✓)**
- Every implementation session must end with a verification script that checks all changed items and confirms backtick parity.

```js
// WRONG — breaks the template literal
body: `Use the \`openssl\` command...`

// CORRECT
body: `Use the <code>openssl</code> command...`
```

### 3. NEVER IMPLEMENT WITHOUT CONFIRMATION

Default to **"think with me, do not implement"** for any design decision. Present a summary of proposed changes and wait for explicit confirmation before writing code.

### 4. OUTPUT LOCATION

All outputs go to `/mnt/user-data/outputs/`. All deliverables must be paste-ready and complete — no placeholders or stubs.

### 5. READ THE SKILL FILE FIRST

Before creating any file type (docx, xlsx, pptx, pdf, HTML), read the relevant `SKILL.md` file.

### 6. WORK IN PHASES

Audit → Implementation → Verification. Every implementation session ends with a verification script that checks all changed items and confirms backtick parity.

---

## ARCHITECTURE

### File Structure

```
index.html          — entire application (~21,712 lines, ~1.27 MB)
sw.js               — service worker (cache-first HTML, network-first fonts)
manifest.json       — PWA manifest (name: CryptoCourse, theme: #0F172A)
```

### State Model

```js
let state = {
  // Core gamification
  xp, streak, freezeTokens,
  lessonsCompleted, quizzesCompleted, perfectQuizzes, labsCompleted,
  moduleProgress: {},          // { moduleId: completionFraction }
  badges: [],

  // Accessibility / i18n
  language, highContrast, textSize, reduceAnim,

  // Sync & quiz analytics
  lastSync,
  quizAttempts: {},

  // Navigation persistence
  currentLesson: { moduleId, stage },

  // Daily challenge
  lastChallengeDate, diagnosticDone, diagDismissed,

  // Social
  leaderboardOptIn,

  // Announcements
  readAnnouncements: [], semesterId,

  // Phase 3 — Spaced repetition
  spacedRevisits: {},
  // { moduleId: { completedAt, nextRevisit7, nextRevisit14, revisitsDone, lastQuestionText } }

  // DBR Cycle 1 additions
  diagnosticScore: null,       // 0-100 integer, saved after diagnostic (PR12)
  bypassedModules: [],         // module IDs bypassed via diagnostic
  researchMode: false,         // admin toggle for NASA-TLX instrument (PR3)
  moduleTimes: {},             // { moduleId: firstCompletionMs } for PR1
  nasaTLX: {},                 // { moduleId: [{md,pd,td,perf,ef,fr,ts}] } (PR3)
};
```

Persisted to localStorage via `saveState()` / `loadUserState()`. Per-user key: `crypto_course_state_{userId}`.

### Screen Navigation

`navigate(screenName)` controls which `<div class="screen" id="screen-{name}">` is active. All render functions (`renderHome`, `renderModules`, `renderProgress`, `renderProfile`, `renderAdmin`) are called by `navigate()`.

### i18n

```js
const i18n = { en: {...}, ar: {...} }
// t(key) resolves the current language
// setLanguage(lang) sets dir="rtl" on <html>
//   AND calls navigate(currentScreen) to re-render all dynamic content
```

### Admin Tabs

`dashboard, analytics, groups, badges, content, ai, cipherpulse, research`

The **Research tab** (added Cycle 1) contains:
- Research Mode toggle (enables NASA-TLX after module completion)
- PR1 completion time table with per-module bar charts
- PR3 NASA-TLX aggregate view (`state.nasaTLX`)
- PR13 payload inspector
- PR5 performance panel (`measurePR5()`)
- PR9/PR10 integration test runner (`runPR9PR10Tests()`)

### Sequential Module Unlock

```js
seqLocked = m.id > 1
  && !(state.moduleProgress[m.id - 1] >= 0.5)
  && !_bypassedSet.has(m.id - 1);
// _bypassedSet derived from state.bypassedModules on every render
```

### Spaced Repetition

`buildRevisitPool()` assembles 6-8 questions per module. `startRevisitQuiz()` filters the 14-day pool to exclude the question shown at 7 days, stored in `state.spacedRevisits[modId].lastQuestionText`.

---

## DAILY_MCQ_BANK SCHEMA

37 entries. Schema:

```js
{
  moduleId: 0,           // links to MODULES[n]
  tier: 'core',          // 'core' | 'consol' | 'boost'
  topic: 'Caesar Cipher',
  question: '...',
  options: [
    { t: 'Option text', c: true },   // c: true = correct
    { t: 'Option text', c: false },
  ],
  hint: '...',
  explanation: '...',    // shown after submit
  concept: 'Caesar Cipher — Module 0',  // format: 'Topic — Module N'
  xp: 5,
}
```

All 37 entries have the `concept` field (added Cycle 1). The MCQ feedback renderer shows: answer state → explanation → `Revisit: concept` on submit and on `mcqDone` restore.

---

## THE SECRET CHANNEL — PRODUCTION RULES

12-episode cryptography drama. Tagline: *"You cannot love someone you cannot verify."*
Characters: Alice, Bob, Eve, Mallory.

**Multi-clip shots:** Use an identical location description block in every prompt for a given scene — prevents scene drift. The Alice library scene is the canonical template.

**Voiceover pacing:** ~2.17 words per second. Lines longer than shot duration must be trimmed before recording.

**Voiceover register:** Confessional, interior monologue.

**Character image prompts:** Must reflect wide cultural and demographic diversity.

**Output format:** MP4 H.264 1080x1920 24 fps (9:16 portrait).

---

## PR COMPLIANCE — QUICK REFERENCE

| PR | Status | Key implementation |
|----|--------|--------------------|
| PR1 | Done | `state.moduleTimes`, Research tab bar charts |
| PR2 | Done | By design — `level` field, concept-boxes in every stage |
| PR3 | Done | `showNasaTLX()`, `state.nasaTLX`, Research tab aggregate |
| PR4 | Done | All 125 module questions + all 37 MCQ bank entries: why + concept |
| PR5 | Done | Research tab `measurePR5()` panel |
| PR6 | Done | All 14 modules: pool depth 6-8, cross-revisit deduplication |
| PR7 | Done | `--muted` #64748B, focus rings, ARIA progressbar |
| PR8 | Done | Web Crypto API only, zero network calls in labs |
| PR9 | Done | `runPR9PR10Tests()` in Research tab |
| PR10 | Done | `runPR9PR10Tests()` in Research tab |
| PR11 | Done | RTL CSS block (55 lines), `setLanguage()` re-renders, 5 new i18n keys |
| PR12 | Done | `applyBypassAndStart()`, `_bypassedSet`, 70% threshold |
| PR13 | Done | Payload inspector in Research tab, 6-field hard limit |
| PR14 | Done | By design — content registry enables incremental updates |

**Before changing any gamification mechanic:** verify PR9 — connectivity failure must never reduce learner standing.

**Before adding sync fields:** verify PR13 — 6-field hard limit, no free-text / device ID / geolocation.
