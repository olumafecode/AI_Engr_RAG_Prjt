# Deployed Application

**Live URL:** https://veridane-policy-assistant.onrender.com

| Page | Path |
|---|---|
| Chat page | `/` |
| Health check (JSON) | `/health` |
| Chat API | `POST /chat` with `{"question": "..."}` |
| Source documents | `/docs/<doc ID>`, for example `/docs/VB-POL-002` |

## How it is deployed

- A Render free web service, defined in [render.yaml](render.yaml), with server settings in [gunicorn.conf.py](gunicorn.conf.py).
- The build installs the dependencies and builds the vector index (`python -m app.ingest`), so the index and the embedding model are part of the deployed build.
- The server is gunicorn with one worker and four threads. The model and index load in the background once the server has started, in about 12 to 15 seconds; `/health` shows the progress under `warmup`.
- Deploys are triggered only by the GitHub Actions workflow, after lint, tests, an index build, and a retrieval smoke test pass on `main`. Render's own auto-deploy is turned off.
- The Groq API key is stored as a secret in Render, not in the repository.

## Note for reviewers

Render's free tier puts the service to sleep after 15 minutes without traffic.

- **Waking up:** the first request after that took about 33 seconds in testing.
- **Loading the model:** after waking, the model takes about 15 seconds more to load. A question asked during that time waits for it, or asks you to try again in a few seconds.
- **Warm answers:** after that, answers took about 1.2 seconds at the median (1.9 seconds at the 95th percentile).

If the page shows Render's loading screen, wait a moment and it will open.
