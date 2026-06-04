# MEMORY.md — Crypto-Course App

Human-readable project record. Running log of what has been built, what decisions were made, and what comes next. Update this as the project evolves.

---

## Project Identity

**Crypto-Course** is an offline-first, mobile-first cryptography education platform for learners in resource-constrained and conflict-affected environments (Gaza, Lebanon, Ukraine, and similar contexts). It is the implementation artefact of two University of Westminster research papers:

- **Paper 2** — *Designing for the Digital Exclusion Nexus*: technology selection framework
- **Paper 3** — *Pedagogical Design of a Gamified Offline-First Cryptography Learning Platform*: 14 Pedagogical Requirements (PR1–PR14)

**Target device:** Low-end Android (2GB RAM, dual-core, 720p). No assumed connectivity, no assumed instructor presence.

---

## Current State (end of DBR Cycle 1)

| Item | State |
|------|-------|
| `index.html` | ~21,712 lines, ~1.27 MB. Single-file SPA + PWA. |
| `sw.js` | Present. Cache-first strategy for HTML; network-first for fonts. |
| `manifest.json` | Present. Name: CryptoCourse, theme: #0F172A. |
| Backtick audit | CLEAN — 1,586 backticks total (even). Zero raw backticks inside template literal bodies. |
| DBR cycle | Cycle 1 complete. Cycle 2 (field pilot) is next empirical phase. |

---

## PR Compliance Status

### PR1 — Completion-time logging (Done)

- `openModule()` records `lessonState.startTime = Date.now()`
- First-completion duration stored in `state.moduleTimes[moduleId]`
- Visible in admin Research tab with per-module bar charts
- Formal acceptance: mean completion ≤20 min across ≥20 participants (Cycle 2)

### PR2 — Difficulty taxonomy and scaffolding (Done — by design inspection)

- All 14 modules carry a `level` field: Introductory / Foundational / Intermediate / Advanced
- Concept-boxes and worked examples present at every stage
- Strict ascending sequence enforced by sequential unlock

### PR3 — NASA-TLX instrument (Done)

- `NASA_TLX_DIMS` array: 6 dimensions (md, pd, td, perf, ef, fr)
- `showNasaTLX(moduleId)` triggered after module completion when `state.researchMode = true`
- Responses stored in `state.nasaTLX[moduleId][]` with timestamp
- Aggregate view in admin Research tab
- Formal acceptance: NASA-TLX score ≤50/100 (Cycle 2 field testing)

### PR4 — Three-component feedback (Done)

- All 125 MODULES quiz questions: `why` + `concept` fields present
- All 37 DAILY_MCQ_BANK questions: `explanation` + `concept` fields present
- `concept` field added to all 37 MCQ bank entries this cycle
- MCQ feedback renderer shows answer state → explanation → Revisit link after submission

### PR5 — Memory ≤300 MB, load ≤3 s (Done — instrument in place)

- Research tab has `measurePR5()` panel with live performance metrics
- Formal acceptance requires Chrome DevTools on reference Android device (Cycle 2)

### PR6 — Spaced repetition depth (Done)

- All 14 modules: pool depth 6–8 questions (target ≥3)
- Cross-revisit deduplication: 14-day pool excludes 7-day question via `state.spacedRevisits[modId].lastQuestionText`
- `buildRevisitPool()` and `startRevisitQuiz()` handle the full flow

### PR7 — WCAG 2.1 AA (Done for Cycle 1 items)

Changes made this cycle:
- `--muted` colour darkened: #94A3B8 → #64748B (now 4.76:1 on white)
- `.cp-decoded-output.correct` changed to `--secondary-d` (#059669)
- `.tag-amber` uses `--accent-d` (7.09:1) — already compliant
- 3 `outline:none` focus rules replaced with `box-shadow` focus rings
- Global `:focus-visible` rule added (3px solid `--primary`)
- Dark-bg focus ring override for `.home-hero` and `#bottom-nav`
- Lesson progress bar: `role="progressbar"` + `aria-valuenow` added; updated programmatically on stage advance

Remaining (Cycle 2 / external): TalkBack manual testing with native Arabic-speaker.

### PR8 — Web Crypto API labs (Done — by design inspection)

All 10 lab types use Web Crypto API exclusively. Zero server calls during lab execution. Hard constraint — do not modify without re-verifying offline operation.

### PR9 — Streak and freeze mechanics (Done — test runner in place)

- `state.freezeTokens` default 3; 1 token auto-awarded per 7 days
- Confirmation sheet before token use
- Research tab `runPR9PR10Tests()` for integration verification
- Hard constraint: connectivity failure must never reduce learner standing

### PR10 — State persistence and restoration (Done — test runner in place)

- `saveState()` called after every XP award, quiz answer, lab completion, and nav event
- `loadUserState()` restores exact position on relaunch
- Research tab `runPR9PR10Tests()` covers both PR9 and PR10

### PR11 — Arabic RTL interface (Done for Cycle 1 items)

Changes made this cycle:
- Comprehensive `[dir="rtl"]` CSS block (55 lines): border-left/right mirrors for 9 components, margin mirrors, quiz option text-align, toggle slider, list indentation, nav badge
- Arabic font stack declared on `[dir="rtl"]` body
- `setLanguage()` calls `navigate(currentScreen)` for full re-render
- 5 new i18n keys in both `en` and `ar`: `welcome_new`, `both_done_tomorrow`, `course_progress`, `tag_available` / `complete` / `continue` / `assigned` / `skipped`
- `renderHome` uses `t()` for greeting, challenge, course progress
- `renderModules` status tags use `t()`

Remaining: native Arabic-speaker review (Cycle 2).

### PR12 — Diagnostic entry assessment (Done)

- Auto-triggers for new `ROLES.STUDENT` learners via `enterApp()`
- `state.diagnosticScore` persists score (0–100)
- `state.bypassedModules = [0, 1]` set by `applyBypassAndStart()` when score ≥70%
- `applyBypassAndStart()` replaces the earlier direct `startAtModule(2)` call
- Both `seqLocked` and `isLocked` respect `_bypassedSet`
- Score chip rendered in result screen
- Wording: "Introduction to Cryptography and Classical Cryptography bypassed"
- xAPI payload includes `diagnosticScore` and `bypassedModules`
- Sync merge: `diagnosticScore = max`, `bypassedModules = union`

### PR13 — Sync payload ≤6 fields (Done)

- `triggerSync()` payload hardcoded to exactly 6 fields: `xpDelta`, `streak`, `badgeTimestamps`, `quizOutcomes`, `labCompletions`, `sessionDuration`
- PR13 payload inspector in Research tab shows live payload for verification
- No free-text, device ID, or geolocation permitted — hard constraint

### PR14 — Content updates ≤500 MB (Done — by design inspection)

- Content registry (`CONTENT_REGISTRY_KEY`) enables incremental module updates
- No full-file replacement required for content-only changes

---

## Design Decisions Log

### Why a single HTML file

Target deployment includes offline USB distribution, WhatsApp file sharing, and contexts where learners cannot install dependencies. A single file with zero build step satisfies R14 (single-server operation) and R15 (file-based backup) and can be shared as-is. React+Node.js+SQLite (Paper 2 top-ranked stack, 4.66/5.0) is the target for a future production version. **Do not refactor to multi-file** without confirming the deployment model has changed.

### Why localStorage instead of IndexedDB

`localStorage` is synchronous and universally available on the low-end Android devices in scope. IndexedDB adds async complexity not justified in a single-file prototype. All storage calls are synchronous — do not introduce async storage patterns without migrating all state management.

### Why passwords are stored in plaintext

Client-side-only prototype. No server to hash against. Demo seeds hardcoded accounts (`admin123`, `teach123`, `student123`). Never ship to real learners without server-side auth with bcrypt or equivalent.

### Why the leaderboard requires ≥10 members

PR9/privacy requirement from Paper 3 gamification framework. In conflict-affected contexts, being identifiable as a student can be a safety risk. The threshold prevents re-identification in small groups. Do not lower without explicit research team sign-off.

### Why freeze tokens are awarded at 1 per 7 days

Documented power and connectivity outage frequency in conflict zones is approximately weekly (Burde et al., 2019; cited in Paper 3). The 7-day interval is calibrated to this, not chosen arbitrarily. Changing it requires updating the PR9 compliance claim.

### Why the diagnostic bypass threshold is 70%

Mastery learning bypass threshold (Bloom, 1968): sufficient competence to proceed without foundational instruction. Deliberately lower than the mastery threshold (80–90%) to reduce barriers for learners with computing backgrounds. Defined in PR12. Do not change without updating the PR12 specification.

### Why the sync payload is capped at 6 fields

PR13 data minimisation requirement. In conflict settings, metadata about study activity can be sensitive. No free-text, device ID, geolocation, or behavioural sequences are ever transmitted. Do not add fields to the sync payload without reviewing PR13.

### Why AI jobs call the Anthropic API directly from the browser

Prototype convenience only. Will be blocked by CORS in most real deployments and exposes the API key. A thin server-side proxy is required before any real deployment. `buildAIPrompt()` is the right place to adjust prompt templates.

---

## YouTube Channel

**56 scripts complete** (.docx files in outputs directory). 4 videos per module × 14 modules:
1. Concept Introduction
2. Worked Example
3. Lab Walkthrough
4. Quiz Review

Production not yet started. Next step: production tracker Excel workbook.

---

## The Secret Channel

12-episode cryptography drama.
- Tagline: *"You cannot love someone you cannot verify."*
- Characters: Alice, Bob, Eve, Mallory
- EP0 pilot + EP1–EP11

**Production workbook complete:** `The_Secret_Channel_Series_Final_VO.xlsx`
- 67 shots, ~200 Veo 3.1 clip prompts, 4 Motion Graphics shots, 49 timed voiceover lines

Production not yet started. Next step: EP0 clip generation in Google Flow.

---

## Known Issues and Tech Debt

| Issue | Severity | Notes |
|-------|----------|-------|
| API key exposed in AI pipeline | High | Needs server-side proxy before any real deployment |
| Plaintext passwords in localStorage | High | Demo only — needs server-side auth for production |
| Unsigned JWT tokens | Medium | base64 payload only; no HMAC signing |
| QR codes on certificates are decorative | Low | Procedural SVG, not real QR codes |
| `triggerSync()` is simulated | Medium | Logs to console; no real HTTP POST |
| localStorage ~5 MB quota | Medium | Heavy xAPI logs or large content registry could hit limit on some devices |
| Dynamic groups not auto-rebuilt | Low | `rebuildDynamicGroup()` must be called manually; no scheduled trigger |

---

## Open Content Expansions (not started)

- Peggy (prover) and Victor (verifier) characters in Zero-Knowledge proof modules (Module 10)
- Additional DAILY_MCQ_BANK entries for Modules 11–13 (currently 2 each; all other modules have 3+)

---

## What Comes Next (Cycle 2)

1. Field pilot with target-population learners
2. TalkBack manual testing with native Arabic speaker
3. Formal NASA-TLX data collection (PR3 acceptance)
4. Chrome DevTools performance measurement on reference Android device (PR5 acceptance)
5. EP0 clip generation for The Secret Channel
6. YouTube production tracker workbook
