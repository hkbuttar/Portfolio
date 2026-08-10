# Portfolio Site

A statically-generated portfolio: **content is data, not code**. Every
project, coursework, and work-experience entry lives as a validated YAML
file; a small, tested Python build system renders them through Jinja2
templates into plain static HTML. No JavaScript framework, no Node — the
*output* is a handful of `.html`/`.css`/`.js` files deployable anywhere,
but the *build* is a real pipeline: schema validation, a test suite, and
CI/CD that deploys automatically on every push.

## Why this structure

Content and code are kept deliberately separate:

| Layer | Lives in | Changes when... |
|---|---|---|
| **Content** | `data/projects/*.yaml`, `data/coursework/*.yaml`, `data/experience/*.yaml` | you add/edit a project, course, or job |
| **Schema/validation** | `content/schema.py` | you change what fields an entry requires |
| **Presentation** | `templates/*.html` | you change layout/markup |
| **Design tokens** | `style.css` | you change colors/type/spacing |
| **Orchestration** | `build.py` | rarely — it just wires the above together |

Adding a project, course, or job is a content change, not a code change:
drop in a YAML file, run the build. Education is the one exception — it's
a genuinely static page (two degrees, unlikely to grow), so it's hand-written
directly in `templates/education.html` rather than YAML-driven.

## Structure

```
.
├── data/
│   ├── projects/            # one YAML file per project (24 currently)
│   ├── coursework/           # one YAML file per coursework entry (2 currently)
│   └── experience/           # one YAML file per job (9 currently)
│
├── content/
│   └── schema.py             # Entry/Link dataclasses + validation rules
│
├── templates/                 # Jinja2, with inheritance + shared partials
│   ├── base.html              # page shell: <head>, nav, footer
│   ├── home.html               # extends base — hero (incl. profile photo)/about/résumé
│   ├── education.html          # extends base — static page, hand-written (not YAML)
│   ├── index.html              # extends base — the projects/coursework/experience grid
│   ├── detail.html             # extends base — a single project/course/job page
│   └── partials/
│       ├── nav.html, footer.html, brush.html   # shared chrome
│       ├── card.html            # index-grid card macro
│       └── doc_card.html        # PDF/PPTX preview card macro
│
├── tests/
│   └── test_content.py        # schema validity, unique slugs, link hygiene (9 tests)
│
├── scripts/
│   └── new_entry.py            # scaffolds a new project/coursework YAML entry from the CLI
│
├── .github/workflows/
│   └── deploy.yml              # CI: test → build → deploy to GitHub Pages
│
├── assets/
│   ├── HARLEEN-BUTTAR.pdf      # résumé, embedded on the home page
│   ├── profile-photo.png       # hero section photo (circular crop)
│   └── documents/
│       ├── projects/<slug>/    # auto-synced to match data/projects/ — 8 already have real decks/reports
│       ├── coursework/<slug>/  # auto-synced to match data/coursework/
│       └── experience/<slug>/  # auto-synced to match data/experience/ — 1 already has real docs
│
├── style.css                   # design system (colors, type, layout, doc-cards, hero photo)
├── doc-viewer.js                # PDF preview lightbox
├── build.py                     # loads YAML → validates → renders → writes
├── requirements.txt
├── Makefile
│
└── index.html, projects.html, coursework.html, experience.html, education.html,
    projects/*.html, coursework/*.html, experience/*.html,   ← generated output
    sitemap.xml                                                (rebuilt from templates
                                                                 + data every build)
```

## Quickstart

```bash
pip install -r requirements.txt
python3 build.py          # or: make build
python3 -m http.server    # or: make serve
```

## Adding a project, coursework, or experience entry

```bash
python3 scripts/new_entry.py project my-new-project
# → creates data/projects/25-my-new-project.yaml with placeholder fields
```

(Swap `project` for `coursework` to scaffold a coursework entry the same
way. `experience` entries don't currently have a scaffold script — copy an
existing file in `data/experience/` as a starting template instead.)

All three kinds share the same YAML schema and the same `detail.html`
template, but `kind` drives two small conditional differences: experience
entries show a **Skills** heading instead of **Tech Stack**, and their
`team` field is conventionally a location (`Chicago, IL`) rather than a
list of project teammates. Numeric filename prefixes (`01-`, `02-`, ...)
control display order within each section — renumber the surrounding
files if you insert an entry out of order (e.g. a new job that's more
recent than an existing one).

Fill in the placeholders (title, dates, stack, overview, approach bullets,
links), then rebuild:

```bash
python3 build.py
```

That's it — no template or Python code needs to change. The build:

1. Loads every `.yaml` file in `data/projects/`, `data/coursework/`, and
   `data/experience/` (numeric filename prefixes control display order).
2. **Validates** each one against the schema in `content/schema.py` — a
   missing field, wrong type, bad slug format, duplicate slug, or an
   empty/malformed YAML file fails the build immediately with the exact
   file and reason, rather than crashing with a raw traceback or silently
   producing broken HTML.
3. Renders `index.html`, `projects.html`, `coursework.html`,
   `experience.html`, `education.html`, and one detail page per
   project/coursework/experience entry through the Jinja2 templates.
4. Deletes stale pages for any entry you removed, and syncs
   `assets/documents/<kind>/<slug>/` folders to match current content
   (creating new ones, removing orphaned ones).
5. Writes `sitemap.xml`.

**To remove an entry:** delete its YAML file and rebuild — the generated
page and its document folder are cleaned up automatically.

## Tests

```bash
python3 -m unittest tests.test_content -v     # or: make test
```

Covers: every YAML file (projects, coursework, *and* experience) parses
and validates; slugs are unique and URL-safe within and across all three
sections; every entry has at least one non-empty link; every entry's
document folder exists after a build. These run automatically in CI on
every push and pull request — a broken content file fails the check
before it can reach the live site.

## Continuous deployment

`.github/workflows/deploy.yml` runs on every push to `main`: install
dependencies → run the test suite → build → deploy to GitHub Pages. To
enable it on your fork: push this repo to GitHub, then in
**Settings → Pages**, set the source to **GitHub Actions**. From then on,
editing a YAML file and pushing is the entire deploy process.

If a workflow run shows green on `test-and-build` but red on `deploy`
the very first time you enable Pages, it's usually because the Pages site
itself hadn't finished provisioning yet — reselecting "GitHub Actions" as
the source in Settings → Pages and re-running the job resolves it.

## Document previews (PDF/PPTX)

Every detail page's "Links & Documents" section renders `.pdf`/`.pptx`
links as visual preview cards, not plain text:

- **PDF** — a live thumbnail of the first page; click to open an in-page
  lightbox viewer (`doc-viewer.js`) with a close button and "open in new
  tab" fallback.
- **PPTX** — a styled placeholder icon (browsers can't render PowerPoint
  natively); click to open/download.

To attach one: drop the file into
`assets/documents/<projects|coursework|experience>/<slug>/`, point the
entry's YAML `links:` at it with a path relative to the repo root (e.g.
`assets/documents/experience/my-job/deck.pptx`) — matching the exact
filename, since a mismatch fails silently as a 404 rather than a build
error — rebuild.

Detail pages live one directory below the repo root (`projects/<slug>.html`,
etc.), so the `doc_card` Jinja macro (`templates/partials/doc_card.html`)
prefixes every document href with `{{ depth }}` (`../`) at render time —
the YAML `href` itself should never include that prefix.

## Site sections

- **Home** (`index.html`) — hero with photo, About, embedded résumé viewer
- **Education** (`education.html`) — static page, two degrees, hand-written
- **Experience** (`experience.html` + `experience/*.html`) — 9 roles, card
  grid → full detail page each, ordered most-recent-first by end date
- **Projects** (`projects.html` + `projects/*.html`) — 24 entries
- **Coursework** (`coursework.html` + `coursework/*.html`) — 2 entries

Nav order: Home / Experience / Education / Projects / Coursework.

## Status — what's real vs. still placeholder

- ✅ Résumé (`assets/HARLEEN-BUTTAR.pdf`), embedded and working
- ✅ Profile photo in the hero section
- ✅ 23 of 24 projects have real GitHub repo links; 8 projects + 1
  experience entry have real PDF/PPTX document previews attached
- ✅ The portfolio site's own repo/live-site links are populated (see
  `data/projects/portfolio-website.yaml`)
- ✅ Footer contact info (`templates/partials/footer.html`) — real email,
  LinkedIn, and GitHub links
- ⬜ Two entries still have placeholder `href: '#'` links (a Gradio demo, one
  unconfirmed GitHub repo). Search `data/` for `href: '#'`.

## Deploying

**GitHub Pages (automatic, via CI)** — see "Continuous deployment" above.

**GitHub Pages (manual)**
```bash
python3 build.py
git add . && git commit -m "Update portfolio" && git push
```
Enable Pages in repo settings (Source → GitHub Actions) once.

**Netlify Drop** — run `python3 build.py`, then drag the whole folder into
[netlify.com/drop](https://app.netlify.com/drop).

**Vercel** — `python3 build.py && vercel` (auto-detects a static site).

## Design system

- **Palette**: warm paper background, charcoal ink text, deep indigo +
  ochre accents (nods to oil paint).
- **Type**: Fraunces (display/headings), Inter (body), IBM Plex Mono
  (labels, tags, meta info).
- **Signature motif**: a hand-drawn brush-stroke underline (SVG, animates
  in on load) under every section heading, and a small brush accent on the
  hero photo — a nod to your painting practice.
- All tokens live at the top of `style.css` under `:root`.
