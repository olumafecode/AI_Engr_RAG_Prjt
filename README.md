# Veridane Policy Assistant

A retrieval-augmented generation (RAG) application that answers staff questions about the policies of Veridane Bank, a fictional commercial bank. Answers are grounded in the bank's policy documents and cite the document and section they come from.

Built for the Quantic MSSE AI Engineering Project. Veridane Bank, its people, regulators, laws, and systems are all fictional.

## Project status

| Stage | Status |
|---|---|
| 0. Repository, environment, and CI | Done |
| 1. Policy corpus and success metrics | Done |
| 2. Ingestion and indexing | Done |
| 3. Retrieval and generation | Next |
| 4. Web application | Placeholder page and API contract in place |
| 5. Deployment to Render | Workflow ready; waiting for a Render service |
| 6. Evaluation | Metrics and targets defined |
| 7. Documentation and demo | In progress |

## Repository layout

```
.
├── app/                     Flask application and RAG pipeline
│   ├── __init__.py          App factory (create_app)
│   ├── __main__.py          Local dev server: python -m app
│   ├── config.py            Settings read from environment variables
│   ├── corpus_utils.py      Finding and reading corpus files
│   ├── parsing.py           Parse and clean md, txt, html, and pdf into sections
│   ├── chunking.py          Heading-aware and window chunking
│   ├── embeddings.py        bge-small embedder (fastembed) and an offline test embedder
│   ├── vector_store.py      Chroma collection wrapper
│   ├── index_manifest.py    Records how the index was built
│   ├── ingest.py            Builds the index: python -m app.ingest
│   ├── retrieval.py         Top-k search over the index
│   ├── search.py            Command-line search: python -m app.search
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

- Python 3.12 (3.11 also works)
- Git
- VS Code with the Python and Ruff extensions (VS Code offers to install them when you open the folder)

## Setup

macOS or Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Windows (PowerShell):

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
copy .env.example .env
```

If PowerShell refuses to run the activation script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.

Open `.env` and add your API keys when a later stage needs them. The `.env` file is ignored by Git and must never be committed.

## Build the index

```bash
python -m app.ingest
```

This parses and cleans all 14 documents, splits them into chunks, embeds each chunk with BAAI/bge-small-en-v1.5, and stores the vectors in Chroma under `.chroma/`. The first run downloads the embedding model (about 67 MB) into `.cache/fastembed/`; later runs reuse it.

Useful options:

```bash
python -m app.ingest --dry-run                      # parse and chunk only, no download
python -m app.ingest --strategy window --chunk-size 200 --chunk-overlap 30
```

Each build also writes `.chroma/index_manifest.json` (settings and chunk statistics) and `.chroma/chunks.jsonl` (every chunk's text and metadata) so you can inspect exactly what was indexed.

Check retrieval from the command line:

```bash
python -m app.search "How long is mandatory block leave?"
python -m app.search "Who approves international travel?" --k 3
```

## Run the app

```bash
python -m app
```

Then open http://127.0.0.1:5000. In production (Linux, including Render) the app runs with `gunicorn wsgi:app`.

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Chat page |
| `/chat` | POST | Takes `{"question": "..."}` and returns an answer with citations. Returns 501 until Stage 3 is built. |
| `/health` | GET | Returns `{"status": "ok", ...}` with the app version, corpus document count, and index status (built, chunk count, up to date with the corpus) |

## Tests and checks

```bash
pytest -q                       # app, corpus, parsing, chunking, and index tests
ruff check .                    # lint
python -m scripts.corpus_stats  # corpus word and page counts
```

The test suite uses an offline stand-in embedder, so it runs without downloading the model.

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
| `EMBEDDING_MODEL` | BAAI/bge-small-en-v1.5 (`hash` selects the offline test embedder) | Stage 2 |
| `CHUNK_STRATEGY` | heading (or window) | Stage 2 |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | 350 / 50 tokens | Stage 2 |
| `CHROMA_DIR` / `MODEL_CACHE_DIR` | .chroma / .cache/fastembed | Stage 2 |
| `TOP_K` | 5 | Stage 2 |
| `GROQ_API_KEY` | (none) | Stage 3 |
| `LLM_MODEL` | llama-3.1-8b-instant | Stage 3 |
| `JUDGE_MODEL` | llama-3.3-70b-versatile | Stage 6 |

## CI/CD

`.github/workflows/ci.yml` runs on every push and pull request:

1. Installs the pinned dependencies on Python 3.12.
2. Lints with Ruff.
3. Imports and builds the app (`python -c "import app; app.create_app()"`).
4. Runs the test suite.
5. Builds the full vector index with the real embedding model.
6. Runs a retrieval smoke test that fails unless the Password and Access Control Policy is among the top results for a password question.

On a push to `main`, a second job triggers a Render deploy, but only after the tests pass. It calls the deploy hook stored in the repository secret `RENDER_DEPLOY_HOOK_URL`. Until that secret exists, the deploy job skips itself and reports success.

## Reproducibility

- Dependencies are pinned to exact versions.
- `SEED` fixes random seeds for any sampling.
- Corpus files are always processed in sorted order, and chunk IDs (for example `VB-POL-006-012`) are assigned in that order, so a rebuild produces the same chunks.
- PDF rendering is deterministic.
- The index manifest records a fingerprint of the corpus, and `/health` reports whether the index is out of date.

## Documentation

- [design-and-evaluation.md](design-and-evaluation.md): design decisions, corpus, metrics, and evaluation results
- [ai-tooling.md](ai-tooling.md): how AI tools were used, and what worked and what didn't
- [deployed.md](deployed.md): link to the deployed application
