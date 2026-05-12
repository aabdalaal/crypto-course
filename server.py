#!/usr/bin/env python3
"""
Local dev server for Crypto-Course.
Overrides guess_type() so Windows Registry MIME mappings cannot interfere
(fixes .js served as text/plain breaking SW registration).
Also serves /api/sync/:userId  GET + PUT for multi-device progress sync.

Usage:
    python server.py          # serves on http://localhost:8000
    python server.py 9000     # custom port
"""
import http.server
import json
import os
import re
import sys

MIME_OVERRIDES = {
    '.js':          'application/javascript',
    '.mjs':         'application/javascript',
    '.json':        'application/json',
    '.webmanifest': 'application/manifest+json',
    '.svg':         'image/svg+xml',
    '.css':         'text/css',
    '.html':        'text/html',
    '.htm':         'text/html',
    '.woff2':       'font/woff2',
    '.woff':        'font/woff',
}

SYNC_DIR = os.path.join(os.path.dirname(__file__), 'sync-data')
os.makedirs(SYNC_DIR, exist_ok=True)

CORS_HEADERS = {
    'Access-Control-Allow-Origin':  '*',
    'Access-Control-Allow-Methods': 'GET, PUT, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
}

def safe_user_id(raw):
    """Sanitise userId to a safe filename."""
    return re.sub(r'[^a-zA-Z0-9_@.\-]', '_', raw)


class Handler(http.server.SimpleHTTPRequestHandler):

    # ── CORS pre-flight ───────────────────────────────────────────
    def do_OPTIONS(self):
        self.send_response(204)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()

    # ── Sync API — PUT /api/sync/:userId ──────────────────────────
    def do_PUT(self):
        m = re.match(r'^/api/sync/([^/?]+)$', self.path)
        if not m:
            self.send_error(404)
            return
        user_id = safe_user_id(m.group(1))
        length  = int(self.headers.get('Content-Length', 0))
        if length > 512_000:
            self.send_error(413, 'Payload too large')
            return
        body = self.rfile.read(length)
        try:
            json.loads(body)          # validate JSON
        except ValueError:
            self.send_error(400, 'Invalid JSON')
            return
        file_path = os.path.join(SYNC_DIR, user_id + '.json')
        with open(file_path, 'wb') as f:
            f.write(body)
        self._json_response(200, {'ok': True})

    # ── Sync API — GET /api/sync/:userId ──────────────────────────
    def do_GET(self):
        m = re.match(r'^/api/sync/([^/?]+)$', self.path)
        if m:
            user_id   = safe_user_id(m.group(1))
            file_path = os.path.join(SYNC_DIR, user_id + '.json')
            if not os.path.exists(file_path):
                self.send_response(204)
                for k, v in CORS_HEADERS.items():
                    self.send_header(k, v)
                self.end_headers()
                return
            with open(file_path, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            for k, v in CORS_HEADERS.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(data)
            return
        # Fall through to normal static-file serving
        super().do_GET()

    # ── Helper ────────────────────────────────────────────────────
    def _json_response(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def guess_type(self, path):
        for ext, mime in MIME_OVERRIDES.items():
            if str(path).endswith(ext):
                return mime
        return super().guess_type(path)

    def log_message(self, fmt, *args):
        print(f'  {self.address_string()} — {fmt % args}')


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
# Bind to 0.0.0.0 so mobile devices on the same WiFi can connect
import socket
local_ip = socket.gethostbyname(socket.gethostname())
print(f'Serving at http://localhost:{port}/ and http://{local_ip}:{port}/')
print(f'Sync API at http://{local_ip}:{port}/api/sync/')
http.server.test(HandlerClass=Handler, port=port, bind='0.0.0.0')
