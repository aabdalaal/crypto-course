# Crypto-Course — Video Landing Pages

Companion video layer for the Arabic printed textbook. Every printed QR code
links to a stable URL on this domain; the actual video destinations live in
`videos.json` and can be updated without reprinting a single page.

---

## Architecture

```
Printed QR code
      │
      ▼
/videos/module.html?m=N          ← stable URL — never changes
      │
      │  fetch('./videos.json')
      ▼
/videos/videos.json              ← single source of truth for all 56 video links
      │
      ▼
Learner clicks ▶ Watch           → YouTube / Mirror / Download
```

**Why this indirection matters:** YouTube links change (videos get re-uploaded,
censored, or moved to mirrors). The QR codes in the printed book point to
`module.html?m=N` — a URL *you* control forever. When a video moves, you update
`videos.json` and push; every existing printed book is instantly fixed with no
reprint.

---

## File map

| File | Purpose |
|------|---------|
| `videos.json` | Source of truth — 14 modules × 4 video types = 56 entries |
| `module.html` | Dynamic landing page — reads `?m=N`, fetches JSON, renders cards |
| `generate_qr.py` | Generates 28 QR files (PNG + SVG) into `qr/` |
| `qr/module_NN.png` | Print-ready QR at 300 DPI (≥3.5 cm per side) |
| `qr/module_NN.svg` | Scalable QR for layout software |

The `qr/` folder is committed to the repository so GitHub Pages serves the
images directly (useful for companion web pages or digital textbook versions).

---

## How to fill in video URLs

Open `videos.json`. Every placeholder follows this pattern:

```
"primary_url": "https://PLACEHOLDER-PRIMARY-M01-CONCEPT-INTRO"
```

Replace each `https://PLACEHOLDER-…` value with the real URL:

```json
"primary_url": "https://youtu.be/REAL_VIDEO_ID",
"mirror_url":  "https://archive.org/details/REAL_ARCHIVE_ID",
"download_url": "https://youtu.be/REAL_VIDEO_ID?quality=low"
```

Fields:
- **`primary_url`** — main link (YouTube, Vimeo, etc.)
- **`mirror_url`** — fallback if primary is blocked (Internet Archive, PeerTube, etc.)
- **`download_url`** — direct download of a low-bandwidth version (≤100 MB)

Leave a field as `https://PLACEHOLDER-…` and the landing page shows a
"Coming Soon" state instead of a broken link — safe to deploy before all
videos are ready.

---

## How to update a video after printing

1. Open `videos.json`
2. Change the relevant `primary_url` (or `mirror_url`) value
3. `git add videos/videos.json && git commit -m "Update M03 lab walkthrough URL"`
4. `git push`

GitHub Pages typically deploys within 60 seconds. The change is live
globally — all printed books now resolve to the new destination.
No QR regeneration. No reprint.

---

## How to generate QR codes

**One-time setup:**
```bash
pip install segno
```

**Edit `generate_qr.py`** — set the two constants at the top:
```python
GITHUB_USER = "ahmedfuad"         # your GitHub username
REPO_NAME   = "crypto-course"     # your repository name
```

**Run:**
```bash
cd videos/
python generate_qr.py
```

Output: `qr/module_01.png` … `qr/module_14.png` and matching `.svg` files.
The script also prints a table of all 14 stable URLs for copy-paste into the
textbook layout.

**QR spec:**
- Error correction level **H** (survives up to 30% physical damage — safe for
  textbook print where pages flex and corners wear)
- PNG at **300 DPI**, scale = 10 px/module → ≥3.5 cm per side for all URL lengths
- SVG is inherently scalable — place at **≥2 cm × 2 cm** in your layout tool
- Pure black `#000000` on white `#ffffff` — no colour, no gradients

---

## Pre-print QR scan-test checklist

Run this checklist on a physical printout (not a screen) before sending
to the printer.

- [ ] **Replace placeholders** — `GITHUB_USER` and `REPO_NAME` in
      `generate_qr.py` are set to real values; re-run the script.
- [ ] **Fill all URLs** — search `videos.json` for `PLACEHOLDER`; none should
      remain for modules included in this print run.
- [ ] **Deploy** — `git push` is complete and GitHub Pages has rebuilt
      (wait ≥ 2 minutes; check the Actions tab).
- [ ] **Scan module 1 QR** — opens `module.html?m=1` on a real mobile device.
- [ ] **Scan module 14 QR** — confirms the highest module number works.
- [ ] **Scan 3 random middle modules** — spot-check modules 5, 9, 12.
- [ ] **Tap Watch on each spot-checked card** — confirm it opens the correct
      video, not a 404 or placeholder state.
- [ ] **Test on low-end Android** (Chrome, airplane mode off, 3G throttle in
      DevTools or actual slow connection) — page loads within 5 seconds.
- [ ] **Test Arabic display** — module titles render right-to-left with no
      layout overflow on a 360px-wide screen.
- [ ] **Minimum QR print size** — measure the printed QR with a ruler:
      must be ≥2 cm × 2 cm. If smaller, increase image size in layout software
      and reprint the test page.
- [ ] **Scan from 20 cm distance** — phone camera decodes without error;
      no manual URL entry required.

---

## Cache note

Browsers cache `videos.json`. If a learner visited the page before an update
and sees stale content, a hard refresh (Ctrl+Shift+R / ⌘+Shift+R) clears it.
For a forced cache-bust on deploy, append a version query to the fetch call
in `module.html`:

```js
// Change ?v=2 to ?v=3 on next update
const resp = await fetch('./videos.json?v=2');
```

---

## Deployment note

This folder deploys automatically as part of the main GitHub Pages push —
no separate workflow needed. The only requirement is that `videos.json` and
`module.html` sit at `/videos/` relative to the Pages root, which is the
case when this `videos/` folder is committed to the repository root.
