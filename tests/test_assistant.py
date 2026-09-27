"""End-to-end pipeline checks with the offline index and a scripted LLM."""

from dataclasses import replace

import pytest

from app.assistant import PolicyAssistant
from app.generation import REFUSAL, LLMNotConfiguredError
from tests.conftest import FakeChatModel

QUESTION = "What is the minimum password length for a standard account?"


def make(hash_settings, *replies, threshold=0.0):
    settings = replace(hash_settings, relevance_threshold=threshold)
    model = FakeChatModel(*replies) if replies else None
    return PolicyAssistant(settings, chat_model=model), model


def test_answer_carries_numbered_citations_that_match_retrieved_chunks(hash_settings):
    assistant, model = make(
        hash_settings, "At least 14 characters [S2]. Changed every 180 days [S2][S1]."
    )
    answer = assistant.answer(QUESTION)
    assert not answer.refused
    assert answer.answer == "At least 14 characters [1]. Changed every 180 days [1][2]."
    retrieved_ids = [item["chunk_id"] for item in answer.retrieved]
    assert [c.chunk_id for c in answer.citations] == [retrieved_ids[1], retrieved_ids[0]]
    assert all(c.url.startswith(f"/docs/{c.doc_id}") and c.snippet for c in answer.citations)
    assert set(answer.latency_ms) == {"retrieval", "generation", "total"}
    system, user = model.calls[0]
    assert "[S1]" in user and QUESTION in user and "Use only the excerpts" in system


def test_uncited_answer_is_retried_once_then_refused(hash_settings):
    assistant, model = make(hash_settings, "Fourteen characters.", "Still no citation.")
    answer = assistant.answer(QUESTION)
    assert answer.refused and answer.refusal_reason == "no_citations"
    assert len(model.calls) == 2


def test_retry_can_recover_a_cited_answer(hash_settings):
    assistant, model = make(hash_settings, "Fourteen characters.", "Fourteen characters [S1].")
    answer = assistant.answer(QUESTION)
    assert not answer.refused and len(answer.citations) == 1 and len(model.calls) == 2


def test_model_refusal_is_reported(hash_settings):
    assistant, _ = make(hash_settings, REFUSAL)
    answer = assistant.answer("What is Veridane Bank's share price?")
    assert answer.refused and answer.refusal_reason == "model_refusal" and not answer.citations


def test_relevance_gate_refuses_without_calling_the_llm(hash_settings):
    assistant, model = make(hash_settings, "should not be used", threshold=0.99)
    answer = assistant.answer("What is the capital of France?")
    assert answer.refused and answer.refusal_reason == "no_relevant_context"
    assert model.calls == []


def test_gate_works_without_a_key_but_answers_need_one(hash_settings):
    gated, _ = make(hash_settings, threshold=0.99)
    assert gated.answer("Write a poem").refused
    open_gate, _ = make(hash_settings, threshold=0.0)
    with pytest.raises(LLMNotConfiguredError):
        open_gate.answer(QUESTION)
