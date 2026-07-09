"""validate_lesson.py -- deterministically check a Kalilmod lesson file.

Standard-library only. This is the *classical* validation step for authored
lessons: it parses the JSON with a real parser (not an LLM eyeballing it) and
then checks the block schema, so a structurally-broken lesson is caught before
the GUI ever tries to render it. An LLM can easily emit JSON that parses but is
wrong -- a quiz-choice whose `answer` index is out of range, a missing
`options`, an unknown block `type` -- and those are exactly the mistakes this
script flags.

Usage:
  python tools/validate_lesson.py subjects/<topic>/lesson-NN.json [more.json ...]

Exit code 0 only if every file is valid (warnings allowed). Non-zero if any
file fails to parse or violates the schema. Errors and warnings are printed
with the offending block index so they're easy to fix.
"""
import json
import sys

CONTENT = {"explanation", "link", "video", "graph"}
KNOWN = CONTENT | {"quiz-choice", "quiz-free", "assess"}


def _is_str(v):
    return isinstance(v, str)


def _is_nonempty_str(v):
    return isinstance(v, str) and v.strip() != ""


def check_block(b, i, errors, warns):
    """Append schema problems for one block to errors/warns."""
    where = f"block {i}"
    if not isinstance(b, dict):
        errors.append(f"{where}: not an object")
        return
    t = b.get("type")
    if not _is_str(t):
        errors.append(f"{where}: missing/invalid 'type'")
        return
    where = f"block {i} ({t})"
    if t == "manim":
        errors.append(f"{where}: 'manim' is reserved/not implemented -- the viewer can't render it")
        return
    if t not in KNOWN:
        errors.append(f"{where}: unknown type '{t}' (the viewer shows it as unsupported)")
        return

    if t == "explanation":
        if not _is_nonempty_str(b.get("markdown")):
            errors.append(f"{where}: needs a non-empty 'markdown' string")
        if "lead" in b and not _is_str(b["lead"]):
            errors.append(f"{where}: 'lead' must be a string")

    elif t == "link":
        for f in ("url", "title"):
            if not _is_nonempty_str(b.get(f)):
                errors.append(f"{where}: needs a non-empty '{f}'")

    elif t == "video":
        for f in ("url", "title"):
            if not _is_nonempty_str(b.get(f)):
                errors.append(f"{where}: needs a non-empty '{f}'")

    elif t == "graph":
        if not isinstance(b.get("data"), list):
            errors.append(f"{where}: 'data' must be a list (a Plotly data array)")
        if not isinstance(b.get("layout"), dict):
            errors.append(f"{where}: 'layout' must be an object (a Plotly layout)")

    elif t == "quiz-choice":
        if not _is_nonempty_str(b.get("question")):
            errors.append(f"{where}: needs a non-empty 'question'")
        opts = b.get("options")
        if not isinstance(opts, list) or not (2 <= len(opts) <= 5):
            errors.append(f"{where}: 'options' must be a list of 2-5 items")
            opts = []
        elif not all(_is_nonempty_str(o) for o in opts):
            errors.append(f"{where}: every entry in 'options' must be a non-empty string")
        ans = b.get("answer")
        if isinstance(ans, bool) or not isinstance(ans, int):
            errors.append(f"{where}: 'answer' must be an integer index")
        elif opts and not (0 <= ans < len(opts)):
            errors.append(f"{where}: 'answer' index {ans} is out of range for {len(opts)} options")
        if "hints" in b:
            h = b["hints"]
            if not isinstance(h, list) or not all(_is_str(x) for x in h):
                errors.append(f"{where}: 'hints' must be a list of strings")

    elif t == "quiz-free":
        if not _is_nonempty_str(b.get("question")):
            errors.append(f"{where}: needs a non-empty 'question'")
        if not _is_nonempty_str(b.get("reference")):
            warns.append(f"{where}: no 'reference' -- static-mode users can't self-check this")

    elif t == "assess":
        if not _is_nonempty_str(b.get("question")):
            errors.append(f"{where}: needs a non-empty 'question'")
        if "options" in b:
            o = b["options"]
            if not isinstance(o, list) or not all(_is_nonempty_str(x) for x in o):
                errors.append(f"{where}: 'options' must be a list of non-empty strings")


def validate_file(path):
    """Return (errors, warns) for one lesson file. A parse failure is a single
    fatal error and short-circuits the schema checks."""
    errors, warns = [], []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return [f"file not found: {path}"], []
    except json.JSONDecodeError as e:
        return [f"not valid JSON: line {e.lineno}, column {e.colno}: {e.msg}"], []

    if not isinstance(data, dict):
        return ["top level must be a JSON object"], []
    if not _is_nonempty_str(data.get("title")):
        warns.append("no 'title' -- the page title falls back to 'Kalilmod'")
    blocks = data.get("blocks")
    if not isinstance(blocks, list) or len(blocks) == 0:
        errors.append("'blocks' must be a non-empty list")
        return errors, warns
    for i, b in enumerate(blocks):
        check_block(b, i, errors, warns)

    # a lesson of only real content with no quiz is against the whole point;
    # (assess-only files are legitimate -- an evaluation round awaiting authoring)
    types = [b.get("type") for b in blocks if isinstance(b, dict)]
    has_quiz = any(t in ("quiz-choice", "quiz-free") for t in types)
    only_assess = types and all(t == "assess" for t in types)
    if not has_quiz and not only_assess:
        warns.append("no quiz-choice/quiz-free block -- the lesson has nothing for the student to answer")
    return errors, warns


def main():
    paths = sys.argv[1:]
    if not paths:
        sys.stderr.write("usage: python tools/validate_lesson.py <lesson.json> [...]\n")
        sys.exit(2)
    any_error = False
    for path in paths:
        errors, warns = validate_file(path)
        if errors:
            any_error = True
            print(f"INVALID  {path}")
            for e in errors:
                print(f"  ERROR: {e}")
            for w in warns:
                print(f"  warn:  {w}")
        else:
            print(f"VALID    {path}" + (f"  ({len(warns)} warning(s))" if warns else ""))
            for w in warns:
                print(f"  warn:  {w}")
    sys.exit(1 if any_error else 0)


if __name__ == "__main__":
    main()
