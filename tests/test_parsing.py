"""Parsing and cleaning checks for every corpus format."""

import pytest

from app.parsing import parse_corpus, parse_document, slugify, title_case


@pytest.fixture(scope="module")
def documents():
    from app.config import Settings

    return {doc.doc_id: doc for doc in parse_corpus(Settings.from_env().corpus_dir)}


def _section(document, prefix):
    return next(section for section in document.sections if section.heading.startswith(prefix))


def test_every_document_has_core_metadata(documents):
    assert len(documents) == 14
    for document in documents.values():
        for field in ("doc_id", "title", "version", "effective_date", "owner"):
            assert document.metadata.get(field), f"{document.doc_id} is missing {field}"


def test_every_document_starts_with_an_information_section(documents):
    for document in documents.values():
        first = document.sections[0]
        assert first.heading == "Document information"
        assert f"Document ID: {document.doc_id}" in first.text


def test_markdown_formatting_is_removed(documents):
    text = "\n".join(section.text for section in documents["VB-ORG-001"].sections)
    assert "**" not in text
    assert "|---" not in text
    assert "Retail Banking: current and savings accounts" in text


def test_plain_text_headings_and_subheadings(documents):
    document = documents["VB-POL-002"]
    assert document.title == "Password and Access Control Policy"
    section = _section(document, "4. Password Requirements > 4.1")
    assert section.anchor == "41-minimum-requirements-by-account-type"
    assert "Minimum length: 14 characters" in section.text


def test_html_sections_keep_their_ids_as_anchors(documents):
    section = _section(documents["VB-POL-008"], "6. Cash Management > 6.2")
    assert section.anchor == "cash-management"
    assert "USD 20,000" in section.text


def test_pdf_tables_stay_row_by_row_and_footers_are_removed(documents):
    document = documents["VB-POL-007"]
    tiers = _section(document, "8. Tiered KYC")
    assert "2 | Tier 1 plus an uploaded photo ID" in tiers.text
    assert "USD 2,000 | USD 1,000" in tiers.text
    assert tiers.anchor.startswith("page=")
    all_text = "\n".join(section.text for section in document.sections)
    assert "Page 1" not in all_text
    assert "(cid:" not in all_text


def test_parsing_is_deterministic():
    from app.config import Settings

    settings = Settings.from_env()
    path = sorted(settings.corpus_dir.glob("VB-POL-006*"))[0]
    assert parse_document(path) == parse_document(path)


def test_helpers():
    assert slugify("6.5 Mandatory block leave") == "65-mandatory-block-leave"
    assert title_case("JOINERS, MOVERS, AND LEAVERS") == "Joiners, Movers, and Leavers"
