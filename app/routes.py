"""HTTP routes: the chat page, the chat API, source documents, and the health check."""

from __future__ import annotations

import re
import sys
import threading
import time

from flask import Blueprint, abort, current_app, jsonify, render_template, request, send_file

from app.assistant import PolicyAssistant
from app.corpus_utils import doc_id_from_filename, list_documents
from app.generation import LLMNotConfiguredError, LLMUnavailableError
from app.parsing import parse_document
from app.retrieval import IndexNotReadyError
from app.warmup import warmup_status

bp = Blueprint("main", __name__)

DOC_ID = re.compile(r"^VB-(?:ORG|POL)-\d{3}$")
CHAT_WAIT_FOR_WARMUP_SECONDS = 20
_assistant_lock = threading.Lock()


def get_assistant() -> PolicyAssistant:
    """Create the assistant on first use (loading the embedding model takes a few seconds)."""
    extensions = current_app.extensions
    if "policy_assistant" not in extensions:
        with _assistant_lock:
            if "policy_assistant" not in extensions:
                extensions["policy_assistant"] = PolicyAssistant(current_app.config["SETTINGS"])
    return extensions["policy_assistant"]


def _peak_memory_mb() -> float | None:
    """Peak resident memory of this process, where the platform reports it (not Windows)."""
    try:
        import resource
    except ImportError:
        return None
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    divisor = 1024 * 1024 if sys.platform == "darwin" else 1024  # bytes on macOS, KB on Linux
    return round(peak / divisor, 1)


@bp.get("/")
def index():
    return render_template("index.html")


@bp.get("/health")
def health():
    """Cheap by design: Render calls it every few seconds and allows 5 seconds for a reply."""
    settings = current_app.config["SETTINGS"]
    static = current_app.config["HEALTH_STATIC"]
    return jsonify(
        status="ok",
        version=current_app.config["VERSION"],
        corpus_documents=static["corpus_documents"],
        index=static["index"],
        llm_configured=bool(settings.groq_api_key),
        assistant_ready="policy_assistant" in current_app.extensions,
        warmup=warmup_status(current_app).as_dict(),
        uptime_seconds=round(time.time() - current_app.config["STARTED_AT"]),
        peak_memory_mb=_peak_memory_mb(),
    )


@bp.post("/chat")
def chat():
    settings = current_app.config["SETTINGS"]
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify(error='Send a JSON body such as {"question": "..."}.'), 400

    question = payload.get("question")
    if not isinstance(question, str) or not question.strip():
        return jsonify(error="The 'question' field must be a non-empty string."), 400

    if len(question) > settings.max_question_chars:
        limit = settings.max_question_chars
        return jsonify(error=f"Questions are limited to {limit} characters."), 400

    warmup = warmup_status(current_app)
    if warmup.state == "running" and not warmup.done.wait(CHAT_WAIT_FOR_WARMUP_SECONDS):
        message = "The assistant is still starting up. Please try again in a few seconds."
        return jsonify(error=message), 503

    try:
        answer = get_assistant().answer(question.strip())
    except (IndexNotReadyError, LLMNotConfiguredError) as error:
        return jsonify(error=str(error)), 503
    except LLMUnavailableError:
        current_app.logger.exception("LLM request failed")
        message = "The language model is unavailable right now. Try again in a moment."
        return jsonify(error=message), 503
    return jsonify(answer.to_dict())


@bp.get("/docs/<doc_id>")
def document(doc_id: str):
    """Serve a source policy so citation links can open it at the cited section."""
    if not DOC_ID.match(doc_id):
        abort(404)
    settings = current_app.config["SETTINGS"]
    path = next(
        (p for p in list_documents(settings.corpus_dir) if doc_id_from_filename(p) == doc_id),
        None,
    )
    if path is None:
        abort(404)
    if path.suffix in (".pdf", ".html"):
        return send_file(path)
    return render_template("document.html", document=parse_document(path))
