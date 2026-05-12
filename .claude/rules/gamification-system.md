---
description: XP thresholds, 9 built-in badges with trigger conditions, streak and freeze token rules, and the CipherPulse daily challenge
alwaysApply: true
---

## XP & Levels

```
LVL 1 — Novice               (0 XP)
LVL 2 — Apprentice           (100 XP)
LVL 3 — Practitioner         (225 XP)
LVL 4 — Cryptographer        (375 XP)
LVL 5 — Master Cryptographer (500 XP)
```

## Badges (9 built-in + custom)

| ID | Icon | Trigger |
|----|------|---------|
| `first_lesson` | 🔐 | 1 lesson completed |
| `on_fire` | 🔥 | 3-day streak |
| `quiz_master` | ⚡ | 1 perfect quiz |
| `week_warrior` | 📅 | 7-day streak |
| `crypto_scholar` | 🎓 | 12 lessons completed |
| `diamond_coder` | 💎 | 375 XP (Level 4) |
| `lab_hero` | ⚗️ | 3 labs completed |
| `mod_intro` | 📖 | Module 0 complete |
| `metro_breaker` | 🗞️ | CipherPulse substitution cipher cracked (`state.metroBadgeEarned`) |

`getAllBadges()` merges built-in badges with published custom badges.

## Streak & Freeze Tokens (PR9)

- `state.freezeTokens` default 3; ≥1 token auto-awarded per 7 days (matches conflict-zone outage frequency)
- Confirmation sheet before use
- **Never reduce standing on connectivity failure** — hard PR9 constraint

## Daily Challenge — CipherPulse

Rotating `DAILY_CRYPTOGRAMS` array; Caesar cipher puzzles with hints. Once per day (`YYYY-MM-DD` key). Awards 3 XP. Also drives `caesar_lab` with standard and Metro (frequency analysis) modes.
