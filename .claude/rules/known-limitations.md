---
description: Known prototype limitations — security, storage, and features that are simulated or incomplete and must not be presented as production-ready
alwaysApply: true
---

- JWT tokens are **not** cryptographically signed (base64 only)
- Passwords stored as **plaintext** in `localStorage`
- All storage is `localStorage` — multi-device sync requires a real backend
- QR codes on certificates are decorative SVG — not scannable
- Leaderboard is per-device only
- Cloud sync is real, not simulated: `pullSync()` / `triggerSync()` call the Cloudflare Worker set in `sync-config.json` (cached as `crypto_course_sync_url`) and need a write token (`crypto_course_write_token`, from a semester join or restored at login). Since v1.6.0, `cloudSyncAllowed()` keeps guest sessions and token-less sessions local — no request carries their id. The write token is device-wide and is **not** cleared on logout.
- `sw.js` and `manifest.json` must exist as separate files for PWA/offline to work
- AI pipeline calls `api.anthropic.com` directly from the browser — requires a server-side proxy in production
