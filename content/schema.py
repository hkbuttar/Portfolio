"""
Content schema and validation.

Every project/coursework entry is a YAML file under data/projects/ or
data/coursework/. This module defines what a valid entry looks like and
turns raw YAML dicts into validated, typed objects — so a malformed entry
fails loudly at build time with a clear message, rather than silently
producing broken or empty HTML.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class ContentValidationError(Exception):
    """Raised when a YAML content file doesn't match the expected schema."""


SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DOC_EXTS = {"pdf": "PDF", "pptx": "PPTX", "ppt": "PPT", "docx": "DOCX"}


@dataclass
class Link:
    label: str
    href: str

    @property
    def doc_ext(self) -> Optional[str]:
        """File extension if this link points at a previewable/badge-able document."""
        name = self.href.rsplit("/", 1)[-1]
        if "." in name:
            ext = name.rsplit(".", 1)[-1].lower()
            if ext in DOC_EXTS:
                return ext
        return None

    @property
    def doc_badge(self) -> Optional[str]:
        ext = self.doc_ext
        return DOC_EXTS[ext] if ext else None


@dataclass
class Entry:
    """A single project or coursework item."""

    slug: str
    tag: str
    title: str
    org: str
    dates: str
    short: str
    stack: list[str]
    overview: str
    approach: list[str]
    links: list[Link]
    team: str = ""
    source_file: str = field(default="", repr=False, compare=False)

    @property
    def doc_links(self) -> list[Link]:
        return [l for l in self.links if l.doc_ext]

    @property
    def other_links(self) -> list[Link]:
        return [l for l in self.links if not l.doc_ext]

    @classmethod
    def from_dict(cls, raw: dict, source_file: str) -> "Entry":
        errors = []

        def require(key, expected_type):
            if key not in raw:
                errors.append(f"missing required field '{key}'")
                return None
            val = raw[key]
            if not isinstance(val, expected_type):
                errors.append(
                    f"field '{key}' must be {expected_type.__name__}, got {type(val).__name__}"
                )
                return None
            return val

        slug = require("slug", str)
        if slug and not SLUG_RE.match(slug):
            errors.append(
                f"'slug' must be lowercase kebab-case (letters, digits, hyphens only), got '{slug}'"
            )

        title = require("title", str)
        tag = require("tag", str)
        org = require("org", str)
        dates = require("dates", str)
        short = require("short", str)
        overview = require("overview", str)
        stack = require("stack", list)
        approach = require("approach", list)
        raw_links = require("links", list)

        if short and len(short) > 260:
            errors.append(
                f"'short' description is {len(short)} chars; keep it under ~260 for the card grid"
            )
        if not approach:
            errors.append("'approach' must contain at least one bullet point")

        links: list[Link] = []
        if raw_links is not None:
            for i, l in enumerate(raw_links):
                if not isinstance(l, dict) or "label" not in l or "href" not in l:
                    errors.append(f"links[{i}] must be a mapping with 'label' and 'href'")
                    continue
                links.append(Link(label=l["label"], href=l["href"]))

        if errors:
            joined = "\n  - ".join(errors)
            raise ContentValidationError(f"{source_file}:\n  - {joined}")

        return cls(
            slug=slug,
            tag=tag,
            title=title,
            org=org,
            dates=dates,
            short=short,
            stack=stack,
            overview=overview,
            approach=approach,
            links=links,
            team=raw.get("team", ""),
            source_file=source_file,
        )


def load_entries(directory: Path) -> list[Entry]:
    """Load and validate every .yaml file in a directory, sorted by filename
    (files are numerically prefixed, e.g. 01-slug.yaml, to control display order)."""
    import yaml

    entries = []
    seen_slugs: dict[str, str] = {}
    for path in sorted(directory.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text())
        entry = Entry.from_dict(raw, source_file=str(path))
        if entry.slug in seen_slugs:
            raise ContentValidationError(
                f"duplicate slug '{entry.slug}' in {path} (already used by {seen_slugs[entry.slug]})"
            )
        seen_slugs[entry.slug] = str(path)
        entries.append(entry)
    return entries
