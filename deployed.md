# Deployed Application

**Live URL:** [replace with your Render URL, for example https://veridane-policy-assistant.onrender.com]

| Page | Path |
|---|---|
| Chat page | `/` |
| Health check (JSON) | `/health` |
| Chat API | `POST /chat` with `{"question": "..."}` |
| Source documents | `/docs/<doc ID>`, for example `/docs/VB-POL-002` |

## How it is deployed

- A Render free web service, defined in [render.yaml](render.yaml).
- The build installs the dependencies and builds the vector index (`python -m app.ingest`), so the index and the embedding model are part of the deployed build.
- The server is gunicorn with one worker and two threads. The model and index load in the background at start-up.
- Deploys are triggered only by the GitHub Actions workflow, after lint and tests pass on `main`. Render's own auto-deploy is turned off.
- The Groq API key is stored as a secret in Render, not in the repository.

## Note for reviewers

Render's free tier puts the service to sleep after 15 minutes without traffic. The first request after that takes about a minute while it wakes up; after that, answers usually take a couple of seconds. If the page shows Render's loading screen, wait a moment and it will open.
