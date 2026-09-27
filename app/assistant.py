"""The question-answering pipeline behind POST /chat.

1. Retrieve the top-k chunks (hybrid vector + BM25 search).
2. Relevance gate: if the best vector similarity is below RELEVANCE_THRESHOLD,
   refuse without calling the LLM.
3. Send the labeled excerpts to the LLM with the rules in app.generation.
4. Check citations against the retrieved excerpts. If the model gave an answer
   with no valid citation, ask once more; if it still has none, refuse.
5. Return the answer, numbered citations with snippets and links, and timings.
"""

from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass

from app.config import Settings
from app.generation import (
    REFUSAL,
    RETRY_NOTE,
    ChatModel,
    GroqChatModel,
    LLMNotConfiguredError,
    build_user_prompt,
    process_answer,
    system_prompt,
)
from app.retrieval import RetrievedChunk, Retriever

logger = logging.getLogger(__name__)

SNIPPET_CHARS = 240


@dataclass(frozen=True)
class Citation:
    number: int
    doc_id: str
    title: str
    section: str
    snippet: str
    url: str
    chunk_id: str


@dataclass(frozen=True)
class Answer:
    question: str
    answer: str
    refused: bool
    refusal_reason: str | None  # no_relevant_context, model_refusal, or no_citations
    citations: list[Citation]
    retrieved: list[dict]
    best_vector_score: float
    model: str
    latency_ms: dict

    def to_dict(self) -> dict:
        return asdict(self)


def snippet(text: str, limit: int = SNIPPET_CHARS) -> str:
    flat = " ".join(text.split())
    if len(flat) <= limit:
        return flat
    return flat[:limit].rsplit(" ", 1)[0] + "..."


def source_url(metadata: dict) -> str:
    anchor = metadata.get("anchor", "")
    return f"/docs/{metadata['doc_id']}" + (f"#{anchor}" if anchor else "")


class PolicyAssistant:
    def __init__(
        self,
        settings: Settings,
        retriever: Retriever | None = None,
        chat_model: ChatModel | None = None,
    ) -> None:
        self._settings = settings
        self._retriever = retriever or Retriever(settings)
        if chat_model is None:
            try:
                chat_model = GroqChatModel(settings)
            except LLMNotConfiguredError:
                chat_model = None  # the relevance gate still works; answers need a key
        self._chat = chat_model

    def warm_up(self) -> None:
        """Run one retrieval so the model and index are loaded before the first user."""
        self._retriever.search("warm-up", 1)

    def answer(self, question: str) -> Answer:
        settings = self._settings
        started = time.perf_counter()
        retrieval = self._retriever.search(question, settings.top_k)
        retrieved_at = time.perf_counter()
        chunks = retrieval.chunks
        retrieved = [
            {
                "chunk_id": chunk.chunk_id,
                "doc_id": chunk.metadata["doc_id"],
                "section": chunk.metadata["section"],
                "vector_score": chunk.vector_score,
                "lexical_score": chunk.lexical_score,
                "added_for": chunk.added_for,
            }
            for chunk in chunks
        ]

        def finish(text: str, reason: str | None, cited: list[RetrievedChunk]) -> Answer:
            done = time.perf_counter()
            citations = [
                Citation(
                    number=number,
                    doc_id=chunk.metadata["doc_id"],
                    title=chunk.metadata["title"],
                    section=chunk.metadata["section"],
                    snippet=snippet(chunk.text),
                    url=source_url(chunk.metadata),
                    chunk_id=chunk.chunk_id,
                )
                for number, chunk in enumerate(cited, start=1)
            ]
            answer = Answer(
                question=question,
                answer=text,
                refused=reason is not None,
                refusal_reason=reason,
                citations=citations,
                retrieved=retrieved,
                best_vector_score=retrieval.best_vector_score,
                model=self._chat.name if self._chat else "none",
                latency_ms={
                    "retrieval": round((retrieved_at - started) * 1000),
                    "generation": round((done - retrieved_at) * 1000),
                    "total": round((done - started) * 1000),
                },
            )
            logger.info(
                "answered refused=%s reason=%s citations=%d best_score=%.3f total_ms=%d",
                answer.refused,
                reason,
                len(citations),
                retrieval.best_vector_score,
                answer.latency_ms["total"],
            )
            return answer

        if not chunks or retrieval.best_vector_score < settings.relevance_threshold:
            return finish(REFUSAL, "no_relevant_context", [])

        if self._chat is None:
            raise LLMNotConfiguredError(
                "The language model is not configured. Add GROQ_API_KEY to the environment."
            )

        system = system_prompt(settings.max_answer_words)
        user = build_user_prompt(question, [(chunk.metadata, chunk.text) for chunk in chunks])
        result = process_answer(
            self._chat.complete(system, user), len(chunks), settings.max_answer_words
        )
        if not result.refused and not result.cited:
            result = process_answer(
                self._chat.complete(system, user + RETRY_NOTE),
                len(chunks),
                settings.max_answer_words,
            )
            if not result.refused and not result.cited:
                return finish(REFUSAL, "no_citations", [])

        if result.refused:
            return finish(REFUSAL, "model_refusal", [])
        return finish(result.text, None, [chunks[number - 1] for number in result.cited])
