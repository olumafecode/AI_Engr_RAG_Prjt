"""Index build and retrieval checks using the offline HashEmbedder (no model download)."""

from dataclasses import replace

import pytest

from app.embeddings import HashEmbedder
from app.index_manifest import index_status
from app.ingest import build_index
from app.retrieval import IndexNotReadyError, Retriever


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    from app.config import Settings

    settings = replace(
        Settings.from_env(),
        chroma_dir=tmp_path_factory.mktemp("chroma"),
        embedding_model="hash",
    )
    manifest, chunks = build_index(settings, embedder=HashEmbedder())
    return settings, manifest, chunks


def test_every_chunk_is_stored(built):
    settings, manifest, chunks = built
    assert manifest["chunks"] == len(chunks)
    assert (settings.chroma_dir / "chunks.jsonl").is_file()
    status = index_status(settings)
    assert status["built"] and status["up_to_date"]
    assert status["chunks"] == len(chunks)


def test_retrieval_returns_ranked_results_with_metadata(built):
    settings, _, _ = built
    results = Retriever(settings).search("minimum password length standard accounts", k=5)
    assert len(results) == 5
    assert results[0].score >= results[-1].score
    assert any(result.metadata["doc_id"] == "VB-POL-002" for result in results)


def test_retriever_refuses_a_missing_index(tmp_path):
    from app.config import Settings

    settings = replace(Settings.from_env(), chroma_dir=tmp_path, embedding_model="hash")
    with pytest.raises(IndexNotReadyError):
        Retriever(settings)


def test_retriever_refuses_an_index_built_with_another_model(built):
    settings, _, _ = built
    other = replace(settings, embedding_model="BAAI/bge-small-en-v1.5")

    class FakeEmbedder(HashEmbedder):
        name = "BAAI/bge-small-en-v1.5"

    with pytest.raises(IndexNotReadyError):
        Retriever(other, embedder=FakeEmbedder())
