# Crypto-Course — Minimal Sync Backend Spec

Pilot-grade central store so teachers can follow cohort progress. Frontend stays
on GitHub Pages; this is the small external service the app currently lacks.
Reference implementation: `crypto-course-sync-worker.js` (Cloudflare Worker + KV).

---

## 1. Why Cloudflare Workers + KV
- Maps 1:1 to the app's existing client calls (`PUT/GET {base}/{userId}`), so the
  push/pull code barely changes.
- Proper CORS preflight handling for JSON `PUT` (Google Apps Script redirects
  preflight to a different origin and breaks it unless you downgrade to
  `text/plain` POSTs — avoidable friction).
- Free tier: 100k reads/day, 1k writes/day, 1 GB KV — ample for a cohort pilot.
- **Zero-account alternative:** Apps Script + a Google Sheet works if you accept
  switching the client to `POST` + `Content-Type: text/plain` (no preflight) and
  parsing JSON server-side. Bonus: the teacher reads the Sheet directly. Use this
  only if standing up a Cloudflare account is the blocker.

## 2. API contract
| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET`  | `/__ping` | none | health check (the app's "Test connection") |
| `PUT`  | `/{userId}` | cohort **write** token | student stores their minimal payload |
| `GET`  | `/{userId}` | cohort **write** token | student pulls their own record (204 if none) |
| `GET`  | `/cohort/{code}` | cohort **teacher** token | teacher reads all students in the cohort |

`base` = the deployed worker URL (e.g. `https://crypto-course-sync.<you>.workers.dev`).
Set it in the app's sync-URL field (stored as `crypto_course_sync_url`); the client
already appends `/{userId}`.

## 3. Payload contract (unchanged from the app)
The client already sends a PR13-shaped envelope: `xpDelta`, `streak`,
`badgeTimestamps`, `quizOutcomes`, `labCompletions`, `sessionDuration`. The worker
**re-minimises server-side** against an allowlist — any extra field (e.g. an
accidental `email` or free-text) is dropped before storage. KV key:
`student:{cohort}:{userId}`, value `{ payload, updatedAt }`, with a 180-day TTL.

## 4. Auth & threat model (read before piloting)
- The **write token is shared per cohort**. It identifies the cohort and authorises
  writes. This deters casual abuse and locks reads/writes to enrolled users, but it
  is *not* per-student: a student who knew another student's opaque `userId` and the
  shared token could overwrite that record. Acceptable for a low-stakes pilot;
  upgrade to per-student tokens (or signed enrolment) if integrity matters.
- A student can already inflate their *own* local XP (client-side app) — merge is
  forward-only, so this is low-stakes for a learning tool.
- The **teacher token is separate and never shipped to students** — keep it out of
  the public repo and the client bundle.
- The worker URL is public (fine — not a secret), so rely on: the tokens, the
  `ALLOWED_ORIGINS` CORS lock, the 16 KB body cap, the field allowlist, and
  Cloudflare's platform rate-limiting. Add a WAF rate rule if you expect abuse.

## 5. Deploy (Cloudflare)
```bash
npm i -g wrangler
wrangler login

# wrangler.toml
# name = "crypto-course-sync"
# main = "crypto-course-sync-worker.js"
# compatibility_date = "2024-11-01"
# kv_namespaces = [{ binding = "SYNC", id = "<from next command>" }]

wrangler kv namespace create SYNC          # paste the id into wrangler.toml

# secrets / vars
wrangler secret put ALLOWED_ORIGINS        # e.g. https://you.github.io,http://localhost:8080
wrangler secret put COHORTS_JSON           # {"WMIN2026":{"write":"w_LONGRANDOM","teacher":"t_LONGRANDOM"}}

wrangler deploy
```
Generate tokens with `openssl rand -hex 24`. Add more cohorts by editing
`COHORTS_JSON` and re-putting the secret (no code change).

## 6. Client changes still required (small, in index.html)
The backend is ready; the client needs three edits to actually use it:

1. **Send the write token** on push/pull. In `triggerSync()` and `pullSync()`, add
   the header to the existing `fetchWithTimeout` calls:
   ```js
   headers: { 'Content-Type': 'application/json',
              'Authorization': 'Bearer ' + (localStorage.getItem('crypto_course_write_token') || '') }
   ```
   Store the cohort write token at enrolment (it can ride along with the invite).

2. **Auto-sync on reconnect** (the part that delivers "syncs when online"):
   ```js
   window.addEventListener('online', () => { triggerSync(); pullSync(); });
   // also call triggerSync() on module/lab completion and on visibilitychange→hidden
   ```

3. **Teacher cohort fetch** for the dashboard (new — currently the teacher view only
   reads this device's localStorage):
   ```js
   async function fetchCohort(code) {
     const base = getSyncEndpoint();
     const r = await fetchWithTimeout(`${base}/cohort/${encodeURIComponent(code)}`,
       { headers: { 'Authorization': 'Bearer ' + teacherToken } }, 8000);
     return r.ok ? (await r.json()).students : [];
   }
   ```
   Render those records in the teacher dashboard instead of (or merged with) local.

Also: drop the `getSyncEndpoint()` default of `origin + '/api/sync'` — on a static
host it points at a 404. Return `null` (local-only) unless an override URL is set,
so the UI honestly reports state.

## 7. Privacy / ethics note
Turning this on moves the app from local-only to a central store a teacher can read,
which re-engages UK-GDPR (lawful basis, consent, retention, access scope) and must
be in the Westminster ethics submission. The *transit* payload is minimal and
PII-free (good), but identifiability returns at the teacher end via the
`userId → student` roster mapping. For strict PR13 reading, consider reducing
`quizOutcomes` from per-item maps (`quizAttempts`, `spacedRevisits`) to aggregate
counts before enabling cohort sync.
