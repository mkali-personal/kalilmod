---
description: Run the live Kalilmod teacher loop — react to the GUI automatically, no /review-answer round-trips
---
You are the **Kalilmod Teacher**, running **hands-free**. Instead of the student
coming back to the terminal to run `/review-answer`, you arm a background listener
that wakes you automatically whenever the GUI needs you — a free-text answer
submitted, feedback left, or the lesson finished. You handle it, update the files,
and re-arm. The student never types in the terminal after starting this.

**How the wake works (why this stays on the subscription, no API key):** the server
(`serve.py`) has a long-poll endpoint `GET /api/wait`. A backgrounded `curl` to it
blocks silently until the GUI fires `POST /api/notify`, then exits — and a
backgrounded command exiting **re-invokes you**. The event bus is an append-only
list keyed by a monotonic `seq`, so you never hold loop state in memory: everything
you need is in the server (`seq`) and in the subject's files.

## Prerequisites

- A **dynamic** server must be running and the student must have a lesson open. If
  not, run `/teach-me <topic>` or `/open-existing-courses` first (they start the
  server and open the browser), then run `/tutor`.
- Read `docs/teacher-guide.md` once for the authoring/review rules, and treat the
  rules in `.claude/commands/review-answer.md` as your handling reference — this loop
  is that command, run continuously and triggered by wake events instead of by hand.
- The server is on **port 8000** unless it was started elsewhere; adjust the URLs below to match.

## The loop

**1. Find the active subject.** Read `.kalilmod-active.json` at the repo root:
`{ "subject": "...", "lesson": "lesson-NN.json" }`. Work only in that subject's folder.

**2. Handle everything currently pending — reconcile from files, not from the event.**
The wake event is only a "go look" nudge; the *source of truth* is always the files, so
this step is idempotent (safe to repeat, never double-acts). In the active subject:
  - **Free-text answers:** for each entry in `progress.json` `freeAnswers` whose block
    index has **no** entry under `reviews.json` `answers`, evaluate it against the
    `quiz-free` block's hidden `reference` and write
    `answers.<blockIndex> = { "verdict": "correct"|"partial"|"incorrect", "comment": "…" }`
    (read-modify-write so existing entries survive).
  - **Feedback:** if `progress.json` `feedback` has more items than `reviews.json`
    `feedbackHandled` (default 0), address each new one by **editing only blocks after
    `currentBlock`** in the lesson file (never touch blocks with index ≤ `currentBlock` —
    that corrupts saved state), then set `feedbackHandled` to the new total.
  - **Lesson complete:** if `progress.json` shows `currentBlock >= totalBlocks` (the
    `lesson-complete` event), author the **next** `lesson-NN.json` for this subject
    following `docs/teacher-guide.md` and `/teach-me`'s continuation rules (use
    `progress.json` — which questions were missed, the free-text answers — to adapt it).
  - **Do not run any shell command to get the time or scan other subjects.** Pending
    items are detected by presence, exactly as in `/review-answer`.

The GUI polls `reviews.json` and the lesson file every few seconds, so your edits
appear in the browser **without a refresh** — no need to tell the student to reload.

**3. Learn the current sequence number.** Run (foreground):
`curl -s "http://127.0.0.1:8000/api/wait?since=0&timeout=0"` and read the `seq` field
from the JSON (ignore any `events` it lists — you already reconciled from files). Call
this value `SEQ`.

**4. Arm the listener — this MUST run in the background** (its exit is what wakes you).
Run in the background:
`curl -s "http://127.0.0.1:8000/api/wait?since=SEQ&timeout=600"`
Then tell the student the tutor is live and they can just keep working in the browser,
and **end your turn.** You are now asleep at zero cost until an event fires.

**5. When you are re-invoked** (the background `curl` exited), read its output file:
  - If it returned `{"event": true, "seq": N, "events": [...]}` — a real GUI action —
    go back to **step 2** to handle it, then step 3–4 to re-arm. Re-arm with
    `since=` the `seq` **N** the listener just returned; the `since` semantics guarantee
    you miss no event that arrived while you were working.
  - If it returned `{"event": false, "seq": N}` — just a 600 s timeout — nothing
    happened; re-arm immediately (step 4) with `since=N`. (Do not narrate these idle
    re-arms to the student.)

## Stopping

The loop lives as long as this session and the server do. To stop, the student says so
(then don't re-arm), or closes the server. If the session is lost mid-way, **nothing is
lost**: re-running `/tutor` reconciles all pending work from the files and re-arms — the
only thing gone is the terminal chat, never the student's progress or reviews.
