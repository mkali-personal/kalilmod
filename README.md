# Kalilmod — קל ללמוד

An interactive learning tool: Claude Code acts as your teacher, writing lessons that alternate short explanations with frequent quizzes, so you actually engage with the material instead of passively reading. See `CLAUDE.md` for the full design.

## Prerequisites

- Python 3 (no packages needed — the server is standard library only)
- Claude Code
- Internet in the browser (the viewer loads Markdown/LaTeX renderers from a CDN, plus any linked videos)

## How to learn a subject

**Start with Claude Code, not with `serve.py`.** The teacher session interviews you first, writes the lesson, and then launches the server itself.

1. Open a terminal in this repository and run `claude`.
2. Prompt it with something like:

   > I want to learn **[your topic]**. Act as the Kalilmod Teacher: read `docs/teacher-guide.md` and follow it.

   or, for a subject you started before:

   > I want to continue learning **[topic]**. Act as the Kalilmod Teacher: read `docs/teacher-guide.md` and follow it.

   (Mentioning the guide explicitly is a safety net — `CLAUDE.md` is loaded automatically and already points a "teach me" request to the guide, but being explicit costs nothing.)

3. Answer the interview questions in the terminal so the teacher can gauge your level.
4. The teacher writes the lesson and starts the server; your browser opens at the lesson picker. Pick your lesson and work through it — wrong answers reveal hints, and your progress is saved automatically.
5. When you finish (or want more), **return to the terminal** and tell the teacher. It reads your quiz results and writes the next lesson, adapted to what you struggled with.

## Just re-reading existing lessons

If you only want to reopen lessons that already exist (no new content needed), skip Claude entirely:

```
python serve.py
```

The browser opens at the lesson picker; your progress is where you left it. `--port N` and `--no-browser` flags are available.

## Trying the mechanisms

The `_demo` subject is a self-guided test of the tool itself (hints, "Show answer", video embeds). Run `python serve.py` and pick `_demo`.

## Developing the tool

Open `claude` in this repo and describe the change — `CLAUDE.md` puts a session asked about development into the Builder role. Current status and roadmap are at the bottom of `CLAUDE.md`.
