# EURIDICE DataLab

**Learn data science by doing — entirely in the browser.**
An open, Kaggle-style learning environment built by
[IIIM](https://www.iiim.is) (Icelandic Institute for Intelligent Machines)
for the [EURIDICE](https://euridice.eu) project (EU Digital Europe
Programme, Grant Agreement No. 101123121).

## What it is

- **Guided learning tracks** — Python foundations → Exploratory Data
  Analysis → Machine Learning fundamentals — each lesson built around a
  **live Jupyter notebook** embedded in the page.
- **Real code, zero setup** — Python (pandas, matplotlib, scikit-learn)
  runs *inside the learner's browser* via JupyterLite/Pyodide. No install,
  no account, no compute server.
- **Instant feedback** — graded exercises check answers on the spot,
  Kaggle-Learn style, with hints.
- **Teaching datasets** — synthetic, reproducible, EURIDICE-sector themed
  (media habits, student digital skills), downloadable and preloaded in the
  lab.
- **Credential-ready** — designed to plug into EURIDICE's
  Moodle-in-the-loop for formal assessment and microcredential issuance
  (EU Council Recommendation 2022/C 243/02 alignment).

## Why it's cheap to host

The entire product builds to **static files**. The learner's own machine
executes the Python. Hosting the DataLab = serving a folder — GitHub Pages,
Netlify, or any university web server. Cost is the same for 10 or 10,000
learners: ~€0.

## Repository layout

```
site/       Astro Starlight website (pages, components, styling)
lab/        JupyterLite source: notebooks, datasets, checker, config
scripts/    Generators (datasets, EU emblem, notebooks) + build.ps1
.github/    CI: build & deploy to GitHub Pages
```

Notebooks and datasets are **generated programmatically**
(`scripts/make_notebooks.py`, `scripts/make_datasets.py`) — reviewable,
diffable, reproducible.

## Build locally

Prereqs: Python 3.10+, Node.js 20+.

```powershell
# one-time setup
python -m venv .venv
.venv\Scripts\pip install jupyterlite-core==0.8.1 jupyterlite-pyodide-kernel==0.8.1 jupyter_server pandas nbformat scikit-learn matplotlib missingno seaborn

# full build (datasets → notebooks → lab → site)
powershell -File scripts\build.ps1

# or run the dev server while editing content
cd site; npm install; npm run dev
```

Deployable output lands in `site/dist/`.

## Deploying

- **GitHub Pages:** in the repo, *Settings → Pages → Source: GitHub
  Actions*. Every push to `main` then builds, checks and publishes the site.
  The workflow reads the Pages address itself, so the same build works at
  `https://<user>.github.io/<repo>/` and, once connected, a custom domain.
- **Any other static host:** serve `site/dist`. For a sub-folder deploy,
  build with `ASTRO_BASE=/<folder>` (content links are prefixed
  automatically).

## Extending

- **New lesson:** add cells in `scripts/make_notebooks.py`, add an `.mdx`
  page under `site/src/content/docs/tracks/`, add the sidebar entry in
  `site/astro.config.mjs`, rebuild.
- **New dataset:** add a generator in `scripts/make_datasets.py` (write to
  both output locations), document it on the Datasets page.
- **New checker questions:** extend `lab/notebooks/datalab_checks.py` —
  ground truth is computed from the data, so regeneration never breaks it.

## Licence & funding

Learning materials © IIIM, licensed
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); source code under
the MIT License. See [LICENSE](LICENSE).

Co-funded by the European Union under the Digital Europe Programme, project
EURIDICE (Grant Agreement No. 101123121). Views and opinions expressed are
those of the author(s) only and do not necessarily reflect those of the
European Union or the European Commission.
