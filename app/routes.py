"""HTTP routes: the chat page, the chat API, source documents, and the health check."""

from __future__ import annotations

import re
import threading

from flask import Blueprint, abort, current_app, jsonify, render_template, request, send_file

from app.assistant import PolicyAssistant
from app.corpus_utils import doc_id_from_filename, list_documents
from app.generation import LLMNotConfiguredError, LLMUnavailableError
from app.index_manifest import index_status
from app.parsing import parse_document
from app.retrieval import IndexNotReadyError

bp = Blueprint("main", __name__)

DOC_ID = re.compile(r"^VB-(?:ORG|POL)-\d{3}$")
_assistant_lock = threading.Lock()


def get_assistant() -> PolicyAssistant:
    """Create the assistant on first use (loading the embedding model takes a few seconds)."""
    extensions = current_app.extensions
    if "policy_assistant" not in extensions:
        with _assistant_lock:
            if "policy_assistant" not in extensions:
                extensions["policy_assistant"] = PolicyAssistant(current_app.config["SETTINGS"])
    return extensions["policy_assistant"]


@bp.get("/")
def index():
    return render_template("index.html")


@bp.get("/health")
def health():
    settings = current_app.config["SETTINGS"]
    return jsonify(
        status="ok",
        version=current_app.config["VERSION"],
        corpus_documents=len(list_documents(settings.corpus_dir)),
        index=index_status(settings),
        llm_configured=bool(settings.groq_api_key),
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
