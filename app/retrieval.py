"""Top-k retrieval over the vector index. Stage 3 adds the relevance gate and generation."""

from __future__ import annotations

from app.config import Settings
from app.embeddings import Embedder, get_embedder
from app.index_manifest import read_manifest
from app.vector_store import SearchResult, VectorStore


class IndexNotReadyError(RuntimeError):
    pass


class Retriever:
    def __init__(self, settings: Settings, embedder: Embedder | None = None) -> None:
        manifest = read_manifest(settings)
        if manifest is None:
            raise IndexNotReadyError("No index found. Build it first with: python -m app.ingest")
        embedder = embedder or get_embedder(settings)
        if manifest["embedding_model"] != embedder.name:
            raise IndexNotReadyError(
                f"The index was built with {manifest['embedding_model']!r} but the current "
                f"embedding model is {embedder.name!r}. Rebuild with: python -m app.ingest"
            )
        self._embedder = embedder
        self._store = VectorStore(settings.chroma_dir, settings.collection_name)
        self._default_k = settings.top_k

    def search(self, question: str, k: int | None = None) -> list[SearchResult]:
        return self._store.search(self._embedder.embed_query(question), k or self._default_k)
