// ============================================================
// Crypto-Course Service Worker
// Offline-first PWA — app shell + CDN asset caching
//
// CACHE VERSIONING:
//   Bump VERSION when the app shell HTML changes so the SW
//   update cycle clears stale caches and re-fetches the file.
//
// CACHE STRATEGY:
//   cc-shell-{ver}  Cache-first, updated on SW install.
//                   Covers the HTML app shell, manifest, icon.
//   cc-cdn-{ver}    Cache-first (long-lived).
//                   Covers Chart.js, Mermaid.js, Google Fonts.
//   cc-img-{ver}    Network-first, cache fallback.
//                   Covers YouTube thumbnails (optional, nice UX).
// ============================================================

const VERSION      = 'v5';
const SHELL_CACHE  = `cc-shell-${VERSION}`;
const CDN_CACHE    = `cc-cdn-${VERSION}`;
const IMG_CACHE    = `cc-img-${VERSION}`;
const ALL_CACHES   = [SHELL_CACHE, CDN_CACHE, IMG_CACHE];

// Files that must be available offline immediately after install.
// The HTML filename must match the actual file being served.
const SHELL_PRECACHE = [
  './index.html',
  './manifest.json',
  './icon.svg',
  './icon-180.png',
  './icon-192.png',
  './icon-512.png',
  './icon-512-maskable.png',
  './favicon-32.png',
];

// Chart.js and Mermaid.js are now lazy-loaded on first use — they are
// NOT pre-fetched at install time so the install budget stays small.
// They will be cached on first fetch by the cacheFirst handler in the
// fetch event below.  An empty array keeps the install logic unchanged.
const CDN_PRECACHE = [];

// ── MESSAGE ──────────────────────────────────────────────────
// The app page sends SKIP_WAITING when the user taps "Reload"
// on the update banner — activates the new SW immediately.
self.addEventListener('message', event => {
  if (event.data?.type === 'SKIP_WAITING') self.skipWaiting();
});

// ── INSTALL ─────────────────────────────────────────────────
// Pre-cache the app shell synchronously so the app works
// offline immediately after the first online visit.
self.addEventListener('install', event => {
  event.waitUntil(
    (async () => {
      // App shell — must succeed; if any file fails, install fails.
      const shellCache = await caches.open(SHELL_CACHE);
      await shellCache.addAll(SHELL_PRECACHE);

      // CDN assets — best-effort: a CDN miss should not abort
      // install (the user may be re-installing offline).
      const cdnCache = await caches.open(CDN_CACHE);
      await Promise.allSettled(
        CDN_PRECACHE.map(url =>
          cdnCache.add(url).catch(() => {
            console.warn('[SW] CDN pre-cache miss (will retry on fetch):', url);
          })
        )
      );

      // Take over immediately — do not wait for tabs to close.
      await self.skipWaiting();
    })()
  );
});

// ── ACTIVATE ────────────────────────────────────────────────
// Delete every cache whose name is not in ALL_CACHES.
// This removes caches from previous VERSION values.
self.addEventListener('activate', event => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys
          .filter(k => !ALL_CACHES.includes(k))
          .map(k => caches.delete(k))
      );
      // Claim all open tabs immediately.
      await self.clients.claim();
    })()
  );
});

// ── FETCH ────────────────────────────────────────────────────

self.addEventListener('fetch', event => {
  const req = event.request;
  const url = new URL(req.url);

  // Only handle GET requests.
  if (req.method !== 'GET') return;

  // ── 0. Navigation requests (bare / or /repo/) ────────────
  // Installed PWA opens at start_url (./) which never matches
  // the .html pathname check below. Return the cached shell so
  // the app opens offline from the home-screen shortcut.
  if (req.mode === 'navigate') {
    event.respondWith(
      caches.match('./index.html').then(r => r || fetch(req))
    );
    return;
  }

  // ── 1. App shell (same origin .html) ─────────────────────
  // Cache-first with a network refresh in the background.
  // If the network returns a newer version the next load uses it.
  if (url.origin === self.location.origin && url.pathname.endsWith('.html')) {
    event.respondWith(staleWhileRevalidate(req, SHELL_CACHE));
    return;
  }

  // ── 2. Manifest and icon (same origin static files) ──────
  if (url.origin === self.location.origin &&
      (url.pathname.endsWith('.json') || url.pathname.endsWith('.svg') || url.pathname.endsWith('.png'))) {
    event.respondWith(cacheFirst(req, SHELL_CACHE));
    return;
  }

  // ── 3. CDN scripts and fonts ─────────────────────────────
  // chart.js, mermaid, Google Fonts CSS + woff2
  if (
    url.hostname === 'cdn.jsdelivr.net' ||
    url.hostname === 'fonts.googleapis.com' ||
    url.hostname === 'fonts.gstatic.com'
  ) {
    event.respondWith(cacheFirst(req, CDN_CACHE));
    return;
  }

  // ── 4. YouTube thumbnails ─────────────────────────────────
  // Network-first; cache the thumbnail so it shows when offline.
  if (url.hostname === 'i.ytimg.com') {
    event.respondWith(networkFirst(req, IMG_CACHE));
    return;
  }

  // ── 5. Everything else (YouTube embeds, external links) ──
  // Passthrough — do not cache.
  // event.respondWith(fetch(req)); // implicit — let browser handle
});

// ── HELPERS ──────────────────────────────────────────────────

/**
 * Cache-first: return from cache; if absent, fetch, cache, return.
 */
async function cacheFirst(req, cacheName) {
  const cache    = await caches.open(cacheName);
  const cached   = await cache.match(req);
  if (cached) return cached;

  try {
    const response = await fetch(req);
    if (response.ok) cache.put(req, response.clone());
    return response;
  } catch (err) {
    // Offline and not cached — nothing we can do.
    return new Response('Offline and not cached.', { status: 503 });
  }
}

/**
 * Stale-while-revalidate: return cached version immediately,
 * then fetch a fresh copy in the background and update cache.
 * Notifies open tabs when a new shell version is ready.
 */
async function staleWhileRevalidate(req, cacheName) {
  const cache  = await caches.open(cacheName);
  const cached = await cache.match(req);

  const fetchPromise = fetch(req).then(async response => {
    if (response.ok) {
      await cache.put(req, response.clone());
      // Notify all open tabs that an updated shell is cached.
      const clients = await self.clients.matchAll({ type: 'window' });
      clients.forEach(client => client.postMessage({ type: 'SW_SHELL_UPDATED' }));
    }
    return response;
  }).catch(() => null);

  return cached || fetchPromise;
}

/**
 * Network-first: try network, fall back to cache.
 * Used for resources that change (thumbnails).
 */
async function networkFirst(req, cacheName) {
  const cache = await caches.open(cacheName);
  try {
    const response = await fetch(req);
    if (response.ok) cache.put(req, response.clone());
    return response;
  } catch {
    const cached = await cache.match(req);
    return cached || new Response('', { status: 503 });
  }
}
