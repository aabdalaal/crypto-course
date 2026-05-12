---
description: Single-file SPA+PWA architecture, screen navigation pattern, state management shape, and complete localStorage key registry
alwaysApply: true
---

## Single-File SPA + PWA

The app is one HTML file (~15,500 lines) with no build step:
1. `<style>` — CSS with design tokens
2. HTML markup — all screens pre-rendered, shown/hidden via `.screen.active`
3. `<script>` — all logic, data, and state management inline

Two required companion files:
- `sw.js` — service worker (cache strategy for offline use)
- `manifest.json` — PWA manifest (home screen installation)

## Screen Navigation

`navigate(screenName)` controls which `<div class="screen" id="screen-{name}">` is active. Bottom nav: **Home**, **Modules**, **Progress**, **Profile**, **Admin** (teacher+).

## State Management

Global `state` object persisted to `localStorage` after every interaction (PR10). Per-user keys: `STATE_KEY + '_' + currentUser.sub`.

```js
const defaultState = {
  xp, streak, freezeTokens,
  lessonsCompleted, quizzesCompleted, perfectQuizzes, labsCompleted,
  moduleProgress: {},          // { moduleId: completionFraction }
  badges: [],
  language, highContrast, textSize, reduceAnim,
  lastSync, quizAttempts: {},
  currentLesson: { moduleId, stage },
  lastChallengeDate, diagnosticDone, diagDismissed,
  leaderboardOptIn,
  readAnnouncements: [], semesterId,
  spacedRevisits: {},          // Phase 3: { moduleId: { completedAt, nextRevisit7, nextRevisit14, revisitsDone } }
};
```

## localStorage Keys

| Key | Purpose |
|-----|---------|
| `crypto_course_state` | Shared/legacy state |
| `crypto_course_state_{userId}` | Per-user state |
| `crypto_course_leaderboard` | Cohort leaderboard entries |
| `crypto_course_users` | Simulated user database |
| `crypto_course_session` | Auth session token |
| `crypto_course_certs` | Issued certificates |
| `crypto_course_xapi` | xAPI event log (last 200) |
| `crypto_course_assignments` | Teacher-created assignments |
| `crypto_course_quiz_analytics` | Per-question quiz attempt data |
| `crypto_course_content_registry` | Custom/edited module registry |
| `crypto_course_content_index` | Module ordering index |
| `crypto_course_ai_jobs` | AI content generation job queue |
| `crypto_course_ai_approved` | Teacher-approved AI-generated content |
| `crypto_course_announcements` | Teacher/admin announcements |
| `crypto_course_semesters` | Semester definitions |
| `crypto_course_groups` | Cohort groups (static + dynamic) |
| `crypto_course_custom_badges` | Admin-created custom badges |
| `crypto_course_atrisk_dismissed` | Dismissed at-risk student alerts |
| `crypto_course_reminder_shown` | Assignment reminder dedup log |
