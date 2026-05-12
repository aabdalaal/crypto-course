---
description: Known prototype limitations — security, storage, and features that are simulated or incomplete and must not be presented as production-ready
alwaysApply: true
---

- JWT tokens are **not** cryptographically signed (base64 only)
- Passwords stored as **plaintext** in `localStorage`
- All storage is `localStorage` — multi-device sync requires a real backend
- QR codes on certificates are decorative SVG — not scannable
- Leaderboard is per-device only
- `triggerSync()` is fully simulated — no real network call
- `sw.js` and `manifest.json` must exist as separate files for PWA/offline to work
- AI pipeline calls `api.anthropic.com` directly from the browser — requires a server-side proxy in production
