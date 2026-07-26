#!/usr/bin/env python3
"""
Generates the static multi-page portfolio site.

Architecture
------------
Content lives as data, not code: every project/coursework/experience entry
is a YAML file under data/projects/, data/coursework/, or data/experience/.
This script:

  1. Loads and validates every YAML file against the schema in content/schema.py
     (fails loudly, with a file name and reason, on any malformed entry).
  2. Renders each page through Jinja2 templates (templates/), which share a
     base layout, nav, and footer via template inheritance/includes.
  3. Writes the static HTML output to disk, auto-creates a document folder
     for every entry, removes stale pages for entries that no longer exist,
     and generates a sitemap.xml.

To add a project, course, or work experience entry, add a YAML file to
data/projects/, data/coursework/, or data/experience/ (see scripts/new_entry.py
to scaffold projects/coursework) and rerun this script — no template or HTML
editing required.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, str(Path(__file__).parent))
from content.schema import ContentValidationError, load_entries

ROOT = Path(__file__).parent
DATA = ROOT / "data"
TEMPLATES = ROOT / "templates"
SITE_URL = "https://example.com"  # update once the site has a real domain


def strip_html_entities(text: str) -> str:
    """Produce a plain-text <title> from a display title that may contain
    HTML entities (&ndash;, &amp;, etc.)."""
    for entity, plain in [("&ndash;", "-"), ("&rarr;", ""), ("&mdash;", "-"),
                            ("&amp;", "&"), ("&times;", "x")]:
        text = text.replace(entity, plain)
    return text


def clean_generated_dir(path: Path):
    """Remove all previously generated .html pages in a directory (fresh
    build), leaving any non-generated files untouched."""
    if path.exists():
        for f in path.glob("*.html"):
            f.unlink()
    path.mkdir(parents=True, exist_ok=True)


def sync_document_folders(entries, kind: str):
    """Ensure every current entry has an assets/documents/<kind>/<slug>/
    folder, and remove folders for entries that no longer exist."""
    base = ROOT / "assets" / "documents" / kind
    base.mkdir(parents=True, exist_ok=True)
    current_slugs = {e.slug for e in entries}
    for existing in base.iterdir():
        if existing.is_dir() and existing.name not in current_slugs:
            shutil.rmtree(existing)
    for slug in current_slugs:
        (base / slug).mkdir(exist_ok=True)


def main():
    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=False,  # content already carries intentional HTML/entities
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # --- load + validate content -------------------------------------------------
    try:
        projects = load_entries(DATA / "projects")
        coursework = load_entries(DATA / "coursework")
        experience = load_entries(DATA / "experience")
    except ContentValidationError as e:
        print(f"\n✗ Content validation failed:\n\n{e}\n", file=sys.stderr)
        sys.exit(1)

    # --- render home ---------------------------------------------------------------
    (ROOT / "index.html").write_text(
        env.get_template("home.html").render(page_title="Home", active="home", depth="")
    )

    # --- render index pages ---------------------------------------------------------
    (ROOT / "projects.html").write_text(
        env.get_template("index.html").render(
            page_title="Projects", active="projects", depth="", kind="projects",
            items=projects, heading="Projects",
            intro=("A selection of capstone, independent, and applied coursework projects "
                   "spanning time-series forecasting, recommender systems, and applied NLP. "
                   "Select a project for the full write-up, stack, and linked materials."),
        )
    )
    (ROOT / "coursework.html").write_text(
        env.get_template("index.html").render(
            page_title="Coursework", active="coursework", depth="", kind="coursework",
            items=coursework, heading="Coursework",
            intro=("Core coursework from the M.S. Applied Data Science program at UChicago. "
                   "Select an item for the full write-up and linked repository."),
        )
    )
    (ROOT / "experience.html").write_text(
        env.get_template("index.html").render(
            page_title="Experience", active="experience", depth="", kind="experience",
            items=experience, heading="Experience",
            intro=("Roles spanning data science leadership, applied analytics, and teaching. "
                   "Select a role for the full write-up and highlights."),
        )
    )
    (ROOT / "education.html").write_text(
        env.get_template("education.html").render(page_title="Education", active="education", depth="")
    )

    # --- render detail pages ---------------------------------------------------------
    detail_tpl = env.get_template("detail.html")
    sitemap_urls = ["", "projects.html", "coursework.html", "experience.html", "education.html"]
    active_by_kind = {
        "projects": "project-detail",
        "coursework": "course-detail",
        "experience": "experience-detail",
    }

    for kind, entries in (("projects", projects), ("coursework", coursework), ("experience", experience)):
        out_dir = ROOT / kind
        clean_generated_dir(out_dir)
        active = active_by_kind[kind]
        for item in entries:
            html = detail_tpl.render(
                page_title=strip_html_entities(item.title),
                active=active, depth="../",
                kind=kind, item=item,
            )
            (out_dir / f"{item.slug}.html").write_text(html)
            sitemap_urls.append(f"{kind}/{item.slug}.html")
        sync_document_folders(entries, kind)

    # keep otherwise-empty document folders under version control
    for dirpath in (ROOT / "assets" / "documents").rglob("*"):
        if dirpath.is_dir() and not any(dirpath.iterdir()):
            (dirpath / ".gitkeep").touch()

    # --- sitemap.xml -----------------------------------------------------------------
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path in sitemap_urls:
        sitemap.append(f"  <url><loc>{SITE_URL}/{path}</loc></url>")
    sitemap.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap) + "\n")

    # --- build report ------------------------------------------------------------------
    print("✓ Build complete.")
    print(f"  {len(projects)} project page(s), {len(coursework)} coursework page(s), {len(experience)} experience page(s)")
    print(f"  {len(sitemap_urls)} URL(s) written to sitemap.xml")


if __name__ == "__main__":
    main()