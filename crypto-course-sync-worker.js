/**
 * Crypto-Course — Minimal Sync Backend (Cloudflare Worker + KV)
 * ------------------------------------------------------------------
 * Matches the app's existing client contract:
 *   PUT  {base}/{userId}      store a student's minimal progress payload
 *   GET  {base}/{userId}      read one student back (the student's own pull)
 *   GET  {base}/__ping        health check (testSyncConnection)
 * Adds the teacher aggregation read the dashboard needs:
 *   GET  {base}/cohort/{code} all students in a cohort (teacher-gated)
 *
 * Auth model (pilot-grade — see SPEC threat model):
 *   - Students send a per-cohort WRITE token (Authorization: Bearer <token>).
 *     The token identifies the cohort; the worker stores under that cohort.
 *   - Teachers send a per-cohort TEACHER token for the cohort read.
 *
 * Storage (KV namespace bound as `SYNC`):
 *   student:{cohort}:{userId}  ->  { payload, updatedAt }
 *
 * Required env / secrets (set via wrangler):
 *   ALLOWED_ORIGINS  comma-separated origins, e.g.
 *                    "https://you.github.io,http://localhost:8080"
 *   COHORTS_JSON     JSON map of cohort -> tokens, e.g.
 *                    {"WMIN2026":{"write":"w_xxx","teacher":"t_yyy"}}
 */

const MAX_BODY_BYTES = 16 * 1024;          // reject oversized payloads
const RETENTION_DAYS = 180;                // KV TTL for student records

/* ---- PR13 allowlist: server-side minimisation (defensive) ---- */
const ALLOWED_TOP = ['xpDelta', 'streak', 'badgeTimestamps', 'quizOutcomes', 'labCompletions', 'sessionDuration'];
const ALLOWED_QUIZ = ['quizzesCompleted', 'perfectQuizzes', 'lessonsCompleted', 'freezeTokens',
  'moduleProgress', 'quizAttempts', 'spacedRevisits', 'diagnosticDone', 'metroBadgeEarned', 'lastChallengeDate'];
const ALLOWED_LAB = ['count', 'done'];

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = request.headers.get('Origin') || '';
    const cors = corsHeaders(origin, env);

    // CORS preflight
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });

    // Health check
    if (url.pathname === '/__ping') return json({ ok: true }, 200, cors);

    const cohorts = parseCohorts(env);

    try {
      // Teacher cohort read:  GET /cohort/{code}
      const cohortMatch = url.pathname.match(/^\/cohort\/([^/]+)\/?$/);
      if (cohortMatch && request.method === 'GET') {
        const code = decodeURIComponent(cohortMatch[1]);
        const conf = cohorts[code];
        if (!conf) return json({ error: 'unknown cohort' }, 404, cors);
        if (bearer(request) !== conf.teacher) return json({ error: 'unauthorized' }, 401, cors);

        const list = await env.SYNC.list({ prefix: `student:${code}:` });
        const out = [];
        for (const k of list.keys) {
          const rec = await env.SYNC.get(k.name, 'json');
          if (rec) out.push({ userId: k.name.split(':').slice(2).join(':'), name: rec.name || '', role: rec.role || 'student', emailVerified: rec.emailVerified || false, registeredAt: rec.registeredAt || null, updatedAt: rec.updatedAt || null, payload: rec.payload || null });
        }
        return json({ cohort: code, count: out.length, students: out }, 200, cors);
      }

      // Approval route:  PUT /approve/{userId}  (teacher token auth)
      const approveMatch = url.pathname.match(/^\/approve\/([^/]+)\/?$/);
      if (approveMatch && request.method === 'PUT') {
        const userId = decodeURIComponent(approveMatch[1]);
        const approved = isTeacher(bearer(request), cohorts);
        if (!approved) return json({ error: 'unauthorized' }, 401, cors);
        // Find the student's record across all cohorts
        const list = await env.SYNC.list({ prefix: 'student:' });
        for (const k of list.keys) {
          if (k.name.endsWith(':' + userId)) {
            const rec = (await env.SYNC.get(k.name, 'json')) || {};
            rec.emailVerified = true;
            await env.SYNC.put(k.name, JSON.stringify(rec), { expirationTtl: RETENTION_DAYS * 86400 });
            return json({ ok: true }, 200, cors);
          }
        }
        return json({ error: 'student not found' }, 404, cors);
      }

      // Registration route:  PUT /register/{userId}
      // Stores name + role in the KV record without overwriting progress payload.
      const registerMatch = url.pathname.match(/^\/register\/([^/]+)\/?$/);
      if (registerMatch && request.method === 'PUT') {
        const userId = decodeURIComponent(registerMatch[1]);
        const cohort = cohortForWriteToken(bearer(request), cohorts);
        if (!cohort) return json({ error: 'unauthorized' }, 401, cors);
        const raw = await request.text();
        if (raw.length > 512) return json({ error: 'payload too large' }, 413, cors);
        let body;
        try { body = JSON.parse(raw); } catch { return json({ error: 'invalid JSON' }, 400, cors); }
        const key = `student:${cohort}:${userId}`;
        const existing = (await env.SYNC.get(key, 'json')) || {};
        const updated = {
          ...existing,
          name: String(body.name || '').substring(0, 100),
          role: String(body.role || 'student'),
          registeredAt: existing.registeredAt || new Date().toISOString(),
        };
        await env.SYNC.put(key, JSON.stringify(updated), { expirationTtl: RETENTION_DAYS * 86400 });
        return json({ ok: true }, 200, cors);
      }

      // List all semesters (public — used by students to browse before enrolling)
      if (url.pathname === '/semesters' && request.method === 'GET') {
        const list = await env.SYNC.list({ prefix: 'semester:' });
        const out = [];
        for (const k of list.keys) {
          const rec = await env.SYNC.get(k.name, 'json');
          if (!rec) continue;
          const studentList = rec.cohort
            ? await env.SYNC.list({ prefix: `student:${rec.cohort}:` })
            : { keys: [] };
          out.push({ code: rec.code, name: rec.name, startDate: rec.startDate, endDate: rec.endDate, enrolledCount: studentList.keys.length });
        }
        return json({ semesters: out }, 200, cors);
      }

      // Semester routes:  GET/PUT /semester/{code}
      // PUT (write token auth) — teacher pushes semester metadata so students can enrol cross-device
      // GET (no auth)          — student fetches by join code; response includes writeToken so sync works immediately
      const semesterMatch = url.pathname.match(/^\/semester\/([^/]+)\/?$/);
      if (semesterMatch) {
        const code = decodeURIComponent(semesterMatch[1]).toUpperCase();
        const key = `semester:${code}`;

        if (request.method === 'GET') {
          const rec = await env.SYNC.get(key, 'json');
          if (!rec) return new Response(null, { status: 204, headers: cors });
          return json(rec, 200, cors);
        }

        if (request.method === 'PUT') {
          const cohort = cohortForWriteToken(bearer(request), cohorts);
          if (!cohort) return json({ error: 'unauthorized' }, 401, cors);
          const raw = await request.text();
          if (raw.length > 2048) return json({ error: 'payload too large' }, 413, cors);
          let body;
          try { body = JSON.parse(raw); } catch { return json({ error: 'invalid JSON' }, 400, cors); }
          const clean = {
            id:         String(body.id        || ''),
            name:       String(body.name      || ''),
            startDate:  String(body.startDate || ''),
            endDate:    String(body.endDate   || ''),
            code,
            cohort,
            writeToken: String(body.writeToken || ''),
          };
          await env.SYNC.put(key, JSON.stringify(clean), { expirationTtl: RETENTION_DAYS * 86400 });
          return json({ ok: true }, 200, cors);
        }
      }

      // Student list by semester code:  GET /students/{semCode}  (teacher token auth)
      // Looks up the semester's cohort internally — teacher only needs the semester code.
      const studentsMatch = url.pathname.match(/^\/students\/([^/]+)\/?$/);
      if (studentsMatch && request.method === 'GET') {
        if (!isTeacher(bearer(request), cohorts)) return json({ error: 'unauthorized' }, 401, cors);
        const semCode = decodeURIComponent(studentsMatch[1]).toUpperCase();
        const semRec = await env.SYNC.get(`semester:${semCode}`, 'json');
        if (!semRec) return json({ error: 'semester not found' }, 404, cors);
        const cohort = semRec.cohort;
        const list = await env.SYNC.list({ prefix: `student:${cohort}:` });
        const out = [];
        for (const k of list.keys) {
          const rec = await env.SYNC.get(k.name, 'json');
          if (rec) out.push({ userId: k.name.split(':').slice(2).join(':'), name: rec.name || '', role: rec.role || 'student', emailVerified: rec.emailVerified || false, registeredAt: rec.registeredAt || null, updatedAt: rec.updatedAt || null, payload: rec.payload || null });
        }
        return json({ semCode, cohort, count: out.length, students: out }, 200, cors);
      }

      // Per-student routes:  /{userId}
      const userMatch = url.pathname.match(/^\/([^/]+)\/?$/);
      if (userMatch) {
        const userId = decodeURIComponent(userMatch[1]);
        const cohort = cohortForWriteToken(bearer(request), cohorts);
        if (!cohort) return json({ error: 'unauthorized' }, 401, cors);
        const key = `student:${cohort}:${userId}`;

        if (request.method === 'GET') {
          const rec = await env.SYNC.get(key, 'json');
          if (!rec) return new Response(null, { status: 204, headers: cors });
          return json({ ...(rec.payload || {}), emailVerified: rec.emailVerified || false }, 200, cors);
        }

        if (request.method === 'PUT') {
          const raw = await request.text();
          if (raw.length > MAX_BODY_BYTES) return json({ error: 'payload too large' }, 413, cors);
          let body;
          try { body = JSON.parse(raw); } catch { return json({ error: 'invalid JSON' }, 400, cors); }
          const clean = sanitise(body);                 // strip anything not on the allowlist
          await env.SYNC.put(key, JSON.stringify({ payload: clean, updatedAt: new Date().toISOString() }),
            { expirationTtl: RETENTION_DAYS * 86400 });
          return json({ ok: true }, 200, cors);
        }
      }

      return json({ error: 'not found' }, 404, cors);
    } catch (e) {
      return json({ error: 'server error' }, 500, cors);
    }
  }
};

/* ---------------- helpers ---------------- */

function corsHeaders(origin, env) {
  const allowed = (env.ALLOWED_ORIGINS || '').split(',').map(s => s.trim()).filter(Boolean);
  const allow = allowed.includes(origin) ? origin : (allowed[0] || '*');
  return {
    'Access-Control-Allow-Origin': allow,
    'Access-Control-Allow-Methods': 'GET, PUT, OPTIONS',
    'Access-Control-Allow-Headers': 'Authorization, Content-Type',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}

function json(obj, status, cors) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json', ...cors },
  });
}

function bearer(request) {
  const h = request.headers.get('Authorization') || '';
  const m = h.match(/^Bearer\s+(.+)$/i);
  return m ? m[1].trim() : '';
}

function parseCohorts(env) {
  try { return JSON.parse(env.COHORTS_JSON || '{}'); } catch { return {}; }
}

function isTeacher(token, cohorts) {
  if (!token) return false;
  return Object.values(cohorts).some(c => c.teacher && c.teacher === token);
}

function cohortForWriteToken(token, cohorts) {
  if (!token) return null;
  for (const [code, conf] of Object.entries(cohorts)) {
    if (conf.write && conf.write === token) return code;
  }
  return null;
}

/* PR13 minimisation: rebuild a clean object containing only allowed fields. */
function sanitise(body) {
  const out = {};
  for (const k of ALLOWED_TOP) {
    if (!(k in body)) continue;
    if (k === 'quizOutcomes' && body.quizOutcomes && typeof body.quizOutcomes === 'object') {
      const q = {};
      for (const sk of ALLOWED_QUIZ) if (sk in body.quizOutcomes) q[sk] = body.quizOutcomes[sk];
      out.quizOutcomes = q;
    } else if (k === 'labCompletions' && body.labCompletions && typeof body.labCompletions === 'object') {
      const l = {};
      for (const sk of ALLOWED_LAB) if (sk in body.labCompletions) l[sk] = body.labCompletions[sk];
      out.labCompletions = l;
    } else {
      out[k] = body[k];
    }
  }
  return out;
}
