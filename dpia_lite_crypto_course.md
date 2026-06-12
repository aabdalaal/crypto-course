# Crypto-Course PWA — Data Protection Summary (DPIA-lite)

**Prepared:** 12 June 2026 · **System:** Crypto-Course Progressive Web App, cloud sync feature
**Controller (proposed):** University of Westminster · **Processor:** Cloudflare, Inc. (Workers + KV)
**Status:** Draft for DPO / ethics review — not legal advice; requires sign-off before student pilot.

## 1. Processing overview

Crypto-Course is an offline-first educational PWA. All learning data is stored on the
student's device by default. When a student is online and signed in, the app backs up a
minimised progress payload to a Cloudflare Worker + KV store so that (a) teachers can
monitor cohort progress and support struggling students, and (b) the research team can
evaluate the platform's pedagogical effectiveness (DBR methodology, Paper 3).

Transparency model: **notice + opt-out.** A privacy notice (bilingual EN/AR) is presented
in-app at first login; students may disable backup at any time via a Profile toggle or
directly from the notice. When opted out, no network call carrying the student identifier
is made (both push and pull paths are gated in code).

## 2. Data inventory (PR13 payload — enforced in code)

| Field category | Contents | Personal data? |
|---|---|---|
| xpDelta | Accumulated experience points | Yes (linked to user ID) |
| streak | Consecutive-day count | Yes |
| badgeTimestamps | Badge award dates | Yes |
| quizOutcomes | Quiz/lesson counts, module progress, diagnostic score, attempt counts, module time totals | Yes |
| labCompletions | Lab completion count and map | Yes |
| sessionDuration | Seconds in current session | Yes |
| User identifier | Account ID (sub) in request path | Yes |

**Excluded by design (code-enforced):** free-text input, device identifiers, geolocation,
behavioural event sequences, IP-based profiling. Guest-mode users have no identifier and
never sync.

## 3. Purposes and lawful basis

| Purpose | Suggested lawful basis (for DPO confirmation) |
|---|---|
| Teacher progress monitoring | UK GDPR Art. 6(1)(e) public task (education) or 6(1)(f) legitimate interests |
| Research evaluation | Art. 6(1)(e) public task (university research), with ethics approval; consent handled at study level via participant information sheet |

Note: the in-app opt-out is a transparency/objection mechanism, not the lawful basis.
If cohorts include under-18s, the DPO should confirm the basis and whether parental
information is required.

## 4. Storage, security, and transfers

- **At rest:** Cloudflare Workers KV, access controlled by Bearer tokens (separate
  student write token and teacher token); HTTPS in transit.
- **International transfers — ACTION REQUIRED:** Cloudflare KV replicates globally by
  default. Either (a) document the transfer under Cloudflare's UK/EU data processing
  addendum and SCCs, or (b) evaluate Cloudflare's regional/jurisdiction controls for the
  Worker. The DPIA must record the chosen option.
- **Access:** teacher (own cohort via `fetchCohort`, teacher token required) and research
  team only. No public endpoints return personal data without a token.

## 5. Retention and deletion

- **Stated retention:** deleted at the end of the semester (as presented in the in-app notice).
- **ACTION REQUIRED:** an operational deletion process must exist to honour this —
  e.g. a KV namespace purge or TTL set at semester close. Currently no automated
  deletion job is implemented; recommend KV `expirationTtl` on writes or a documented
  end-of-semester purge procedure run by the teacher/researcher.

## 6. Data subject rights handling

- **Right to object / restrict:** in-app backup toggle (immediate effect, code-gated).
- **Access / erasure requests:** directed to the project contact address shown in the
  notice. **ACTION REQUIRED:** the address `cryptocourse-privacy@westminster.ac.uk` is a
  placeholder pattern — create this mailbox or replace it in the app (single location:
  `id="privacy-contact-email"` in index.html) and in this document before any pilot.
- **Rectification:** progress data is machine-generated; rectification requests handled
  case-by-case via the contact address.

## 7. Risk register (summary)

| Risk | Likelihood | Mitigation |
|---|---|---|
| Re-identification of pseudonymous progress data | Low | Minimised payload; access restricted to teacher/research team |
| Token leakage enabling unauthorised reads | Low–Med | Bearer tokens in localStorage; recommend per-cohort token rotation each semester |
| Retention promise not honoured | Med (no automation yet) | Implement KV TTL or documented purge (Section 5) |
| Transfer outside UK without safeguards | Med (KV default) | Resolve per Section 4 before pilot |
| Minors in cohorts without adequate notice | Context-dependent | Notice written in plain language; DPO to confirm age-appropriate requirements |

## 8. Outstanding actions before pilot

1. DPO confirmation of lawful basis (Section 3).
2. International-transfer decision documented (Section 4).
3. Deletion mechanism implemented or procedure documented (Section 5).
4. Contact mailbox created or address replaced in app + this document (Section 6).
5. Ethics approval referencing this summary; participant information sheet aligned with
   the in-app notice wording.
