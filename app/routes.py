"""HTTP routes: the chat page, the chat API, and the health check."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, render_template, request

from app.corpus_utils import list_documents

bp = Blueprint("main", __name__)


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

    # Stage 3 replaces this response with retrieval, generation, and citations.
    message = "The assistant cannot answer yet. Retrieval and generation arrive in Stage 3."
    return jsonify(error=message), 501
