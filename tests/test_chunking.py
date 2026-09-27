"""Chunking checks: size limits, overlap, stable IDs, and both strategies."""

import pytest

from app.chunking import chunk_corpus, chunk_document, count_tokens
from app.parsing import Section


@pytest.fixture(scope="module")
def documents():
    from app.config import Settings
    from app.parsing import parse_corpus

    return parse_corpus(Settings.from_env().corpus_dir)


@pytest.mark.parametrize("strategy,size,overlap", [("heading", 350, 50), ("window", 200, 30)])
def test_chunks_respect_the_size_limit(documents, strategy, size, overlap):
    chunks = chunk_corpus(documents, strategy, size, overlap)
    assert chunks
    assert all(0 < chunk.token_count <= size for chunk in chunks)


def test_chunk_ids_are_unique_and_stable(documents):
    first = chunk_corpus(documents, "heading", 350, 50)
    second = chunk_corpus(documents, "heading", 350, 50)
    ids = [chunk.chunk_id for chunk in first]
    assert len(ids) == len(set(ids))
    assert first == second


def test_every_chunk_carries_citation_metadata(documents):
    for chunk in chunk_corpus(documents, "heading", 350, 50):
        metadata = chunk.metadata()
        assert metadata["doc_id"] and metadata["title"] and metadata["section"]
        assert chunk.embedding_text.startswith(f"{chunk.title} ({chunk.doc_id})")


def test_long_sections_are_windowed_with_overlap(documents):
    document = documents[0]
    long_section = Section(
        "Long section", "long", "\n".join(f"Rule {n} applies here." for n in range(200))
    )
    document = type(document)(
        document.doc_id,
        document.title,
        document.source_file,
        document.file_format,
        document.metadata,
        [long_section],
    )
    chunks = chunk_document(document, "heading", 100, 20)
    assert len(chunks) > 1
    for previous, current in zip(chunks, chunks[1:], strict=False):
        assert previous.text.splitlines()[-1] in current.text  # overlap carries the last line


def test_token_counter_counts_words_numbers_and_punctuation():
    assert count_tokens("USD 5,000 per day.") == 7


def test_invalid_settings_are_rejected(documents):
    with pytest.raises(ValueError):
        chunk_document(documents[0], "sentences", 350, 50)
    with pytest.raises(ValueError):
        chunk_document(documents[0], "heading", 100, 100)
