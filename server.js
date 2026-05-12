// Local dev server — explicit MIME types so sw.js is never served as text/plain
// Also serves the /api/sync/:userId endpoint for multi-device progress sync (PR13)
const http = require('http');
const fs   = require('fs');
const path = require('path');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js':   'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg':  'image/svg+xml',
  '.css':  'text/css; charset=utf-8',
  '.png':  'image/png',
  '.ico':  'image/x-icon',
  '.woff2':'font/woff2',
  '.woff': 'font/woff',
};

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, PUT, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

const PORT     = process.argv[2] || 8000;
const ROOT     = __dirname;
const DATA_DIR = path.join(ROOT, 'sync-data');

if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });

http.createServer((req, res) => {
  // Apply CORS headers to every response
  Object.entries(CORS).forEach(([k, v]) => res.setHeader(k, v));

  // Pre-flight
  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }

  // ── Sync API ─────────────────────────────────────────────────
  // GET  /api/sync/:userId  → return stored payload (204 if none)
  // PUT  /api/sync/:userId  → store payload (must be valid JSON, ≤500 KB)
  const syncMatch = req.url.match(/^\/api\/sync\/([a-zA-Z0-9_@.-]+)$/);
  if (syncMatch) {
    // Sanitise userId to a safe filename (keep only alphanumeric + _ - @.)
    const userId = syncMatch[1].replace(/[^a-zA-Z0-9_@.-]/g, '_');
    const file   = path.join(DATA_DIR, userId + '.json');

    if (req.method === 'GET') {
      if (!fs.existsSync(file)) { res.writeHead(204); res.end(); return; }
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(fs.readFileSync(file));
      return;
    }

    if (req.method === 'PUT') {
      let body = '';
      req.on('data', chunk => {
        body += chunk;
        if (body.length > 512_000) { res.writeHead(413); res.end('{"error":"payload too large"}'); }
      });
      req.on('end', () => {
        try {
          JSON.parse(body); // validate JSON before writing
          fs.writeFileSync(file, body, 'utf8');
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end('{"ok":true}');
        } catch (e) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end('{"error":"invalid json"}');
        }
      });
      return;
    }

    res.writeHead(405); res.end('Method Not Allowed');
    return;
  }

  // ── Static file serving ──────────────────────────────────────
  let urlPath = req.url.split('?')[0];
  if (urlPath === '/') urlPath = '/crypto_course_app.html';

  const filePath = path.join(ROOT, urlPath);
  const ext      = path.extname(filePath).toLowerCase();
  const mime     = MIME[ext] || 'application/octet-stream';

  fs.readFile(filePath, (err, data) => {
    if (err) { res.writeHead(404); res.end('Not found'); return; }
    res.writeHead(200, { 'Content-Type': mime });
    res.end(data);
  });
}).listen(PORT, () => console.log(`Serving at http://localhost:${PORT}/  |  Sync API at http://localhost:${PORT}/api/sync/`));
