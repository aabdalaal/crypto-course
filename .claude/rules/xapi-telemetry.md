---
description: xAPI/SCORM telemetry implementation and the PR13 constraint limiting sync payload to exactly 6 fields
alwaysApply: true
---

Events via `emitXAPI(verb, objectName, extensions)`. Stored locally (last 200 events). Exportable via admin panel.

Sync payload is hardcoded to exactly 6 fields (PR13 compliance):
- `xpDelta`
- `streak`
- `badgeTimestamps`
- `quizOutcomes`
- `labCompletions`
- `sessionDuration`

**No free-text, device ID, or geolocation permitted in sync payload** — hard PR13 constraint.
