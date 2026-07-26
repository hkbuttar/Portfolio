#!/usr/bin/env python3
"""
Scaffold a new project or coursework entry.

Usage:
    python3 scripts/new_entry.py project my-new-project
    python3 scripts/new_entry.py coursework my-new-course

Creates data/<kind>/NN-<slug>.yaml pre-filled with the required fields (as
placeholders) and the next available numeric prefix, so you don't have to
remember the schema or figure out ordering by hand. Fill in the placeholders,
then run `python3 build.py` (or `make build`).
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

TEMPLATE = """\
slug: {slug}
tag: PROJECT NN
title: TODO Title
org: Independent Project
dates: 2026
team: Solo
short: |-
  TODO one-sentence description shown on the {kind} index card.
stack:
- Python
overview: |-
  TODO a fuller paragraph of context for the detail page.
approach:
- TODO first thing you did.
- TODO second thing you did.
links:
- label: GitHub repository
  href: '#'
"""


def next_prefix(directory: Path) -> str:
    existing = sorted(directory.glob("[0-9][0-9]-*.yaml"))
    if not existing:
        return "01"
    last = int(existing[-1].name.split("-", 1)[0])
    return f"{last + 1:02d}"


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("project", "coursework"):
        print(__doc__)
        sys.exit(1)

    kind_singular, slug = sys.argv[1], sys.argv[2]
    kind_dir = "projects" if kind_singular == "project" else "coursework"

    if not SLUG_RE.match(slug):
        print(f"error: '{slug}' must be lowercase kebab-case (e.g. my-new-project)")
        sys.exit(1)

    directory = ROOT / "data" / kind_dir
    directory.mkdir(parents=True, exist_ok=True)

    if any(f.stem.endswith(slug) for f in directory.glob("*.yaml")):
        print(f"error: a {kind_singular} with slug '{slug}' already exists")
        sys.exit(1)

    prefix = next_prefix(directory)
    out_path = directory / f"{prefix}-{slug}.yaml"
    out_path.write_text(TEMPLATE.format(slug=slug, kind=kind_dir))

    print(f"Created {out_path.relative_to(ROOT)}")
    print("Fill in the TODOs, then run: python3 build.py")


if __name__ == "__main__":
    main()
