---
description: Reference table of all key functions in the codebase — what each does and which PR it relates to
alwaysApply: true
---

| Function | Purpose |
|----------|---------|
| `navigate(screen)` | Switch visible screen |
| `getAllModules()` | Merge built-in + custom registry modules |
| `openModule(id)` | Enter lesson flow |
| `lessonNext()` | Advance stage (enforces mastery gate) |
| `renderLab(content, mod)` | Inject lab UI (Web Crypto API — no network) |
| `getActiveTierQuestion(content)` | Resolve tiered question for current tier |
| `computeAdaptiveTier(moduleId)` | Auto-select difficulty from analytics history |
| `scheduleRevisit(moduleId)` | Schedule spaced repetition at +7/+14 days |
| `awardXP(amount, reason)` | Add XP, check level-up, save state |
| `checkBadges()` | Evaluate all badge conditions |
| `getAllBadges()` | Merge built-in + published custom badges |
| `queueAIJob(moduleId, jobType)` | Queue AI content generation job |
| `processAIJob(jobId)` | Call Anthropic API and store result |
| `checkAssignmentReminders()` | Fire deadline toast reminders |
| `rebuildDynamicGroup(group)` | Recalculate dynamic group membership |
| `renderAnalyticsTab()` | Render analytics from xAPI + state |
| `emitXAPI(verb, obj, ext)` | Record learning event |
| `triggerSync()` | Simulate server sync (PR13 6-field payload) |
| `issueCertificate(moduleId)` | Award completion certificate |
| `startDiagnostic()` | Launch 10-question entry assessment (PR12) |
| `setLanguage(lang)` | Switch UI language: `'en'` / `'ar'` (PR11) |
| `saveState()` | Persist state to localStorage (called after every interaction — PR10) |
| `initAuth()` | Restore session from localStorage |
| `canAccess(role)` | RBAC guard |
