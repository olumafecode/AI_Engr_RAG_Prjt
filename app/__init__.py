"""Veridane Policy Assistant: a RAG application over Veridane Bank's policy corpus."""

from __future__ import annotations

import logging
import random
import threading
import time

from flask import Flask

from app.config import Settings
from app.routes import bp

__version__ = "0.4.0"


def create_app(settings: Settings | None = None, assistant=None) -> Flask:
    """Build and configure the Flask application.

    Tests can pass a ready-made assistant; otherwise one is created on the first /chat request.
    """
    settings = settings or Settings.from_env()

    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    for noisy in ("httpx", "httpx2", "chromadb"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    random.seed(settings.seed)

    flask_app = Flask(__name__)
    flask_app.config["SETTINGS"] = settings
    flask_app.config["VERSION"] = __version__
    if assistant is not None:
        flask_app.extensions["policy_assistant"] = assistant
    flask_app.register_blueprint(bp)

    if settings.warmup_on_start and assistant is None:
        thread = threading.Thread(target=_warm_up, args=(flask_app,), daemon=True)
        flask_app.extensions["warmup_thread"] = thread
        thread.start()
    return flask_app


def _warm_up(flask_app: Flask) -> None:
    """Load the embedding model and index in the background so /health answers at once."""
    from app.routes import get_assistant

    log = logging.getLogger("app")
    started = time.perf_counter()
    with flask_app.app_context():
        try:
            get_assistant().warm_up()
        except Exception:  # noqa: BLE001 - a failed warm-up must not stop the server
            log.exception("Warm-up failed; the assistant will load on the first question")
            return
    log.info("Warm-up finished in %.1f s", time.perf_counter() - started)
