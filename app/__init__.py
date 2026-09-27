"""Veridane Policy Assistant: a RAG application over Veridane Bank's policy corpus."""

from __future__ import annotations

import logging
import random

from flask import Flask

from app.config import Settings
from app.routes import bp

__version__ = "0.2.0"


def create_app(settings: Settings | None = None) -> Flask:
    """Build and configure the Flask application."""
    settings = settings or Settings.from_env()

    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    random.seed(settings.seed)

    flask_app = Flask(__name__)
    flask_app.config["SETTINGS"] = settings
    flask_app.config["VERSION"] = __version__
    flask_app.register_blueprint(bp)
    return flask_app
