"""Route tests. The /chat tests inject an assistant backed by the offline index and a fake LLM."""

from dataclasses import replace

import pytest

from app import create_app
from app.assistant import PolicyAssistant
from tests.conftest import FakeChatModel


@pytest.fixture()
def chat_client(hash_settings):
    settings = replace(hash_settings, relevance_threshold=0.0)
    assistant = PolicyAssistant(settings, chat_model=FakeChatModel("Fourteen characters [S1]."))
    app = create_app(settings, assistant=assistant)
    return app.test_client()


def test_health_reports_ok_corpus_index_and_llm(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert body["corpus_documents"] == 14
    assert "built" in body["index"]
    assert isinstance(body["llm_configured"], bool)


def test_index_serves_chat_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Policy Assistant" in response.data


def test_chat_rejects_non_json_body(client):
    assert client.post("/chat", data="hello", content_type="text/plain").status_code == 400


def test_chat_rejects_empty_question(client):
    assert client.post("/chat", json={"question": "   "}).status_code == 400


def test_chat_rejects_overlong_question(client, settings):
    question = "x" * (settings.max_question_chars + 1)
    assert client.post("/chat", json={"question": question}).status_code == 400


def test_chat_returns_answer_with_citations_and_timing(chat_client):
    response = chat_client.post("/chat", json={"question": "Minimum password length?"})
    assert response.status_code == 200
    body = response.get_json()
    assert body["answer"] == "Fourteen characters [1]."
    assert body["refused"] is False
    citation = body["citations"][0]
    assert {"number", "doc_id", "title", "section", "snippet", "url"} <= set(citation)
    assert body["latency_ms"]["total"] >= 0


def test_chat_explains_a_missing_index(tmp_path, settings):
    app = create_app(replace(settings, chroma_dir=tmp_path, embedding_model="hash"))
    response = app.test_client().post("/chat", json={"question": "Minimum password length?"})
    assert response.status_code == 503
    assert "python -m app.ingest" in response.get_json()["error"]


def test_docs_route_renders_text_documents_with_section_anchors(client):
    response = client.get("/docs/VB-POL-002")
    assert response.status_code == 200
    assert b'id="41-minimum-requirements-by-account-type"' in response.data


def test_docs_route_serves_pdf_and_html_sources(client):
    assert client.get("/docs/VB-POL-007").mimetype == "application/pdf"
    assert client.get("/docs/VB-POL-008").mimetype == "text/html"


@pytest.mark.parametrize("doc_id", ["VB-POL-999", "..%2Fapp", "not-a-doc"])
def test_docs_route_rejects_unknown_documents(client, doc_id):
    assert client.get(f"/docs/{doc_id}").status_code == 404


def test_health_reports_readiness_and_memory(client):
    body = client.get("/health").get_json()
    assert body["assistant_ready"] is False
    assert "peak_memory_mb" in body


def test_warm_up_loads_the_assistant_in_the_background(hash_settings):
    from app import create_app
    from app.warmup import start_warm_up

    app = create_app(hash_settings)
    thread = start_warm_up(app)
    assert start_warm_up(app) is None  # a second call does nothing
    thread.join(timeout=30)
    body = app.test_client().get("/health").get_json()
    assert body["assistant_ready"] is True
    assert body["warmup"]["state"] == "ready"


def test_chat_waits_for_a_running_warm_up_then_asks_to_retry(hash_settings, monkeypatch):
    from app import create_app, routes
    from app.warmup import warmup_status

    app = create_app(hash_settings)
    warmup_status(app).state = "running"  # never finishes in this test
    monkeypatch.setattr(routes, "CHAT_WAIT_FOR_WARMUP_SECONDS", 0.1)
    response = app.test_client().post("/chat", json={"question": "Minimum password length?"})
    assert response.status_code == 503
    assert "starting up" in response.get_json()["error"]


def test_health_does_not_start_a_warm_up_by_itself(client):
    body = client.get("/health").get_json()
    assert body["warmup"] == {"state": "off", "seconds": None, "error": None}
    assert body["uptime_seconds"] >= 0
