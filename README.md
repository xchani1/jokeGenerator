# Joke Generator

Generates short data analytics jokes with Gemini on Vertex AI, from the command line or a small local web UI.

## Setup

1. `pip install google-genai google-auth`
2. Put your Vertex AI service-account key in `creds.json` next to the scripts (it is git-ignored, never commit it).

## Usage

- CLI: `python main.py [--model gemini-2.5-flash] [--location us-central1]`
- Web UI: `python app.py`, then open http://127.0.0.1:8000

Leave the topic blank to get a random one.

## Files

- `main.py` – client setup, joke generation and the CLI
- `app.py` – local server exposing `/api/joke` and serving the page
- `index.html` – the web interface

## GitHub Pages

The `docs/` site is static: a GitHub Actions workflow (`.github/workflows/pages.yml`) runs `generate_jokes.py` to pre-generate jokes for every topic into `docs/jokes.json`, then deploys `docs/` to Pages. It runs on every push to `main`, weekly, and on demand.

One-time setup in the repo on GitHub:
1. Settings → Secrets and variables → Actions → New repository secret: name `GCP_CREDENTIALS`, value = the full contents of `creds.json`.
2. Settings → Pages → Source: **GitHub Actions**.
3. Actions tab → "Deploy jokes to GitHub Pages" → Run workflow.
