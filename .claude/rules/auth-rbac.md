---
description: Role definitions, elevation codes, demo credentials, and the security limitations of the prototype auth system
alwaysApply: true
---

## Roles

```js
const ROLES = { STUDENT: 'student', TEACHER: 'teacher', ADMIN: 'admin' }
```

`canAccess(requiredRole)` enforces hierarchy: student < teacher < admin.

## Elevation Codes

- `TEACH2025` → teacher
- `ADMIN2025` → admin
- (none) → student

## Demo Accounts

```
admin@crypto-course.edu / admin123
teacher@crypto-course.edu / teach123  (Dr. Hassan)
student@crypto-course.edu / student123
```

## Security Limitations (Prototype)

Tokens are base64-only (not signed). Passwords stored as plaintext in localStorage. Production requires server-side hashing and signed JWTs.
