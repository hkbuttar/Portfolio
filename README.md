# Portfolio Site

A statically-generated portfolio: **content is data, not code**. Every
project and coursework entry lives as a validated YAML file; a small,
tested Python build system renders them through Jinja2 templates into
plain static HTML. No JavaScript framework, no Node — the *output* is a
handful of `.html`/`.css`/`.js` files deployable anywhere, but the
*build* is a real pipeline: schema validation, a test suite, and CI/CD
that deploys automatically on every push.

## Why this structure

The previous version of this generator worked, but content and code were
tangled together in one big Python file — adding a project meant editing a
Python dictionary by hand, with no validation and no safety net. This
version separates concerns properly:

| Layer | Lives in | Changes when... |
|---|---|---|
| **Content** | `data/projects/*.yaml`, `data/coursework/*.yaml` | you add/edit a project or course |
| **Schema/validation** | `content/schema.py` | you change what fields an entry requires |
| **Presentation** | `templates/*.html` | you change layout/markup |
| **Design tokens** | `style.css` | you change colors/type/spacing |
| **Orchestration** | `build.py` | rarely — it just wires the above together |

Adding a project is now a content change, not a code change: drop in a
YAML file, run the build. No template touched, no Python edited.

## Structure

```
.
├── data/
│   ├── projects/            # one YAML file per project (10 currently)
│   │   ├── 01-rakuten-capstone.yaml
│   │   ├── 02-qlora-recipe-chef.yaml
│   │   └── ...
│   └── coursework/           # one YAML file per coursework entry (2 currently)
│       ├── 01-advanced-ml-ai.yaml
│       └── 02-applied-genai-homework.yaml
│
├── content/
│   └── schema.py             # Entry/Link dataclasses + validation rules
│
├── templates/                 # Jinja2, with inheritance + shared partials
│   ├── base.html              # page shell: <head>, nav, footer
│   ├── home.html               # extends base — hero/about/résumé
│   ├── index.html              # extends base — the projects/coursework grid
│   ├── detail.html             # extends base — a single project/course page
│   └── partials/
│       ├── nav.html, footer.html, brush.html   # shared chrome
│       ├── card.html            # index-grid card macro
│       └── doc_card.html        # PDF/PPTX preview card macro
│
├── tests/
│   └── test_content.py        # schema validity, unique slugs, link hygiene
│
├── scripts/
│   └── new_entry.py            # scaffolds a new YAML entry from the CLI
│
├── .github/workflows/
│   └── deploy.yml              # CI: test → build → deploy to GitHub Pages
│
├── assets/
│   ├── resume.pdf              # placeholder — replace with your real résumé
│   └── documents/
│       ├── projects/<slug>/    # auto-synced to match data/projects/
│       └── coursework/<slug>/  # auto-synced to match data/coursework/
│
├── style.css                   # design system (colors, type, layout, doc-cards)
├── doc-viewer.js                # PDF preview lightbox (unchanged from before)
├── build.py                     # loads YAML → validates → renders → writes
├── requirements.txt
├── Makefile
│
└── index.html, projects.html, coursework.html,   ← generated output
    projects/*.html, coursework/*.html,             (rebuilt from templates
    sitemap.xml                                      + data every build)
```

## Quickstart

```bash
pip install -r requirements.txt
python3 build.py          # or: make build
python3 -m http.server    # or: make serve
```

## Adding a project or coursework entry

```bash
python3 scripts/new_entry.py project my-new-project
# → creates data/projects/11-my-new-project.yaml with placeholder fields
```

Fill in the placeholders (title, dates, stack, overview, approach bullets,
links), then rebuild:

```bash
python3 build.py
```

That's it — no template or Python code needs to change. The build:

1. Loads every `.yaml` file in `data/projects/` and `data/coursework/`
   (numeric filename prefixes control display order).
2. **Validates** each one against the schema in `content/schema.py` — a
   missing field, wrong type, bad slug format, or duplicate slug fails the
   build immediately with the exact file and reason, rather than silently
   producing broken HTML.
3. Renders `index.html`, `projects.html`, `coursework.html`, and one
   detail page per entry through the Jinja2 templates.
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

Covers: every YAML file parses and validates; slugs are unique and
URL-safe within and across sections; every entry has at least one
non-empty link; every entry's document folder exists after a build. These
run automatically in CI on every push and pull request — a broken content
file fails the check before it can reach the live site.

## Continuous deployment

`.github/workflows/deploy.yml` runs on every push to `main`: install
dependencies → run the test suite → build → deploy to GitHub Pages. To
enable it on your fork: push this repo to GitHub, then in
**Settings → Pages**, set the source to **GitHub Actions**. From then on,
editing a YAML file and pushing is the entire deploy process.

## Document previews (PDF/PPTX)

Every detail page's "Links & Documents" section renders `.pdf`/`.pptx`
links as visual preview cards, not plain text:

- **PDF** — a live thumbnail of the first page; click to open an in-page
  lightbox viewer (`doc-viewer.js`) with a close button and "open in new
  tab" fallback.
- **PPTX** — a styled placeholder icon (browsers can't render PowerPoint
  natively); click to open/download.

To attach one: drop the file into `assets/documents/<projects|coursework>/<slug>/`,
point the entry's YAML `links:` at it, rebuild.

## Before you deploy — 3 things to fill in

1. **Résumé** — replace `assets/resume.pdf` with your real résumé (same
   filename).
2. **Links** — several entries still have placeholder `href: '#'` links
   (live demos, a couple of unconfirmed repos, and this site's own
   repo/live-site links once you push it). Search `data/` for `href: '#'`.
3. **Contact info** — in `templates/partials/footer.html`, replace the
   email, LinkedIn, and GitHub placeholder URLs with your real ones.

## Deploying

**GitHub Pages (automatic, via CI)** — see "Continuous deployment" above.

**GitHub Pages (manual)**
```bash
python3 build.py
git add . && git commit -m "Update portfolio" && git push
```
Enable Pages in repo settings (Deploy from branch → main) once.

**Netlify Drop** — run `python3 build.py`, then drag the whole folder into
[netlify.com/drop](https://app.netlify.com/drop).

**Vercel** — `python3 build.py && vercel` (auto-detects a static site).

## Design system

- **Palette**: warm paper background, charcoal ink text, deep indigo +
  ochre accents (nods to oil paint).
- **Type**: Fraunces (display/headings), Inter (body), IBM Plex Mono
  (labels, tags, meta info).
- **Signature motif**: a hand-drawn brush-stroke underline (SVG, animates
  in on load) under every section heading — a nod to your painting
  practice.
- All tokens live at the top of `style.css` under `:root`.

This layer is unchanged from the previous version of this site — only the
build system changed, not the design.
