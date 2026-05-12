# MEMORY.md — Crypto-Course App

This file tracks evolving decisions, active work, known issues, and context that builds up during development. Update it as things change. It is read alongside CLAUDE.md — don't duplicate what's already there.

---

## Current State

- **Single file:** `crypto_course_app.html` (~15,500 lines)
- **Companion files needed:** `sw.js` (service worker) and `manifest.json` (PWA manifest) — these do not yet exist in the repo; PWA/offline features will silently fail without them
- **Auth:** Simulated only — tokens are unsigned base64, passwords are plaintext in localStorage. Not production-ready.
- **Sync:** `triggerSync()` is a stub — logs to console only, no real HTTP call
- **AI pipeline:** `processAIJob()` calls `api.anthropic.com` directly from the browser — CORS will block this in most deployments; needs a proxy

---

## Active Development Context

_Update this section when starting a new work session._

- No active branch or PR tracked here yet
- No pending migrations
- No open bugs logged here yet

---

## Decisions Log

Record significant design decisions here so they don't have to be re-debated.

### Why a single HTML file instead of a proper build system
**Decision:** Keep everything in one `.html` file for the current prototype phase.  
**Rationale:** Target deployment contexts include offline USB distribution, WhatsApp file sharing, and situations where learners cannot install dependencies. A single file with zero build step satisfies R14 (single-server operation) and R15 (file-based backup) and can be shared as-is. React+Node.js+SQLite (the Paper 2 recommended stack) is the target for the production version.  
**Do not refactor to a multi-file build** without confirming the deployment model has changed.

### Why localStorage instead of IndexedDB
**Decision:** `localStorage` is used as an "IndexedDB proxy" (noted in the code comment).  
**Rationale:** `localStorage` is synchronous and universally available on the low-end Android devices in scope. IndexedDB is async and adds complexity that isn't justified in the single-file prototype. The code comments explicitly acknowledge this trade-off.  
**Implication:** All storage calls are synchronous; don't introduce async storage patterns without migrating all state management.

### Why passwords are stored in plaintext
**Decision:** Plaintext passwords in `localStorage` for the demo.  
**Rationale:** This is a client-side-only prototype. There is no server to hash against. The code seeds demo accounts with hardcoded passwords (`admin123`, `teach123`, `student123`).  
**Never ship this to real learners** without a server-side auth system with bcrypt or equivalent.

### Why the leaderboard requires ≥10 group members
**Decision:** Leaderboard is suppressed for groups smaller than 10.  
**Rationale:** This is a **PR9/privacy requirement** grounded in the Paper 3 gamification framework. In conflict-affected contexts, being identifiable as a student (even by name initial) can be a safety risk. The threshold prevents re-identification of individuals in small groups.  
**Do not lower this threshold** without explicit sign-off from the research team.

### Why freeze tokens are awarded at 1 per 7 days
**Decision:** Exactly 1 freeze token auto-awarded every 7 days.  
**Rationale:** Documented power and connectivity outage frequency in conflict zones is approximately weekly (Burde et al., 2019; cited in Paper 3). The 7-day interval is calibrated to this, not chosen arbitrarily. Changing it requires updating the PR9 compliance claim.

### Why the diagnostic bypass threshold is 70%
**Decision:** Learners scoring ≥70% on the 10-item diagnostic can skip Introductory modules.  
**Rationale:** 70% is the mastery learning bypass threshold (Bloom, 1968) — sufficient competence to proceed without foundational instruction. It is deliberately lower than the mastery threshold (80–90%) to reduce barriers for learners with computing backgrounds. Defined in PR12. Do not change without updating the PR12 specification.

### Why the sync payload is capped at 6 fields
**Decision:** `triggerSync()` transmits only: XP delta, streak, badge timestamps, quiz outcome flags, lab completions, session duration.  
**Rationale:** PR13 data minimisation requirement. In conflict settings, metadata about study activity can be sensitive. No free-text, device ID, geolocation, or behavioural sequences are ever transmitted. This is a hard constraint — do not add fields to the sync payload without reviewing PR13.

### Why AI jobs call the Anthropic API directly from the browser
**Decision:** Current implementation calls `api.anthropic.com` from the client.  
**Rationale:** Prototype only. This will be blocked by CORS in most real deployments and exposes the API key. The intent is that a thin server-side proxy will be added before any real deployment. The `buildAIPrompt()` function is the right place to adjust prompt templates.

---

## Known Issues / Tech Debt

| Issue | Severity | Notes |
|-------|----------|-------|
| `sw.js` and `manifest.json` missing | High | PWA install and offline caching will not work until these are created |
| API key exposed in AI pipeline | High | Needs server-side proxy before any real deployment |
| Plaintext passwords | High | Demo only — needs server-side auth for production |
| Unsigned JWT tokens | Medium | base64 payload only; no HMAC signing |
| QR codes on certificates are fake | Low | Procedural SVG, not real QR; verify URL is decorative |
| `triggerSync()` is a stub | Medium | Logs to console; no real HTTP POST |
| localStorage has ~5MB quota | Medium | Heavy xAPI logs or large content registry could hit the limit on some devices |
| Dynamic groups are not auto-rebuilt | Low | `rebuildDynamicGroup()` must be called manually; no scheduled trigger |

---

## Feature Flags / Incomplete Features

| Feature | Status | Notes |
|---------|--------|-------|
| PWA offline | Partial | App works offline; service worker registration is in the HTML but `sw.js` is missing |
| AI content pipeline | Prototype | Functional in browser but needs CORS proxy; Arabic translation supports PR11 |
| Spaced repetition (Phase 3) | Implemented | `spacedRevisits` in state; cards shown on Home screen |
| Adaptive difficulty (Phase 4) | Implemented | `computeAdaptiveTier()` reads last 5 quiz results |
| xAPI export | Implemented | Admin panel → xAPI Export tab |
| Semester system | Implemented | Admin creates semesters; students join via code |
| Dynamic groups | Implemented | Rule-based group membership via `rebuildDynamicGroup()` |
| Certificate QR verification | Stub | URL is decorative; no real verification endpoint |
| Real server sync | Not started | `triggerSync()` is console-only |

---

## PR Compliance Checklist

Use this when reviewing changes to verify nothing has broken a formal requirement.

- [ ] **PR3** — Does every module still follow the 7-stage template?
- [ ] **PR4** — Does every quiz question still have `why` and `concept` fields?
- [ ] **PR8** — Does every lab still use only Web Crypto API with zero network calls?
- [ ] **PR9** — Can any code path reduce XP/streak/badges due to a connectivity event?
- [ ] **PR10** — Is `saveState()` still called after every user interaction?
- [ ] **PR13** — Does the sync payload still contain only the 6 permitted fields?

---

## File Notes

- **`crypto_course_app.html`** — The whole app. Sections are separated by `// ============` comment blocks. Use these as landmarks when navigating.
- **`sw.js`** — Needs to be created. Should cache the HTML file and all Google Fonts requests. Use a cache-first strategy for the HTML and a network-first strategy for fonts.
- **`manifest.json`** — Needs to be created. App name: `CryptoCourse`, theme colour: `#0F172A`, background: `#0F172A`, display: `standalone`, icons needed at 192×192 and 512×512.
- **`Paper2_*.docx`** — Technology selection framework. Read this before changing the architecture.
- **`Paper3v2_Improved.docx`** — Pedagogical requirements PR1–PR14. Read this before changing any learning flow, gamification mechanic, or accessibility feature.
