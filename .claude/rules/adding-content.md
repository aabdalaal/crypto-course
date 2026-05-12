---
description: Step-by-step checklist for adding modules and badges in code or via the admin panel — includes all PR compliance requirements
alwaysApply: true
---

## Add a module (code)

1. Append to `MODULES` with all required fields including `level` (Introductory/Foundational/Intermediate/Advanced)
2. Follow the 7-stage template (PR3): stage1–stage3 lessons, stage4 lab, stage5 quiz, completion stage
3. Add `why` and `concept` fields to every quiz option (PR4)
4. Add `tiers: { core, consol, boost }` to `stage5` for adaptive difficulty
5. Add a `renderLab()` case for any new `labId` — **no network calls** (PR8)

## Add a module (no code)

Use the admin **Content Editor** panel.

## Add a badge

- Code: append to `BADGES` array with a `condition: s => ...` predicate.
- No code: use the admin **Badge Challenges** panel.
