#!/usr/bin/env python3
"""
Content and build tests. Run with:

    python3 -m unittest tests.test_content -v

or via `make test`. Runs in CI on every push (see .github/workflows/deploy.yml)
so a broken or malformed content file fails the build before it ever reaches
GitHub Pages.
"""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from content.schema import ContentValidationError, load_entries

PROJECTS_DIR = ROOT / "data" / "projects"
COURSEWORK_DIR = ROOT / "data" / "coursework"


class TestContentSchema(unittest.TestCase):
    """Every YAML file must parse and validate against the schema."""

    def test_projects_load_without_error(self):
        try:
            entries = load_entries(PROJECTS_DIR)
        except ContentValidationError as e:
            self.fail(f"Project content failed validation:\n{e}")
        self.assertGreater(len(entries), 0, "expected at least one project")

    def test_coursework_loads_without_error(self):
        try:
            entries = load_entries(COURSEWORK_DIR)
        except ContentValidationError as e:
            self.fail(f"Coursework content failed validation:\n{e}")
        self.assertGreater(len(entries), 0, "expected at least one coursework entry")


class TestSlugs(unittest.TestCase):
    """Slugs must be unique (within each section) and filesystem/URL-safe."""

    SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

    def test_project_slugs_unique_and_valid(self):
        entries = load_entries(PROJECTS_DIR)
        slugs = [e.slug for e in entries]
        self.assertEqual(len(slugs), len(set(slugs)), "duplicate project slug found")
        for slug in slugs:
            self.assertRegex(slug, self.SLUG_RE, f"invalid slug format: {slug}")

    def test_coursework_slugs_unique_and_valid(self):
        entries = load_entries(COURSEWORK_DIR)
        slugs = [e.slug for e in entries]
        self.assertEqual(len(slugs), len(set(slugs)), "duplicate coursework slug found")
        for slug in slugs:
            self.assertRegex(slug, self.SLUG_RE, f"invalid slug format: {slug}")

    def test_no_cross_section_slug_collisions(self):
        """A project and a coursework entry could share a slug without the
        schema catching it (uniqueness is only checked within a directory),
        but that would break the /assets/documents/ folder naming scheme
        readability. Not fatal, but worth flagging."""
        project_slugs = {e.slug for e in load_entries(PROJECTS_DIR)}
        course_slugs = {e.slug for e in load_entries(COURSEWORK_DIR)}
        overlap = project_slugs & course_slugs
        self.assertEqual(overlap, set(), f"slug(s) used in both sections: {overlap}")


class TestLinkHygiene(unittest.TestCase):
    """Sanity-check links: no empty hrefs, no obviously broken markup."""

    def _check(self, entries):
        for e in entries:
            self.assertGreater(len(e.links), 0, f"{e.slug}: has no links at all")
            for link in e.links:
                self.assertTrue(link.href.strip(), f"{e.slug}: link '{link.label}' has empty href")
                self.assertTrue(link.label.strip(), f"{e.slug}: a link has an empty label")

    def test_project_links(self):
        self._check(load_entries(PROJECTS_DIR))

    def test_coursework_links(self):
        self._check(load_entries(COURSEWORK_DIR))


class TestDocumentFoldersMatchContent(unittest.TestCase):
    """After a build, every entry should have a matching assets/documents/
    folder (build.py creates these automatically — this test catches the
    case where someone forgot to rerun the build after editing content)."""

    def _check(self, entries, kind):
        docs_dir = ROOT / "assets" / "documents" / kind
        if not docs_dir.exists():
            self.skipTest(f"{docs_dir} doesn't exist yet — run `make build` first")
        for e in entries:
            self.assertTrue(
                (docs_dir / e.slug).is_dir(),
                f"missing assets/documents/{kind}/{e.slug}/ — rerun `make build`",
            )

    def test_project_doc_folders(self):
        self._check(load_entries(PROJECTS_DIR), "projects")

    def test_coursework_doc_folders(self):
        self._check(load_entries(COURSEWORK_DIR), "coursework")


if __name__ == "__main__":
    unittest.main()