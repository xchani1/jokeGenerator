# Handout: Building a Gemini Joke Generator (Vertex AI)

A summary of what we built, how it works, what went wrong, and what is left to do.

## 1. What we built

A data analytics joke generator that calls Gemini on Google Vertex AI, in three forms:

| Form | How to run | Topics |
|---|---|---|
| Command line | `python main.py` | Free text (Enter = random) |
| Local web UI | `python app.py`, open http://127.0.0.1:8000 | Free text (Enter = random) |
| GitHub Pages site | Deployed by GitHub Actions (**not finished**, see section 6) | Preset topics only |

Repo: https://github.com/xchani1/jokeGenerator

## 2. Files

| File | Purpose |
|---|---|
| `creds.json` | Service-account key for Vertex AI. **Secret, git-ignored, never commit.** |
| `main.py` | `make_client()`, `generate_joke()` and the CLI |
| `app.py` | Local server: serves `index.html` and exposes `POST /api/joke` |
| `index.html` | Web UI for the local server (calls `/api/joke`) |
| `generate_jokes.py` | Pre-generates jokes for every topic into `docs/jokes.json` |
| `docs/index.html` | Static page for GitHub Pages (reads `jokes.json`) |
| `.github/workflows/pages.yml` | Workflow: generate jokes, then deploy `docs/` to Pages |
| `.gitignore` | Ignores `creds.json`, `.env`, `__pycache__/`, `docs/jokes.json` |
| `README.md` | Short project readme |

## 3. Key concepts

### Authenticating to Vertex AI with a service account
```python
credentials = service_account.Credentials.from_service_account_info(
    info, scopes=["https://www.googleapis.com/auth/cloud-platform"])
client = genai.Client(vertexai=True, project=project_id,
                      location="us-central1", credentials=credentials)
response = client.models.generate_content(model="gemini-2.5-flash", contents="...")
print(response.text)
```
- `vertexai=True` makes the `google-genai` SDK use Vertex AI, not the public Gemini API.
- The project ID is read from `creds.json`.

### Generation settings used
- `temperature=1.2` gives more varied, creative jokes.
- `max_output_tokens=500` caps the length of the reply.
- `thinking_budget=0` turns off Gemini 2.5's internal "thinking" (see section 4).

### Why a browser page can't call Vertex AI directly
A service-account key in browser code is readable by anyone who opens the page. So something outside the browser must hold the key. That is why the local UI needs `app.py`, and why GitHub Pages (static files only) needs a different design.

## 4. Problems we hit and how they were fixed

1. **Truncated joke** ("...The bartender asks, ")
   - Cause: `gemini-2.5-flash` spends part of `max_output_tokens` on hidden thinking tokens, leaving too little room for the answer.
   - Fix: `thinking_config=types.ThinkingConfig(thinking_budget=0)`, or raise the limit.

2. **`ModuleNotFoundError: No module named 'argparsesta'`**
   - Cause: a stray typo on the import line (`import argparsesta`).
   - Fix: `import argparse`. Lesson: read the traceback's last line, as the module name shows the typo.

3. **"Unexpected token '<', "<html>..." is not valid JSON"** in the web UI
   - Cause: the page was served by something other than `app.py` (VS Code Live Server, `python -m http.server`, or opened from disk). That server answered the `/api/joke` request with an HTML error page, and `res.json()` failed on it.
   - Fix: run `python app.py` and open http://127.0.0.1:8000. The page now explains this if it happens again.
   - Lesson: "starts with `<`" in a JSON error means you got HTML, so check which server answered.

4. **Git "Author identity unknown"**
   - Fix: set a repo-local identity with `git config user.email` and `git config user.name`. These were set for this repo only, not globally.

5. **GitHub Actions run failed at "Generate jokes with Vertex AI"**
   - Most likely cause: the `GCP_CREDENTIALS` secret is missing or wrong. This is not yet confirmed because the log needs a GitHub login.
   - See section 6.

## 5. Git and GitHub notes

- `git init -b main`, `git remote add origin <url>`, `git add -A`, `git commit`, `git push -u origin main`.
- Always check `git status` before committing. `creds.json` must not appear in the staged list.
- `.gitignore` only stops files from being *added*. If a secret is ever committed, deleting it later does not remove it from history, so rotate the key.
- `README.md` was committed, not ignored. (The request was read as "create a README".)

## 6. GitHub Pages: design and unfinished steps

### Design (pre-generated jokes)
GitHub Pages hosts static files only, so there is no live Gemini call per click. Instead:
1. A GitHub Actions workflow runs `generate_jokes.py` using the key stored as a repo secret.
2. It writes 6 jokes per topic into `docs/jokes.json`.
3. It deploys `docs/` to Pages.
4. The static page picks a random joke from that file.

The workflow runs on every push to `main`, weekly (Mondays 06:00 UTC), and on demand. `main.py` reads the key from the `GCP_CREDENTIALS` environment variable when it is set, and from `creds.json` otherwise.

Trade-off: topics are preset (no free text), and new jokes appear only when the workflow reruns.

### Steps still to do (if you ever continue)
1. GitHub repo, Settings, Secrets and variables, Actions, New repository secret: `GCP_CREDENTIALS` = the full contents of `creds.json`.
2. Settings, Pages, Source: **GitHub Actions**. (Right now it publishes the repo's top-level files, so the live site shows the local-only `index.html` and `jokes.json` returns 404.)
3. Actions tab, open the failed run, Re-run all jobs.
4. If it still fails, read the log of the "Generate jokes with Vertex AI" step. A permissions error probably means the service account needs the **Vertex AI User** role.
5. Site URL when working: https://xchani1.github.io/jokeGenerator/

### Alternatives considered
- **Cloud Run backend:** deploy `app.py` to Google Cloud Run. This gives free-text topics and live generation, but needs a Dockerfile and a deploy step, and the public endpoint needs rate limiting or a login to protect your Vertex AI bill.
- **Local only:** keep `python app.py`. A possible tweak is to auto-open the browser or add a `run.bat`.

## 7. Quick reference

```
# Run the CLI
python main.py

# Run the local web UI
python app.py          # then open http://127.0.0.1:8000

# Regenerate the joke pool locally
python generate_jokes.py --per-topic 6

# Install dependencies
pip install google-genai google-auth
```

## 8. Things to remember

- Never commit `creds.json` or put the key in front-end code.
- Keep secrets in `.env` or CI secrets, and make sure they are in `.gitignore`.
- When output looks cut off, check `max_output_tokens` against thinking tokens.
- When a JSON parse error shows HTML, you are talking to the wrong server.
