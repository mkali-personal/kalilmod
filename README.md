# Kalilmod

An interactive learning tool: Claude Code acts as your teacher, alternating short explanations with frequent quizzes so you actually engage with the material instead of passively reading. It works two ways:

- **`/teach-me <topic>`** — Claude evaluates you and *writes* a lesson on the topic.
- **`/read-with-me <source>`** — you supply a text you already have (a paper, a chapter, a web page); Claude *doesn't* re-teach it — it reads the actual source and guides your attention through it with comprehension quizzes. Best for advanced material, where an LLM re-explaining risks flattening or mis-stating the content.

See `CLAUDE.md` for the full design.

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

**Question types.** The very first time the browser opens it asks whether to include **free-text (written) questions** or keep everything **multiple-choice only** — your choice is remembered and can be flipped from the lesson toolbar at any time. Choosing multiple-choice-only hides written questions, even in lessons that were authored with them.

Working through a subject: it opens with a short **evaluation** — a few questions (multiple-choice or free-text, no right/wrong) so the teacher can pitch the lesson at your level; answer them and the lesson appears. Then blocks reveal one at a time. Wrong multiple-choice answers reveal hints, then a "Show answer"; any question you miss is re-quizzed in a review round at the end. For a free-text question, type your answer and submit — the teacher's review appears in the page on its own, no refresh. You can also message the teacher any time via the feedback box. A small corner badge shows whether a teacher session is connected, so you never wait on a review no one is there to write. Progress is saved automatically; pressing **F5 keeps you on the same lesson**. If a session is ever lost, just re-run `/teach-me` — your progress and reviews live in files, so nothing is lost but the chat.

## Actively read a text you already have (dynamic)

When the material already exists — a paper, a textbook section, a web article — and you don't want it re-explained (just read *actively*), use:

- **`/read-with-me <source>`** — where `<source>` is a local file path or a URL, optionally with a page/section range. Examples: `/read-with-me ./papers/aspect1982.pdf pp. 91-94`, or `/read-with-me https://en.wikipedia.org/wiki/Bell%27s_theorem`.

Claude reads the *actual* source (for a PDF, only the pages you name — it doesn't ingest the whole book) and cross-checks related references, then builds a lesson that **points you at each passage, tells you what to watch for, and quizzes your understanding** — without rewriting or summarizing the source itself. There's no evaluation step (you already chose what to read). Everything else is the same as `/teach-me`: sequential reveal, quiz gating, the review round, the feedback box (ask it to explain a passage and it will), the live teacher badge, and F5-safe progress. Long sources are covered a segment at a time; finish one and the next is authored automatically.

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
