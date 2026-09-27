"""Index build and retrieval checks using the offline HashEmbedder (no model download)."""

from dataclasses import replace

import pytest

from app.config import Settings
from app.embeddings import HashEmbedder
from app.index_manifest import index_status
from app.retrieval import IndexNotReadyError, Retriever


def test_every_chunk_is_stored(hash_settings):
    status = index_status(hash_settings)
    assert status["built"] and status["up_to_date"]
    lines = (hash_settings.chroma_dir / "chunks.jsonl").read_text(encoding="utf-8").splitlines()
    assert status["chunks"] == len(lines) > 300


@pytest.mark.parametrize("mode", ["hybrid", "vector"])
def test_retrieval_returns_ranked_results_with_metadata(hash_settings, mode):
    settings = replace(hash_settings, retrieval_mode=mode)
    retrieval = Retriever(settings).search("minimum password length standard accounts", k=5)
    chunks = retrieval.chunks
    assert len(chunks) == 5
    assert chunks[0].fused_score >= chunks[-1].fused_score
    assert any(chunk.metadata["doc_id"] == "VB-POL-002" for chunk in chunks)
    assert (
        retrieval.best_vector_score == max(chunk.vector_score for chunk in chunks)
        or mode == "hybrid"
    )


def test_hybrid_search_uses_keywords(hash_settings):
    retrieval = Retriever(hash_settings).search("lost or stolen corporate card", k=5)
    assert any(chunk.lexical_score > 0 for chunk in retrieval.chunks)
    assert any(chunk.metadata["doc_id"] == "VB-POL-012" for chunk in retrieval.chunks)


def test_retriever_refuses_a_missing_index(tmp_path):
    settings = replace(Settings.from_env(), chroma_dir=tmp_path, embedding_model="hash")
    with pytest.raises(IndexNotReadyError):
        Retriever(settings)


def test_retriever_refuses_an_index_built_with_another_model(hash_settings):
    class OtherEmbedder(HashEmbedder):
        name = "BAAI/bge-small-en-v1.5"

    with pytest.raises(IndexNotReadyError):
        Retriever(hash_settings, embedder=OtherEmbedder())
