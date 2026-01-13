# Copilot instructions for this repository

This repo is a small Django backend. The goal of this document is to give an AI coding agent the minimal, precise context needed to be immediately productive here.

- **Project type:** Django project (Django 6.x). Top-level Django project package: `hotel/`. Entry-point CLI: `manage.py`.
- **Python environment:** A virtualenv lives at `.venv/` (use `./.venv/bin/python` and `./.venv/bin/pip`). Use `install.sh` or `requirements.txt` / `pyproject.toml` / `uv.lock` to install dependencies. `uv.lock` is the lockfile produced by the `uv` package manager used in this repo.
- **Key files to inspect first:** `manage.py`, `hotel/settings.py`, `pyproject.toml`, `uv.lock`, `requirements.txt`, `install.sh`, `db.sqlite3`.

Quick commands (run inside the workspace):

```
# install deps into the repo virtualenv
chmod +x install.sh
./install.sh

# run Django CLI (if virtualenv not activated, use .venv/bin/python)
./.venv/bin/python manage.py migrate
./.venv/bin/python manage.py runserver
./.venv/bin/python manage.py test
```

What to know about structure and conventions:

- The Django project module is `hotel/` (settings, urls, wsgi). App code is expected at either `apps/` or top-level packages; search for `models.py`, `views.py`, and `urls.py` to find business logic.
- Database: default SQLite file at `db.sqlite3` (migrations will modify this file in repo; pull requests that change migrations should include the generated migration files).
- Dependencies are declared in `pyproject.toml` and locked in `uv.lock`. If you add/remove dependencies, update `pyproject.toml` and run the `uv` workflow locally to update `uv.lock` (or leave instructions in the PR for maintainers to run `uv lock`).
- Secrets: `hotel/settings.py` currently contains a development `SECRET_KEY` and `DEBUG = True`. Do not commit production secrets; prefer adding `.env` or using CI secrets for production configuration.

Typical agent workflow for a change:

1. Run `./install.sh` to ensure dependencies are installed in `.venv`.
2. Run quick test steps: `./.venv/bin/python manage.py check` and `./.venv/bin/python manage.py test` (if tests exist).
3. Make small, incremental code changes. If you add models, run `makemigrations` and include migration files in the PR: `./.venv/bin/python manage.py makemigrations`.
4. When changing dependencies, update `pyproject.toml` and regenerate `uv.lock` (explain steps in PR if you cannot regenerate lockfile here).

Integration points and external dependencies:

- Primary external dependency is Django (see `pyproject.toml` and `uv.lock`). No other external service integrations were detected in the repository; search for HTTP clients, database connection strings, or `settings` keys for service credentials.

Examples from this repo:

- Django entry: `manage.py` (runs CLI with `DJANGO_SETTINGS_MODULE = "hotel.settings"`).
- Settings: `hotel/settings.py` (SQLite DB, default installed apps list, `DEBUG = True`).
- Lockfile: `uv.lock` (contains pinned package versions; prefer updating it when changing deps).

Rules for edits and PRs by an AI agent:

- Keep changes minimal and focused to one concern per PR (code + tests + migrations where appropriate).
- Include commands to reproduce your change in the PR description (how to run, test, and any setup steps). Example: `./install.sh && ./.venv/bin/python manage.py migrate && ./.venv/bin/python manage.py runserver`.
- If you change dependencies but cannot run `uv` to lock, clearly state the required `uv` commands in the PR so maintainers can update `uv.lock`.

If anything in this document is unclear or you need additional project-specific rules (naming conventions, preferred test frameworks, CI hooks), ask for that explicitly so the maintainers can add it here.
