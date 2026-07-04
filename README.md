# Kalilmod

An interactive learning tool: Claude Code acts as your teacher, writing lessons that alternate short explanations with frequent quizzes, so you actually engage with the material instead of passively reading. See `CLAUDE.md` for the full design.

## Prerequisites

- Python 3 (no packages needed — the server is standard library only)
- Claude Code (for a **dynamic** session; a static session can use any LLM — see below)
- Internet in the browser (the viewer loads Markdown/LaTeX/graph renderers from a CDN, plus any linked videos)

## Dynamic vs. static sessions

- **Dynamic** (Claude Code): the live session can review your free-text answers and adjust lessons on the fly. This is the full experience. Started by the `/teach-me` command below, which launches the server for you.
- **Static** (any other LLM, or just replaying lessons): you run the server yourself with `python serve.py --static`. Multiple-choice and graphs work fully; free-text questions are self-checked against a reference answer instead of being reviewed live.

## How to learn a subject (dynamic)

**Start with Claude Code, not with `serve.py`** — the teacher evaluates you, writes the lesson, and launches the server itself. In a terminal in this repo, run `claude`, then use the one command:

- **`/teach-me <topic>`** — start a new subject. Example: `/teach-me the Krebs cycle`. The teacher opens your browser, asks a few quick **evaluation questions** right there to gauge your level, builds your lesson from your answers, and then **goes hands-free**.
- **`/teach-me`** (no topic) — lists the subjects you already have to **resume** one, or lets you name a new topic.

That's the whole command surface. After it opens the browser, the teacher **stays live automatically** — reading your evaluation answers (and maybe asking a finer round), reviewing each free-text answer, applying feedback, and writing the next lesson when you finish, all with **no further terminal actions**. A background listener your browser wakes on each action does this; it stays on your Claude subscription (no API key) and costs ~nothing while you read. Stop it any time by saying so, or by closing the server.

Working through a subject: it opens with a short **evaluation** — a few questions (multiple-choice or free-text, no right/wrong) so the teacher can pitch the lesson at your level; answer them and the lesson appears. Then blocks reveal one at a time. Wrong multiple-choice answers reveal hints, then a "Show answer"; any question you miss is re-quizzed in a review round at the end. For a free-text question, type your answer and submit — the teacher's review appears in the page on its own, no refresh. You can also message the teacher any time via the feedback box. A small corner badge shows whether a teacher session is connected, so you never wait on a review no one is there to write. Progress is saved automatically; pressing **F5 keeps you on the same lesson**. If a session is ever lost, just re-run `/teach-me` — your progress and reviews live in files, so nothing is lost but the chat.

## Static session (another LLM, or just replaying lessons)

If you don't have Claude Code, another LLM can still generate lesson files (it reads `docs/teacher-guide.md` and writes `subjects/<topic>/lesson-NN.json`). To study them:

```
python serve.py --static
```

The browser opens at the lesson picker; free-text questions let you write an answer and then reveal a reference answer to self-check. `--port N` and `--no-browser` flags are also available. (Running `python serve.py` with no flag is dynamic mode, which assumes a live Claude session for reviews.)

## Trying the mechanisms

The `_demo` subject is a self-guided test of the tool itself (hints, "Show answer", video embeds, graphs, free-response). Run `python serve.py` and pick `_demo`.

## Developing the tool

Open `claude` in this repo and describe the change — `CLAUDE.md` puts a session asked about development into the Builder role. Current status and roadmap are at the bottom of `CLAUDE.md`.
