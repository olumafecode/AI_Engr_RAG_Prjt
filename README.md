# Veridane Policy Assistant

A retrieval-augmented generation (RAG) application that answers staff questions about the policies of Veridane Bank, a fictional commercial bank. Answers are grounded in the bank's policy documents and cite the document and section they come from.

Built for the Quantic MSSE AI Engineering Project. Veridane Bank, its people, regulators, laws, and systems are all fictional.

## Project status

| Stage | Status |
|---|---|
| 0. Repository, environment, and CI | Done |
| 1. Policy corpus and success metrics | Done |
| 2. Ingestion and indexing | Next |
| 3. Retrieval and generation | Planned |
| 4. Web application | Placeholder page and API contract in place |
| 5. Deployment to Render | Workflow ready; waiting for a Render service |
| 6. Evaluation | Metrics and targets defined |
| 7. Documentation and demo | In progress |

## Repository layout

```
.
├── app/                     Flask application
│   ├── __init__.py          App factory (create_app)
│   ├── __main__.py          Local dev server: python -m app
│   ├── config.py            Settings read from environment variables
│   ├── corpus_utils.py      Finding and reading corpus files
│   ├── routes.py            /, /chat, /health
│   └── templates/index.html Chat page
├── corpus/                  The 14 policy documents the app answers from
├── corpus_src/              Markdown sources for the three PDF policies
├── scripts/
│   ├── corpus_stats.py      Word and page counts for the corpus
│   └── render_pdfs.py       Rebuilds the PDFs from corpus_src/
├── tests/                   pytest suite (app and corpus checks)
├── .github/workflows/ci.yml GitHub Actions: lint, test, deploy
├── requirements.txt         Runtime dependencies (pinned)
├── requirements-dev.txt     Test and tooling dependencies (pinned)
├── wsgi.py                  Production entry point for gunicorn
├── design-and-evaluation.md Design decisions and evaluation results
├── ai-tooling.md            How AI tools were used
└── deployed.md              Link to the deployed app
```

## Prerequisites

- Python 3.11 (3.12 also works)
- Git
- VS Code with the Python and Ruff extensions (VS Code offers to install them when you open the folder)

## Setup

macOS or Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Windows (PowerShell):

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
copy .env.example .env
```

If PowerShell refuses to run the activation script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.

Open `.env` and add your API keys when a later stage needs them. The `.env` file is ignored by Git and must never be committed.

## Run the app

```bash
python -m app
```

Then open http://127.0.0.1:5000. In production (Linux, including Render) the app runs with `gunicorn wsgi:app`.

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Chat page |
| `/chat` | POST | Takes `{"question": "..."}` and returns an answer with citations. Returns 501 until Stage 3 is built. |
| `/health` | GET | Returns `{"status": "ok", ...}` with the app version and corpus document count |

## Tests and checks

```bash
pytest -q                     # app and corpus tests
ruff check .                  # lint
python -m scripts.corpus_stats  # corpus word and page counts
```

## The corpus

`corpus/` holds 14 documents (about 24,200 words, roughly 48 pages) in four formats: 8 Markdown, 2 HTML, 3 PDF, and 1 plain text. Every file name starts with its document ID, for example `VB-POL-006_internal_control.pdf`.

The three PDFs are generated from the Markdown files in `corpus_src/`. To change a PDF policy, edit its source and rebuild:

```bash
python -m scripts.render_pdfs
```

Rendering is deterministic, so rebuilding unchanged sources produces identical files.

Keep `corpus/` for policy documents only. The ingestion step indexes everything in that folder, and the test suite fails if any other kind of file appears there.

## Configuration

All settings are read from environment variables, with defaults in `app/config.py`. See `.env.example` for the full list. The main ones:

| Variable | Default | Used from |
|---|---|---|
| `SEED` | 42 | Stage 0 |
| `EMBEDDING_MODEL` | BAAI/bge-small-en-v1.5 | Stage 2 |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | 400 / 60 tokens | Stage 2 |
| `TOP_K` | 5 | Stage 3 |
| `GROQ_API_KEY` | (none) | Stage 3 |
| `LLM_MODEL` | llama-3.1-8b-instant | Stage 3 |
| `JUDGE_MODEL` | llama-3.3-70b-versatile | Stage 6 |

## CI/CD

`.github/workflows/ci.yml` runs on every push and pull request:

1. Installs the pinned dependencies on Python 3.11.
2. Lints with Ruff.
3. Imports and builds the app (`python -c "import app; app.create_app()"`).
4. Runs the test suite.

On a push to `main`, a second job triggers a Render deploy, but only after the tests pass. It calls the deploy hook stored in the repository secret `RENDER_DEPLOY_HOOK_URL`. Until that secret exists, the deploy job skips itself and reports success.

## Reproducibility

- Dependencies are pinned to exact versions.
- `SEED` fixes random seeds for any sampling.
- Corpus files are always processed in sorted order.
- PDF rendering is deterministic.

## Documentation

- [design-and-evaluation.md](design-and-evaluation.md): design decisions, corpus, metrics, and evaluation results
- [ai-tooling.md](ai-tooling.md): how AI tools were used, and what worked and what didn't
- [deployed.md](deployed.md): link to the deployed application
