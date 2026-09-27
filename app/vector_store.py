"""A thin wrapper around a persistent Chroma collection that uses cosine distance."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.chunking import Chunk


@dataclass(frozen=True)
class SearchResult:
    chunk_id: str
    text: str
    score: float  # cosine similarity: 1.0 is identical, 0.0 is unrelated
    metadata: dict


class VectorStore:
    def __init__(self, persist_dir: Path, collection_name: str) -> None:
        persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=str(persist_dir), settings=ChromaSettings(anonymized_telemetry=False)
        )
        self._name = collection_name

    def _collection(self):
        return self._client.get_collection(self._name, embedding_function=None)

    def rebuild(self, chunks: list[Chunk], embeddings: list[list[float]], batch: int = 100) -> None:
        """Replace the collection with the given chunks and their embeddings."""
        if self._name in {collection.name for collection in self._client.list_collections()}:
            self._client.delete_collection(self._name)
        collection = self._client.create_collection(
            self._name, configuration={"hnsw": {"space": "cosine"}}, embedding_function=None
        )
        for start in range(0, len(chunks), batch):
            part = chunks[start : start + batch]
            collection.add(
                ids=[chunk.chunk_id for chunk in part],
                documents=[chunk.text for chunk in part],
                embeddings=embeddings[start : start + batch],
                metadatas=[chunk.metadata() for chunk in part],
            )

    def count(self) -> int:
        return self._collection().count()

    def search(self, embedding: list[float], k: int) -> list[SearchResult]:
        result = self._collection().query(
            query_embeddings=[embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )
        return [
            SearchResult(chunk_id, text, round(1.0 - distance, 4), metadata)
            for chunk_id, text, metadata, distance in zip(
                result["ids"][0],
                result["documents"][0],
                result["metadatas"][0],
                result["distances"][0],
                strict=True,
            )
        ]
