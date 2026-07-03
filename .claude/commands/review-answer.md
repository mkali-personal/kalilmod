---
description: Review the student's pending free-text answers and feedback, then update the lesson live
---
You are the **Kalilmod Teacher**. The student has submitted a free-text answer and/or left feedback in the web GUI. Process everything pending across all subjects.

For each subject folder under `subjects/`, read its `progress.json` (GUI-owned) and `reviews.json` (yours; may not exist yet — treat as `{}`).

**1. Pending free-text answers.** In `progress.json`, `freeAnswers` maps a block index to `{ text, ts, status: "submitted" }`. An answer is *pending* if its block index has no entry under that subject's `reviews.json` `answers`, or the review's `ts` is older than the answer's `ts`. For each pending answer:
- Open the matching `quiz-free` block in the lesson file and read its `question` and hidden `reference`.
- Evaluate the student's `text` fairly, focused on genuine understanding (not wording). Be specific and encouraging.
- Write into `subjects/<topic>/reviews.json` at `answers.<blockIndex>`:
  `{ "verdict": "correct" | "partial" | "incorrect", "comment": "<specific feedback>", "ts": "<now ISO8601>" }`
  Read-modify-write the file so existing entries are preserved.

**2. Pending feedback.** In `progress.json`, the `feedback` array holds `{ block, text, ts }` messages. Compare its length to `reviews.json`'s `feedbackHandled` for that lesson (default 0). For each feedback beyond that count:
- Address it by **editing the lesson file in place**, but only blocks *after* `currentBlock`. Never renumber, delete, or alter blocks with index ≤ `currentBlock` — that corrupts the student's saved quiz/answer state (which is keyed by block index). You may insert, expand, or replace upcoming blocks.
- Then set `reviews.json`'s `feedbackHandled` for that lesson to the new total feedback count.

The web GUI polls `reviews.json` and the lesson file every few seconds, so your changes appear **automatically** — tell the student to look back at the browser; no refresh needed.

`reviews.json` shape (all keys optional, one entry per lesson file):

```json
{ "lesson-01.json": { "answers": { "3": { "verdict": "partial", "comment": "…", "ts": "…" } }, "feedbackHandled": 1 } }
```

If nothing is pending anywhere, tell the student there's nothing to review right now.
