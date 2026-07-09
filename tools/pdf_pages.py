"""pdf_pages.py -- read a PDF surgically, one page range at a time.

Standard-library only. It shells out to the poppler utilities
(pdftotext / pdftoppm / pdfinfo) so a reading session can pull *just* the
focus pages of a document instead of ingesting the whole book. This is the
PDF path for the /read-with-me skill (docs/reading-guide.md).

Poppler is an external dependency (there is no stdlib way to read or render a
PDF). If it is missing, every command fails loudly with install instructions
rather than silently doing the wrong thing.

Usage:
  python tools/pdf_pages.py info  FILE
      Page count and metadata (via pdfinfo). Use it to sanity-check a range
      and to spot the offset between printed page numbers and PDF page index.

  python tools/pdf_pages.py text  FILE -f FIRST [-l LAST] [--layout]
      Print the text of PDF pages FIRST..LAST to stdout (only those pages).
      -l defaults to -f (a single page). -f is required on purpose: it stops
      an accidental whole-book dump. --layout keeps the physical column layout.

  python tools/pdf_pages.py image FILE -p PAGE [-r DPI] [-o OUT.png]
      Render one PDF page to a PNG and print its path, so you can Read the
      image. Use this for figures or equation-heavy pages, where extracted
      text gets mangled. DPI defaults to 150.

Note on page numbers: FIRST/LAST/PAGE are *PDF page indices* (1 = the first
page of the file). A book's printed "page 604" is often a different index
because of front matter -- run `info` and peek at one page to find the offset.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

REQUIRED = {
    "text": "pdftotext",
    "image": "pdftoppm",
    "info": "pdfinfo",
}


def die_missing(tool):
    """Print a clear, actionable message and exit when poppler isn't found."""
    msg = f"""\
ERROR: '{tool}' was not found on your PATH.

pdf_pages.py reads PDFs with the poppler utilities (pdftotext, pdftoppm,
pdfinfo). They are not installed (or not on PATH). Install poppler, then retry:

  Windows : scoop install poppler   -OR-   choco install poppler
            (the pdftotext/pdftoppm bundled with MiKTeX or TeX Live also work)
  macOS   : brew install poppler
  Linux   : sudo apt install poppler-utils     (Debian/Ubuntu)
            sudo dnf install poppler-utils      (Fedora/RHEL)

No poppler available? Two dependency-free alternatives:
  - point /read-with-me at a web URL instead (WebFetch needs no poppler), or
  - export the document to plain text / HTML and read that file instead.
"""
    sys.stderr.write(msg)
    sys.exit(3)


def require(tool):
    if shutil.which(tool) is None:
        die_missing(tool)


def check_file(path):
    if not os.path.isfile(path):
        sys.stderr.write(f"ERROR: file not found: {path}\n")
        sys.exit(2)


def run(cmd):
    """Run a poppler command, surfacing its stderr on failure."""
    try:
        return subprocess.run(cmd, capture_output=True)
    except OSError as e:
        sys.stderr.write(f"ERROR: could not run {cmd[0]}: {e}\n")
        sys.exit(3)


def cmd_info(args):
    require("pdfinfo")
    check_file(args.file)
    res = run(["pdfinfo", args.file])
    if res.returncode != 0:
        sys.stderr.write(res.stderr.decode("utf-8", "replace"))
        sys.exit(res.returncode)
    sys.stdout.write(res.stdout.decode("utf-8", "replace"))


def cmd_text(args):
    require("pdftotext")
    check_file(args.file)
    last = args.last if args.last is not None else args.first
    if last < args.first:
        sys.stderr.write("ERROR: -l (last page) is before -f (first page).\n")
        sys.exit(2)
    cmd = ["pdftotext", "-f", str(args.first), "-l", str(last)]
    if args.layout:
        cmd.append("-layout")
    cmd += [args.file, "-"]  # "-" => write extracted text to stdout
    res = run(cmd)
    if res.returncode != 0:
        sys.stderr.write(res.stderr.decode("utf-8", "replace"))
        sys.exit(res.returncode)
    sys.stdout.buffer.write(res.stdout)


def cmd_image(args):
    require("pdftoppm")
    check_file(args.file)
    if args.out:
        out = args.out
        if out.lower().endswith(".png"):
            out = out[:-4]  # pdftoppm -singlefile appends .png itself
    else:
        stem = os.path.splitext(os.path.basename(args.file))[0]
        out = os.path.join(tempfile.gettempdir(), f"{stem}-p{args.page}")
    cmd = ["pdftoppm", "-png", "-singlefile",
           "-f", str(args.page), "-l", str(args.page),
           "-r", str(args.dpi), args.file, out]
    res = run(cmd)
    if res.returncode != 0:
        sys.stderr.write(res.stderr.decode("utf-8", "replace"))
        sys.exit(res.returncode)
    png = out + ".png"
    if not os.path.isfile(png):
        sys.stderr.write("ERROR: pdftoppm reported success but produced no PNG "
                         f"(is page {args.page} within the document?).\n")
        sys.exit(3)
    print(os.path.abspath(png))  # the path to Read


def main():
    p = argparse.ArgumentParser(
        description="Read a PDF one page range at a time (needs poppler).")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("info", help="page count + metadata")
    pi.add_argument("file")
    pi.set_defaults(func=cmd_info)

    pt = sub.add_parser("text", help="extract text of a page range to stdout")
    pt.add_argument("file")
    pt.add_argument("-f", "--first", type=int, required=True,
                    help="first PDF page (1-based); required to avoid whole-file dumps")
    pt.add_argument("-l", "--last", type=int, default=None,
                    help="last PDF page (defaults to --first)")
    pt.add_argument("--layout", action="store_true",
                    help="preserve physical layout (helps tables/columns)")
    pt.set_defaults(func=cmd_text)

    pm = sub.add_parser("image", help="render one page to PNG (for figures/equations)")
    pm.add_argument("file")
    pm.add_argument("-p", "--page", type=int, required=True, help="PDF page (1-based)")
    pm.add_argument("-r", "--dpi", type=int, default=150, help="resolution (default 150)")
    pm.add_argument("-o", "--out", default=None, help="output PNG path (default: temp dir)")
    pm.set_defaults(func=cmd_image)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
