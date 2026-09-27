"""Top-k retrieval over the index: vector search, optionally fused with BM25.

In "hybrid" mode (the default) the vector ranking and the BM25 ranking are
combined with reciprocal rank fusion (RRF): each chunk scores
1 / (60 + rank) in every list it appears in, and the sums are sorted. RRF
needs no score calibration between the two methods, which suits BM25 scores
and cosine similarities that live on different scales.

The best vector similarity is also returned so the caller can refuse
questions that nothing in the corpus matches (the relevance gate).

Questions about changes ("what changed", "updated", "before the latest
change") match a policy's topic better than its Revision History section,
which lists changes in terse version notes. For those questions the Revision
History chunk of the top-ranked document is added as one extra excerpt when
it is not already in the results.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from app.config import Settings
from app.embeddings import Embedder, get_embedder
from app.index_manifest import read_manifest
from app.lexical import BM25
from app.vector_store import VectorStore

RRF_K = 60
MODES = ("hybrid", "vector")
CHANGE_QUESTION = re.compile(
    r"\b(chang(?:e|ed|es|ing)|updat(?:e|ed|es|ing)|revis(?:ed|ion|ions)|amend(?:ed|ment)?"
    r"|what'?s new|new in|latest version|previous(?:ly)?|earlier|before the|used to|history)\b",
    re.IGNORECASE,
)


class IndexNotReadyError(RuntimeError):
    pass


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    text: str
    metadata: dict
    vector_score: float  # cosine similarity with the question
    lexical_score: float  # BM25 score (0 when the chunk shares no keywords)
    fused_score: float  # RRF score in hybrid mode; equals vector_score in vector mode
    added_for: str = ""  # set when a retrieval rule added the chunk, e.g. "change question"


@dataclass(frozen=True)
class Retrieval:
    chunks: list[RetrievedChunk]
    best_vector_score: float


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
        if settings.retrieval_mode not in MODES:
            raise ValueError(f"RETRIEVAL_MODE must be one of {MODES}")

        chunks_path = settings.chroma_dir / "chunks.jsonl"
        if not chunks_path.is_file():
            raise IndexNotReadyError("chunks.jsonl is missing. Rebuild with: python -m app.ingest")
        with chunks_path.open(encoding="utf-8") as handle:
            records = [json.loads(line) for line in handle]

        self._settings = settings
        self._embedder = embedder
        self._store = VectorStore(settings.chroma_dir, settings.collection_name)
        self._chunk_ids = [record["chunk_id"] for record in records]
        self._bm25 = BM25([f"{r['title']} {r['section']} {r['text']}" for r in records])
        self._revision_history = {
            record["doc_id"]: record["chunk_id"]
            for record in records
            if "Revision History" in record["section"]
        }

    def search(self, question: str, k: int | None = None) -> Retrieval:
        k = k or self._settings.top_k
        vector_results = self._store.search(
            self._embedder.embed_query(question), len(self._chunk_ids)
        )
        by_id = {result.chunk_id: result for result in vector_results}
        best_vector_score = vector_results[0].score if vector_results else 0.0

        lexical = {
            self._chunk_ids[index]: score
            for index, score in self._bm25.top(question, len(self._chunk_ids))
        }

        if self._settings.retrieval_mode == "vector":
            ranked = [(result.chunk_id, result.score) for result in vector_results[:k]]
        else:
            pool = self._settings.candidate_pool
            fused: dict[str, float] = {}
            for rank, result in enumerate(vector_results[:pool], start=1):
                fused[result.chunk_id] = fused.get(result.chunk_id, 0.0) + 1 / (RRF_K + rank)
            for rank, chunk_id in enumerate(list(lexical)[:pool], start=1):
                fused[chunk_id] = fused.get(chunk_id, 0.0) + 1 / (RRF_K + rank)
            ranked = sorted(fused.items(), key=lambda item: (-item[1], item[0]))[:k]

        added: dict[str, str] = {}
        if ranked and CHANGE_QUESTION.search(question):
            top_doc = by_id[ranked[0][0]].metadata["doc_id"]
            history_id = self._revision_history.get(top_doc)
            if history_id and history_id not in {chunk_id for chunk_id, _ in ranked}:
                ranked.append((history_id, 0.0))
                added[history_id] = "change question"

        chunks = [
            RetrievedChunk(
                chunk_id=chunk_id,
                text=by_id[chunk_id].text,
                metadata=by_id[chunk_id].metadata,
                vector_score=by_id[chunk_id].score,
                lexical_score=round(lexical.get(chunk_id, 0.0), 4),
                fused_score=round(score, 6),
                added_for=added.get(chunk_id, ""),
            )
            for chunk_id, score in ranked
        ]
        return Retrieval(chunks=chunks, best_vector_score=best_vector_score)
