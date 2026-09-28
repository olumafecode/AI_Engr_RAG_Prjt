"""Load the assistant in the background once the server is running, and track progress.

Loading the embedding model takes about 15 seconds on Render's free instance
(a tenth of a CPU). Doing it in a background thread lets /health answer
Render's health checks meanwhile. The thread is started after the app has
been imported (from gunicorn's post_worker_init hook, or from `python -m app`),
never during the import itself.

While the warm-up runs, /chat waits for it for a short time instead of loading
a second copy of the model. If the warm-up has not finished in 90 seconds,
the stack of every thread is written to the log so a stall can be diagnosed.
"""

from __future__ import annotations

import faulthandler
import logging
import sys
import threading
import time

from flask import Flask

STALL_DUMP_SECONDS = 90


class WarmUp:
    """Progress of the background warm-up: off, running, ready, or failed."""

    def __init__(self) -> None:
        self.state = "off"
        self.error = ""
        self.seconds: float | None = None
        self.done = threading.Event()

    def as_dict(self) -> dict:
        return {"state": self.state, "seconds": self.seconds, "error": self.error or None}


def warmup_status(flask_app: Flask) -> WarmUp:
    return flask_app.extensions.setdefault("warmup", WarmUp())


def start_warm_up(flask_app: Flask) -> threading.Thread | None:
    """Start the warm-up thread once; later calls do nothing."""
    status = warmup_status(flask_app)
    if status.state in ("running", "ready"):
        return None
    status.state, status.error = "running", ""
    status.done.clear()
    thread = threading.Thread(target=_run, args=(flask_app, status), name="warm-up", daemon=True)
    thread.start()
    return thread


def _run(flask_app: Flask, status: WarmUp) -> None:
    from app.routes import get_assistant

    log = logging.getLogger("app")
    log.info("Warm-up started")
    started = time.perf_counter()
    faulthandler.dump_traceback_later(STALL_DUMP_SECONDS, exit=False, file=sys.stderr)
    try:
        with flask_app.app_context():
            get_assistant().warm_up()
    except Exception as error:  # noqa: BLE001 - a failed warm-up must not stop the server
        status.state, status.error = "failed", f"{type(error).__name__}: {error}"
        log.exception("Warm-up failed; the assistant will load on the first question")
    else:
        status.state = "ready"
        status.seconds = round(time.perf_counter() - started, 1)
        log.info("Warm-up finished in %.1f s", status.seconds)
    finally:
        faulthandler.cancel_dump_traceback_later()
        status.done.set()
