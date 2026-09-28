"""Run the local development server with `python -m app`."""

import os

from app import create_app
from app.warmup import start_warm_up

if __name__ == "__main__":
    app = create_app()
    # With the debug reloader, the app runs in a child process; warm up only there.
    if app.config["SETTINGS"].warmup_on_start and os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        start_warm_up(app)
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=True)
