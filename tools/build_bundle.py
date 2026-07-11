"""build_bundle.py -- assemble a self-contained *static* share bundle.

Given one or more subjects, this copies the pieces a recipient needs to run the
lessons on their own machine with no Claude session: the server, the viewer, and
the lesson files -- but NOT your per-user state (progress.json / reviews.json).
The bundle runs in static mode, where free-text questions self-check against the
built-in reference answer and there is no live teacher (assess diagnostics are
hidden automatically). Recipients need only Python 3 and a browser with internet
(for the CDN-hosted Markdown / LaTeX / graph renderers).

By default the launchers run the server with --ephemeral: progress is never
written to disk, so the bundle can live in a *shared* folder without one
student's position leaking to the next (F5 resets, which is fine for short
lessons). Pass --keep-progress to build a bundle that saves progress per subject.

Usage:
  python tools/build_bundle.py <subject> [<subject> ...] [-o OUTDIR] [--zip] [--keep-progress]

  -o/--out         where to write the bundle (default: dist/<subject>-static/)
  --zip            also produce <bundle>.zip next to it
  --keep-progress  persist progress.json (default is ephemeral / no persistence)

The lessons are validated as they're copied; a lesson with schema ERRORS aborts
the build, and a quiz-free block missing its `reference` is warned about (static
users rely on it to self-check).
"""
import argparse
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from validate_lesson import validate_file  # noqa: E402  (sibling module)

def readme(ephemeral):
    """Run instructions for the bundle; the progress note depends on the mode."""
    flags = "--static" + (" --ephemeral" if ephemeral else "")
    progress_note = (
        "  * Progress is NOT saved: this bundle is meant for a shared folder, so\n"
        "    each session starts fresh and no one sees anyone else's position\n"
        "    (refreshing the page resets to the start -- fine for short lessons).\n"
        if ephemeral else
        "  * Your progress is saved locally (a progress.json appears per subject) so\n"
        "    you can close the tab and resume later.\n"
    )
    return f"""\
This is a Kalilmod lesson bundle (static mode -- no Claude session needed).

To run it:
  1. Install Python 3 (nothing else -- the server uses only the standard library).
  2. In a terminal in THIS folder, run:
         python serve.py {flags}
     (or double-click run-static.bat on Windows / run-static.sh on macOS/Linux)
  3. Your browser opens at the lesson picker. Click a lesson to begin.
     Flags: --port 8001 if 8000 is busy, --no-browser to not auto-open.

Notes:
  * A browser with internet is required -- the viewer loads its Markdown, LaTeX
    and graph renderers from public CDNs (plus any videos/links a lesson uses).
  * Free-text questions are self-checked: you write an answer, then reveal a
    reference answer to compare. There is no live grading or feedback in static
    mode, and the pre-lesson "about you" diagnostic questions are hidden.
{progress_note}"""


def copy_subject(subject, bundle):
    """Copy one subject's lesson files (only) into the bundle. Returns the list
    of copied lesson paths. Exits on a missing/empty subject."""
    src = os.path.join(ROOT, "subjects", subject)
    if not os.path.isdir(src):
        sys.exit(f"ERROR: no such subject: subjects/{subject}")
    lessons = sorted(f for f in os.listdir(src)
                     if f.startswith("lesson-") and f.endswith(".json"))
    if not lessons:
        sys.exit(f"ERROR: subjects/{subject} has no lesson-*.json files")
    dst = os.path.join(bundle, "subjects", subject)
    os.makedirs(dst, exist_ok=True)
    copied = []
    for l in lessons:  # deliberately skip progress.json / reviews.json (per-user state)
        shutil.copy2(os.path.join(src, l), os.path.join(dst, l))
        copied.append(os.path.join(dst, l))
    return copied


def zip_dir(folder):
    """Zip a folder into <folder>.zip (paths relative to the folder's parent)."""
    zip_path = folder.rstrip("/\\") + ".zip"
    base = os.path.dirname(folder)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _dirs, files in os.walk(folder):
            for f in files:
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, base))
    return zip_path


def main():
    ap = argparse.ArgumentParser(description="Build a static Kalilmod share bundle.")
    ap.add_argument("subjects", nargs="+", help="subject folder name(s) under subjects/")
    ap.add_argument("-o", "--out", default=None, help="output folder (default: dist/<subject>-static)")
    ap.add_argument("--zip", action="store_true", help="also produce a .zip")
    ap.add_argument("--keep-progress", action="store_true",
                    help="persist progress.json (default: ephemeral / no persistence)")
    args = ap.parse_args()
    ephemeral = not args.keep_progress

    default_name = (args.subjects[0] if len(args.subjects) == 1 else "kalilmod") + "-static"
    out = args.out or os.path.join(ROOT, "dist", default_name)
    out = os.path.abspath(out)

    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)

    # Core runtime: the server and the viewer.
    shutil.copy2(os.path.join(ROOT, "serve.py"), os.path.join(out, "serve.py"))
    shutil.copytree(os.path.join(ROOT, "gui"), os.path.join(out, "gui"))

    # Lessons, validated as we go.
    copied, errors, warns = [], 0, 0
    for s in args.subjects:
        copied += copy_subject(s, out)
    for p in copied:
        rel = os.path.relpath(p, out)
        e, w = validate_file(p)
        for x in e:
            print(f"  ERROR {rel}: {x}")
        for x in w:
            print(f"  warn  {rel}: {x}")
        errors += len(e)
        warns += len(w)
    if errors:
        shutil.rmtree(out)
        sys.exit(f"\nAborted: {errors} lesson error(s). Fix them, then rebuild.")

    # Run instructions + convenience launchers.
    serve_flags = "--static" + (" --ephemeral" if ephemeral else "")
    with open(os.path.join(out, "README.txt"), "w", encoding="utf-8") as f:
        f.write(readme(ephemeral))
    with open(os.path.join(out, "run-static.bat"), "w", encoding="utf-8", newline="\r\n") as f:
        f.write(f"@echo off\r\npython serve.py {serve_flags}\r\npause\r\n")
    sh = os.path.join(out, "run-static.sh")
    with open(sh, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"#!/bin/sh\npython3 serve.py {serve_flags}\n")
    try:
        os.chmod(sh, 0o755)
    except OSError:
        pass

    print(f"\nBundle ready: {out}")
    print(f"  subjects: {', '.join(args.subjects)}  ({len(copied)} lesson file(s), {warns} warning(s))")
    print(f"  progress: {'ephemeral (not saved -- shared-folder safe)' if ephemeral else 'persisted per subject'}")
    if args.zip:
        print(f"  zipped:   {zip_dir(out)}")
    print(f"  run with: python serve.py {serve_flags}   (from inside the bundle)")


if __name__ == "__main__":
    main()
