"""Smoke tests for the web application's routes."""


def test_health_reports_ok_and_counts_corpus(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert body["corpus_documents"] == 14


def test_index_serves_chat_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Policy Assistant" in response.data


def test_chat_rejects_non_json_body(client):
    response = client.post("/chat", data="hello", content_type="text/plain")
    assert response.status_code == 400


def test_chat_rejects_empty_question(client):
    response = client.post("/chat", json={"question": "   "})
    assert response.status_code == 400


def test_chat_rejects_overlong_question(client, settings):
    response = client.post("/chat", json={"question": "x" * (settings.max_question_chars + 1)})
    assert response.status_code == 400


def test_chat_valid_question_reaches_pipeline_placeholder(client):
    # Until Stage 3 wires in retrieval and generation, a valid question returns 501.
    response = client.post("/chat", json={"question": "How long is mandatory block leave?"})
    assert response.status_code == 501
