"""Veridane Policy Assistant: a RAG application over Veridane Bank's policy corpus."""

from __future__ import annotations

import logging
import random
import time

from flask import Flask

from app.config import Settings
from app.corpus_utils import list_documents
from app.index_manifest import index_status
from app.routes import bp

__version__ = "0.5.1"


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
    flask_app.config["STARTED_AT"] = time.time()
    flask_app.config["HEALTH_STATIC"] = {
        "corpus_documents": len(list_documents(settings.corpus_dir)),
        "index": index_status(settings),
    }
    return flask_app
