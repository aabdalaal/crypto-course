---
description: Phase 2 tiered questions, Phase 3 spaced repetition, Phase 4 adaptive difficulty, and the mastery gate — pedagogical enhancement features
alwaysApply: true
---

## Phase 2 — Tiered Questions (Flow Theory)

`stage5` can carry a `tiers` object to maintain the flow channel across skill levels:

```js
tiers: {
  core:   { question, options, why, concept },    // baseline
  consol: { ... },  // consolidation — links to earlier concept
  boost:  { ... },  // harder applied/challenge question
}
```

`getActiveTierQuestion(content)` resolves the active tier from `lessonState.currentTier`.

## Phase 3 — Spaced Repetition (Memory Science)

`scheduleRevisit(moduleId)` queues revisit quizzes at +7 and +14 days after module completion. Cards appear on the home screen. `SR_INTERVALS_DAYS = [7, 14]`.

## Phase 4 — Adaptive Difficulty (Flow Theory)

`computeAdaptiveTier(moduleId)` reads the last 5 quiz results from analytics. Consistent high scores → promote tier to `consol` or `boost`. Struggling → keep/demote to `core`.

## Mastery Gate (Mastery Learning — Bloom, 1968)

Students cannot complete a module without passing the quiz (`lessonState.quizPassed`). Advancement requires demonstrated competence, not just exposure.
