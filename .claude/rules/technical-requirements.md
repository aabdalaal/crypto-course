---
description: 17 technical requirements from Paper 2 grouped by the 6 dimensions of the digital exclusion nexus
alwaysApply: true
---

The 17 technical requirements from Paper 2 are grouped under 6 dimensions of the **digital exclusion nexus**:

| Dimension | Requirements |
|-----------|-------------|
| **Connectivity** | R1: 100% offline core features · R2: <500MB/sync update · R3: Opportunistic background sync |
| **Device** | R4: Android 8+, 2GB RAM · R5: <300MB active memory · R6: 720p touch-first UI · R7: <4GB total storage |
| **Performance** | R8: <3s initial load · R9: <5% battery/hour · R10: Dual-core CPU compatible |
| **Accessibility** | R11: WCAG 2.1 AA · R12: Screen reader + keyboard nav · R13: RTL language support |
| **Deployment** | R14: Single-server operation · R15: File-based backup |
| **Community** | R16: Long-term viability · R17: Active community support |

Paper 2 evaluated stacks using MCDM and 8 LLMs; **React+Node.js+SQLite** scored highest (4.66/5.0). The current implementation is a single-file PWA — an intentional simplification that satisfies the same requirements while eliminating deployment complexity for the prototype phase.
