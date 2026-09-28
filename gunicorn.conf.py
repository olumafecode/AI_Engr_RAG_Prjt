"""gunicorn settings for production (Render). gunicorn reads this file automatically.

One worker keeps memory inside the free instance's 512 MB. Four threads mean
Render's health check always finds a free thread, even while a question is
being answered and the browser is loading the page.
"""

import os

bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
workers = 1
threads = 4
timeout = 120


def post_worker_init(worker):
    """Start loading the model once the worker has imported the app and is about to serve."""
    if os.environ.get("WARMUP_ON_START", "").strip().lower() in ("1", "true", "yes", "on"):
        from app.warmup import start_warm_up

        start_warm_up(worker.wsgi)
