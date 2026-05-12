---
description: AI content automation pipeline — job types, output shapes, model used, and the production proxy requirement
alwaysApply: true
---

Uses **Anthropic API** (`claude-sonnet-4-20250514`) to generate content for teacher review.

| Job type | Output |
|----------|--------|
| `summary` | `{ summary, keyPoints[], practiceQ }` |
| `quiz` | `{ questions: [{ question, options[], why }] }` |
| `flashcards` | `{ flashcards: [{ front, back }] }` |
| `translation` | `{ titleAr, descAr, keyTermsAr[] }` (Arabic — supports PR11) |
| `scenario` | `{ scenario, context, learningGoal }` (low-connectivity framing) |

All prompts instruct the model to return only valid JSON.

**The API is called directly from the browser — use a server-side proxy in production to avoid exposing API keys.**
