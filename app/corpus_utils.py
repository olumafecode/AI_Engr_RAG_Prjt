"""Helpers for locating and reading documents in the policy corpus.

Stage 2 builds the full parser, cleaner, and chunker on top of these functions.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader

SUPPORTED_SUFFIXES = {".md", ".txt", ".html", ".pdf"}
FILENAME_PATTERN = re.compile(r"^(VB-(?:ORG|POL)-\d{3})_[a-z0-9_]+$")


def list_documents(corpus_dir: Path) -> list[Path]:
    """Return the corpus files in a stable, sorted order."""
    if not corpus_dir.is_dir():
        return []
    return sorted(
        path
        for path in corpus_dir.iterdir()
        if path.is_file() and path.suffix in SUPPORTED_SUFFIXES
    )


def doc_id_from_filename(path: Path) -> str | None:
    """Return the document ID encoded in a file name, e.g. VB-POL-006."""
    match = FILENAME_PATTERN.match(path.stem)
    return match.group(1) if match else None


def read_text(path: Path) -> str:
    """Return the plain text of a corpus file, whatever its format."""
    if path.suffix == ".pdf":
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    raw = path.read_text(encoding="utf-8")
    if path.suffix == ".html":
        return BeautifulSoup(raw, "html.parser").get_text("\n")
    return raw


def word_count(text: str) -> int:
    return len(text.split())


def corpus_fingerprint(corpus_dir: Path) -> str:
    """SHA-256 over every corpus file's name and bytes, in sorted order."""
    digest = hashlib.sha256()
    for path in list_documents(corpus_dir):
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()
