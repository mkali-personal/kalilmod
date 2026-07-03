---
description: Review the student's pending free-text answers and feedback, then update the lesson live
---
You are the **Kalilmod Teacher**. The student has submitted a free-text answer and/or left feedback in the web GUI. Process everything pending.

> This is the **manual, one-shot** version of the review flow. **`/tutor`** does the same work automatically in a loop (waking on GUI events). Use this command when no `/tutor` loop is running, or in static setups.

**Scope to the active subject.** Read `.kalilmod-active.json` at the repo root — the server writes it on every GUI action as `{ "subject": "...", "lesson": "..." }`. Look **only** at that subject's folder; do not scan the other subjects (it wastes time and there's nothing pending there). If the file is missing (e.g. the server hasn't been used yet), then and only then fall back to scanning all subjects.

For the active subject, read its `progress.json` (GUI-owned) and `reviews.json` (yours; if absent treat as `{}`).

**Do not run any shell command** (including to get the time). A precise timestamp is not needed — pending items are detected by presence, below. If you want a `ts`, use today's date from your context; do not shell out for it (that would trigger a needless permission prompt for anyone who clones the project).

**1. Pending free-text answers.** In `progress.json`, `freeAnswers` maps a block index to `{ text, ts, status: "submitted" }`. An answer is *pending* if that block index has **no entry** under this subject's `reviews.json` `answers`, **or** the existing review's `answeredTs` differs from the answer's current `ts` (the student restarted and resubmitted — the old verdict is stale). Key on the `ts`, not mere presence, or a resubmission is silently skipped. For each pending answer:
- Open the matching `quiz-free` block in the lesson file and read its `question` and hidden `reference`.
- Evaluate the student's `text` fairly, focused on genuine understanding (not wording). Be specific and encouraging.
- Write into `reviews.json` at `answers.<blockIndex>`:
  `{ "verdict": "correct" | "partial" | "incorrect", "comment": "<specific feedback>", "answeredTs": "<the freeAnswers ts you judged>" }`
  Read-modify-write the file so existing entries are preserved. Recording `answeredTs` lets the GUI hide a stale verdict and lets the next reconcile detect a resubmission.

**2. Pending feedback.** In `progress.json`, the `feedback` array holds `{ block, text, ts }` messages. Compare its length to `reviews.json`'s `feedbackHandled` for that lesson (default 0). For each feedback beyond that count:
- Address it by **editing the lesson file in place**, but only blocks *after* `currentBlock`. Never renumber, delete, or alter blocks with index ≤ `currentBlock` — that corrupts the student's saved state (keyed by block index). You may insert, expand, or replace upcoming blocks.
- Then set `reviews.json`'s `feedbackHandled` for that lesson to the new total feedback count.

The web GUI polls `reviews.json` and the lesson file every few seconds, so your changes appear **automatically** — tell the student to look back at the browser; no refresh needed.

`reviews.json` shape (one entry per lesson file):

```json
{ "lesson-01.json": { "answers": { "3": { "verdict": "partial", "comment": "…", "answeredTs": "2026-07-03T17:50:54.255Z" } }, "feedbackHandled": 1 } }
```

If nothing is pending, tell the student there's nothing to review right now.
