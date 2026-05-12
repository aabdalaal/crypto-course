---
description: 14 CyBOK-aligned modules with levels and lab IDs, plus the mandatory 7-stage lesson structure (PR3)
alwaysApply: true
---

## Modules (14 total, CyBOK-aligned)

Sequencing follows the **CyBOK knowledge framework** (Rashid et al., 2018) — from historical foundations to contemporary applications, in strict ascending difficulty order (PR2).

| ID | Name | Level | Lab |
|----|------|-------|-----|
| 0 | Introduction to Cryptography | Introductory | `hash_lab` |
| 1 | Introduction to Cryptography (Extended) | Foundational | `vigenere_lab` |
| 2 | Symmetric Cryptography I | Foundational | `openssl_sym_lab` |
| 3 | Symmetric Cryptography II | Foundational | `openssl_modes_lab` |
| 4 | Hash Functions | Foundational | `openssl_hash_lab` |
| 5 | Public Key Cryptography I | Intermediate | `openssl_rsa_lab` |
| 6 | Mid-Module Review | Intermediate | `hash_lab` |
| 7 | Public Key Cryptography II | Intermediate | `openssl_rsa_lab` |
| 8 | Key Management | Intermediate | `cert_lab` |
| 9 | Authentication Protocols | Intermediate | `sign_lab` |
| 10 | Zero-Knowledge & Auth Proofs | Advanced | `sign_lab` |
| 11 | Key Establishment & TLS | Advanced | `ecdh_lab` |
| 12 | Attacks | Advanced | `attacks_lab` |
| 13 | Developments | Advanced | `sign_lab` |

The hardcoded `MODULES` array is the seed. `getAllModules()` merges it with custom modules in the content registry at runtime.

## Lesson Stage Structure (PR3 — identical 7-stage template)

Every module follows this exact structure:
- `stage1` — lesson content (HTML: concept-boxes, code-blocks, worked examples)
- `stage2/3` — additional lesson stages
- `stage4` — interactive lab (`type: 'lab'`, `labId`)
- `stage5` — quiz with tiered questions (`tiers`) or flat `question`/`bank`
- `stage6/7` — completion screen with XP award

`lessonState`: `{ moduleId, stage, quizAnswered, quizAttempts, quizPassed, labRecallValue, masteryGateAttempts, currentTier, tierResults }`
