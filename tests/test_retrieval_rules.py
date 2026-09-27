"""The retrieval rule for questions about policy changes."""

from app.retrieval import CHANGE_QUESTION, Retriever


def test_change_questions_are_recognised():
    assert CHANGE_QUESTION.search("What changed in the latest version of the password policy?")
    assert CHANGE_QUESTION.search("What was the critical patch window before the latest change?")
    assert CHANGE_QUESTION.search("Has the gift limit been updated?")
    assert not CHANGE_QUESTION.search("What is the minimum password length?")


def test_change_question_includes_the_top_documents_revision_history(hash_settings):
    retrieval = Retriever(hash_settings).search(
        "What changed in the latest version of the password policy?", 5
    )
    top_doc = retrieval.chunks[0].metadata["doc_id"]
    assert any(
        chunk.metadata["doc_id"] == top_doc and "Revision History" in chunk.metadata["section"]
        for chunk in retrieval.chunks
    )
    assert len(retrieval.chunks) in (5, 6)


def test_other_questions_get_exactly_k_chunks(hash_settings):
    retrieval = Retriever(hash_settings).search("minimum password length standard accounts", 5)
    assert len(retrieval.chunks) == 5
    assert not any(chunk.added_for for chunk in retrieval.chunks)
