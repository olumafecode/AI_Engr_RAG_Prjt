"""Checks that the policy corpus is complete, well formed, and within the brief's size limits."""

from app.corpus_utils import (
    FILENAME_PATTERN,
    SUPPORTED_SUFFIXES,
    doc_id_from_filename,
    list_documents,
    read_text,
    word_count,
)

EXPECTED_IDS = {"VB-ORG-001"} | {f"VB-POL-{number:03d}" for number in range(1, 14)}
WORDS_PER_PAGE = 500


def test_every_expected_document_is_present_exactly_once(settings):
    ids = [doc_id_from_filename(path) for path in list_documents(settings.corpus_dir)]
    assert sorted(ids) == sorted(EXPECTED_IDS)


def test_corpus_folder_holds_only_policy_documents(settings):
    for path in settings.corpus_dir.iterdir():
        if path.name.startswith("."):
            continue
        assert path.suffix in SUPPORTED_SUFFIXES, f"Unexpected file type: {path.name}"
        assert FILENAME_PATTERN.match(path.stem), f"File name breaks the naming rule: {path.name}"


def test_corpus_mixes_all_required_formats(settings):
    suffixes = {path.suffix for path in list_documents(settings.corpus_dir)}
    assert suffixes == {".md", ".txt", ".html", ".pdf"}


def test_each_document_declares_its_own_id(settings):
    for path in list_documents(settings.corpus_dir):
        doc_id = doc_id_from_filename(path)
        assert doc_id in read_text(path), f"{path.name} does not mention {doc_id}"


def test_corpus_size_is_within_30_to_120_pages(settings):
    total = sum(word_count(read_text(path)) for path in list_documents(settings.corpus_dir))
    assert 30 * WORDS_PER_PAGE <= total <= 120 * WORDS_PER_PAGE
