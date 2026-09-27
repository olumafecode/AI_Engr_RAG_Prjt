from dataclasses import replace

import pytest

from app import create_app
from app.config import Settings
from app.embeddings import HashEmbedder
from app.ingest import build_index


class FakeChatModel:
    """Stands in for the LLM: returns scripted replies and records every call."""

    name = "fake-llm"

    def __init__(self, *replies: str) -> None:
        self.replies = list(replies)
        self.calls: list[tuple[str, str]] = []

    def complete(self, system: str, user: str) -> str:
        self.calls.append((system, user))
        return self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]


@pytest.fixture()
def settings() -> Settings:
    return Settings.from_env()


@pytest.fixture(scope="session")
def hash_settings(tmp_path_factory) -> Settings:
    """Settings pointing at an index built once with the offline HashEmbedder."""
    settings = replace(
        Settings.from_env(),
        chroma_dir=tmp_path_factory.mktemp("chroma"),
        embedding_model="hash",
        groq_api_key="",
        retrieval_mode="hybrid",
        top_k=5,
    )
    build_index(settings, embedder=HashEmbedder())
    return settings


@pytest.fixture()
def client(settings):
    app = create_app(settings)
    app.config["TESTING"] = True
    return app.test_client()
