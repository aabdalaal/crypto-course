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

const MAX_BODY_BYTES        = 16 * 1024;   // reject oversized student payloads
const MAX_ADMIN_BACKUP_BYTES = 512 * 1024; // admin backup can be larger
const MAX_CONTENT_BYTES     = 1024 * 1024; // content registry (videos, flowcharts, modules)
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
          if (rec) out.push({ userId: k.name.split(':').slice(2).join(':'), name: rec.name || '', email: rec.email || '', role: rec.role || 'student', emailVerified: rec.emailVerified || false, registeredAt: rec.registeredAt || null, updatedAt: rec.updatedAt || null, payload: rec.payload || null });
        }
        return json({ cohort: code, count: out.length, students: out }, 200, cors);
      }

      // Teacher account management routes (all require teacher token)
      const mgmtMatch = url.pathname.match(/^\/(approve|suspend|unsuspend|update|student)\/([^/]+)\/?$/);
      if (mgmtMatch) {
        const [, action, rawId] = mgmtMatch;
        const userId = decodeURIComponent(rawId);
        if (!isTeacher(bearer(request), cohorts)) return json({ error: 'unauthorized' }, 401, cors);

        // DELETE /student/{userId} — remove from cohort
        if (action === 'student' && request.method === 'DELETE') {
          const list = await env.SYNC.list({ prefix: 'student:' });
          for (const k of list.keys) {
            if (k.name.endsWith(':' + userId)) {
              await env.SYNC.delete(k.name);
              return json({ ok: true }, 200, cors);
            }
          }
          return json({ error: 'not found' }, 404, cors);
        }

        // PUT /approve|suspend|unsuspend|update/{userId}
        if (request.method === 'PUT') {
          const list = await env.SYNC.list({ prefix: 'student:' });
          for (const k of list.keys) {
            if (k.name.endsWith(':' + userId)) {
              const rec = (await env.SYNC.get(k.name, 'json')) || {};
              if (action === 'approve')   rec.emailVerified = true;
              if (action === 'suspend')   rec.suspended = true;
              if (action === 'unsuspend') rec.suspended = false;
              if (action === 'update') {
                const body = await request.json().catch(() => ({}));
                if (body.name) rec.name = String(body.name).substring(0, 100);
              }
              await env.SYNC.put(k.name, JSON.stringify(rec), { expirationTtl: RETENTION_DAYS * 86400 });
              return json({ ok: true }, 200, cors);
            }
          }
          return json({ error: 'not found' }, 404, cors);
        }
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
        if (raw.length > 1024) return json({ error: 'payload too large' }, 413, cors);
        let body;
        try { body = JSON.parse(raw); } catch { return json({ error: 'invalid JSON' }, 400, cors); }
        const key = `student:${cohort}:${userId}`;
        const existing = (await env.SYNC.get(key, 'json')) || {};
        const updated = {
          ...existing,
          name:  String(body.name  || '').substring(0, 100),
          email: String(body.email || '').substring(0, 200),
          role:  String(body.role  || 'student'),
          registeredAt: existing.registeredAt || new Date().toISOString(),
        };
        // Store credential hash for cross-device account recovery (never plaintext password)
        if (body.passwordHash && body.passwordSalt) {
          updated.passwordHash = String(body.passwordHash).substring(0, 128);
          updated.passwordSalt = String(body.passwordSalt).substring(0, 64);
          if (typeof body.passwordIter === 'number') updated.passwordIter = body.passwordIter;
        }
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
          if (rec) out.push({ userId: k.name.split(':').slice(2).join(':'), name: rec.name || '', email: rec.email || '', role: rec.role || 'student', emailVerified: rec.emailVerified || false, suspended: rec.suspended || false, registeredAt: rec.registeredAt || null, updatedAt: rec.updatedAt || null, payload: rec.payload || null });
        }
        return json({ semCode, cohort, count: out.length, students: out }, 200, cors);
      }

      // ── Email verification ──────────────────────────────────────────────────
      //   POST /verify/send   — generate code, store in KV, email to student
      //   POST /verify/check  — validate code, mark student emailVerified
      // ───────────────────────────────────────────────────────────────────────

      if (url.pathname === '/verify/send' && request.method === 'POST') {
        const cohort = cohortForWriteToken(bearer(request), cohorts);
        if (!cohort) return json({ error: 'unauthorized' }, 401, cors);
        const raw = await request.text();
        if (raw.length > 512) return json({ error: 'payload too large' }, 413, cors);
        let body;
        try { body = JSON.parse(raw); } catch { return json({ error: 'invalid JSON' }, 400, cors); }
        const { userId, email, name } = body;
        if (!userId || !email) return json({ error: 'missing userId or email' }, 400, cors);
        const code = String(Math.floor(100000 + Math.random() * 900000));
        await env.SYNC.put(`verify:${userId}`, JSON.stringify({
          code, email, name: String(name || ''), attempts: 0,
          expiresAt: new Date(Date.now() + 86400000).toISOString(),
        }), { expirationTtl: 86400 });
        await sendVerificationEmail(env, email, name || 'Student', code);
        return json({ ok: true }, 200, cors);
      }

      if (url.pathname === '/verify/check' && request.method === 'POST') {
        const raw = await request.text();
        let body;
        try { body = JSON.parse(raw); } catch { return json({ error: 'invalid JSON' }, 400, cors); }
        const { userId, code } = body;
        if (!userId || !code) return json({ error: 'missing fields' }, 400, cors);
        const key = `verify:${userId}`;
        const rec = await env.SYNC.get(key, 'json');
        if (!rec) return json({ error: 'no pending verification — request a new code' }, 404, cors);
        if (new Date(rec.expiresAt) < new Date()) {
          await env.SYNC.delete(key);
          return json({ error: 'code expired' }, 410, cors);
        }
        if (rec.attempts >= 5) return json({ error: 'too many attempts — request a new code' }, 429, cors);
        if (rec.code !== String(code).trim()) {
          rec.attempts++;
          await env.SYNC.put(key, JSON.stringify(rec), { expirationTtl: 86400 });
          return json({ error: 'invalid code', attemptsLeft: 5 - rec.attempts }, 400, cors);
        }
        await env.SYNC.delete(key);
        // Mark student as verified in their KV record
        const list = await env.SYNC.list({ prefix: 'student:' });
        for (const k of list.keys) {
          if (k.name.endsWith(':' + userId)) {
            const sr = (await env.SYNC.get(k.name, 'json')) || {};
            sr.emailVerified = true;
            await env.SYNC.put(k.name, JSON.stringify(sr), { expirationTtl: RETENTION_DAYS * 86400 });
            break;
          }
        }
        return json({ ok: true }, 200, cors);
      }

      // Admin backup:  GET /admin-backup  |  PUT /admin-backup
      if (url.pathname === '/admin-backup') {
        const cohort = cohortForTeacherToken(bearer(request), cohorts);
        if (!cohort) return json({ error: 'unauthorized' }, 401, cors);
        const key = `admin-backup:${cohort}`;

        if (request.method === 'GET') {
          const rec = await env.SYNC.get(key, 'json');
          if (!rec) return new Response(null, { status: 204, headers: cors });
          return json(rec, 200, cors);
        }

        if (request.method === 'PUT') {
          const raw = await request.text();
          if (raw.length > MAX_ADMIN_BACKUP_BYTES) return json({ error: 'payload too large' }, 413, cors);
          let body;
          try { body = JSON.parse(raw); } catch { return json({ error: 'invalid JSON' }, 400, cors); }
          if (!body.version || !body.data) return json({ error: 'invalid backup format' }, 400, cors);
          await env.SYNC.put(key, JSON.stringify(body), { expirationTtl: RETENTION_DAYS * 86400 });
          return json({ ok: true }, 200, cors);
        }
      }

      // Content registry:  GET /content  |  PUT /content
      // PUT — teacher pushes updated module content (videos, flowcharts, custom modules)
      // GET — student pulls on sync; returns the cohort's published content
      if (url.pathname === '/content') {
        if (request.method === 'PUT') {
          const cohort = cohortForTeacherToken(bearer(request), cohorts);
          if (!cohort) return json({ error: 'unauthorized' }, 401, cors);
          const raw = await request.text();
          if (raw.length > MAX_CONTENT_BYTES) return json({ error: 'payload too large' }, 413, cors);
          let body;
          try { body = JSON.parse(raw); } catch { return json({ error: 'invalid JSON' }, 400, cors); }
          await env.SYNC.put(`content:${cohort}`, JSON.stringify({ ...body, pushed_at: new Date().toISOString() }),
            { expirationTtl: RETENTION_DAYS * 86400 });
          return json({ ok: true }, 200, cors);
        }
        if (request.method === 'GET') {
          const cohort = cohortForWriteToken(bearer(request), cohorts);
          if (!cohort) return json({ error: 'unauthorized' }, 401, cors);
          const rec = await env.SYNC.get(`content:${cohort}`, 'json');
          if (!rec) return new Response(null, { status: 204, headers: cors });
          return json(rec, 200, cors);
        }
      }

      // Cross-device account recovery:  GET /account-by-email/{email}
      // No auth required — only returns a PBKDF2 hash (never plaintext).
      // Searched across all cohorts so a fresh device with no write token can recover.
      const accountByEmailMatch = url.pathname.match(/^\/account-by-email\/([^/]+)\/?$/);
      if (accountByEmailMatch && request.method === 'GET') {
        const email = decodeURIComponent(accountByEmailMatch[1]).toLowerCase();
        const list = await env.SYNC.list({ prefix: 'student:' });
        for (const k of list.keys) {
          const rec = await env.SYNC.get(k.name, 'json');
          if (rec && (rec.email || '').toLowerCase() === email && rec.passwordHash) {
            const parts = k.name.split(':'); // student:{cohort}:{userId}
            const cohort = parts[1];
            const userId = parts.slice(2).join(':');
            const writeToken = cohorts[cohort]?.write || '';
            return json({
              id: userId, name: rec.name || '', email: rec.email || '',
              role: rec.role || 'student', emailVerified: rec.emailVerified || false,
              passwordHash: rec.passwordHash, passwordSalt: rec.passwordSalt,
              passwordIter: rec.passwordIter,
              writeToken,           // lets the new device call pullSync() immediately
              payload: rec.payload || null, // existing progress for offline restore
            }, 200, cors);
          }
        }
        return new Response(null, { status: 204, headers: cors });
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
          return json({ ...(rec.payload || {}), emailVerified: rec.emailVerified || false, suspended: rec.suspended || false }, 200, cors);
        }

        if (request.method === 'PUT') {
          const raw = await request.text();
          if (raw.length > MAX_BODY_BYTES) return json({ error: 'payload too large' }, 413, cors);
          let body;
          try { body = JSON.parse(raw); } catch { return json({ error: 'invalid JSON' }, 400, cors); }
          const clean = sanitise(body);                 // strip anything not on the allowlist
          // Merge with existing record to preserve name/role/emailVerified set by /register
          const existing = (await env.SYNC.get(key, 'json')) || {};
          await env.SYNC.put(key, JSON.stringify({ ...existing, payload: clean, updatedAt: new Date().toISOString() }),
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
    'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS',
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

async function sendVerificationEmail(env, email, name, code) {
  if (!env.RESEND_API_KEY) return; // skip silently if not configured
  const from = env.FROM_EMAIL || 'CryptoCourse <onboarding@resend.dev>';
  await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from,
      to: [email],
      subject: 'Your CryptoCourse verification code',
      text: `Hi ${name},\n\nYour CryptoCourse verification code is:\n\n    ${code}\n\nEnter this code in the app. It expires in 24 hours.\n\nIf you did not sign up for CryptoCourse, you can safely ignore this email.`,
    }),
  }).catch(() => {}); // fire-and-forget; don't fail the route if email fails
}

function cohortForTeacherToken(token, cohorts) {
  if (!token) return null;
  for (const [code, conf] of Object.entries(cohorts)) {
    if (conf.teacher && conf.teacher === token) return code;
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
