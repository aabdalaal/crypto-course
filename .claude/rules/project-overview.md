---
description: What the Crypto-Course app is, who it's for, and why every feature decision must be checked against research paper requirements
alwaysApply: true
---

**Crypto-Course** is an offline-first, mobile-first cryptography education platform for learners in resource-constrained and conflict-affected environments (war zones, low-connectivity regions, unreliable power).

It implements two University of Westminster research papers:
- **Paper 2** (*Designing for the Digital Exclusion Nexus*) — technology selection framework; concludes React+Node.js+SQLite (or single-file PWA) is optimal for 17 technical requirements.
- **Paper 3** (*Pedagogical Design of a Gamified Offline-First Cryptography Learning Platform*) — 14 Pedagogical Requirements (PR1–PR14), each with a falsifiable acceptance criterion.

**When modifying any feature, check whether it touches a PR or technical requirement — changing it may invalidate a compliance claim.**

**Target users:** Learners in Gaza, Lebanon, Ukraine, and similar conflict-affected contexts. Platform assumes: intermittent or zero connectivity, low-end Android (2GB RAM, dual-core, 720p), shared devices, fragmented study sessions, no instructor presence.
