"""Split parsed documents into chunks for embedding.

Two strategies are available so they can be compared in the evaluation:

- "heading" (default): each section becomes one chunk. A section longer than
  chunk_size is split into overlapping windows of whole sentences and lines.
- "window": each document is treated as one stream of sentences and lines and
  split into overlapping windows, ignoring section boundaries.

Token counts use a simple regex tokenizer (words, numbers, and punctuation
marks each count as one token). It needs no model download, gives the same
answer on every machine, and slightly undercounts the embedding model's own
WordPiece tokens, so the default chunk_size of 350 leaves headroom under the
model's 512-token limit.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.parsing import ParsedDocument, Section

TOKEN = re.compile(r"\w+|[^\w\s]")
SENTENCE_END = re.compile(r"(?<=[.!?;])\s+(?=[A-Z0-9(\"'-])")
STRATEGIES = ("heading", "window")


def count_tokens(text: str) -> int:
    return len(TOKEN.findall(text))


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    version: str
    section: str
    anchor: str
    source_file: str
    text: str
    token_count: int

    @property
    def embedding_text(self) -> str:
        """Text sent to the embedding model: a short context header plus the chunk."""
        return f"{self.title} ({self.doc_id}), {self.section}\n{self.text}"

    def metadata(self) -> dict[str, str | int]:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "version": self.version,
            "section": self.section,
            "anchor": self.anchor,
            "source_file": self.source_file,
            "token_count": self.token_count,
        }


@dataclass(frozen=True)
class _Unit:
    """A sentence or line, with the section it came from."""

    section: Section
    text: str
    tokens: int
    new_line: bool


def _split_long(text: str, limit: int) -> list[str]:
    """Hard-split a single sentence that is longer than the chunk size."""
    words, pieces, current = text.split(), [], []
    for word in words:
        if current and count_tokens(" ".join([*current, word])) > limit:
            pieces.append(" ".join(current))
            current = []
        current.append(word)
    if current:
        pieces.append(" ".join(current))
    return pieces


def _units(section: Section, limit: int) -> list[_Unit]:
    units = []
    for line in section.text.splitlines():
        sentences = [line] if count_tokens(line) <= limit else SENTENCE_END.split(line)
        first = True
        for sentence in sentences:
            for piece in (
                [sentence] if count_tokens(sentence) <= limit else _split_long(sentence, limit)
            ):
                units.append(_Unit(section, piece, count_tokens(piece), new_line=first))
                first = False
    return units


def _windows(units: list[_Unit], size: int, overlap: int) -> list[list[_Unit]]:
    """Greedy windows of whole units, each at most `size` tokens, overlapping by up to `overlap`."""
    windows: list[list[_Unit]] = []
    current: list[_Unit] = []
    current_tokens = 0
    for unit in units:
        if current and current_tokens + unit.tokens > size:
            windows.append(current)
            carry: list[_Unit] = []
            carry_tokens = 0
            for previous in reversed(current):
                if carry_tokens + previous.tokens > overlap:
                    break
                carry.insert(0, previous)
                carry_tokens += previous.tokens
            while carry and carry_tokens + unit.tokens > size:
                carry_tokens -= carry.pop(0).tokens
            current, current_tokens = carry, carry_tokens
        current.append(unit)
        current_tokens += unit.tokens
    if current:
        windows.append(current)
    return windows


def _join(units: list[_Unit]) -> str:
    parts = []
    for index, unit in enumerate(units):
        if index:
            parts.append("\n" if unit.new_line else " ")
        parts.append(unit.text)
    return "".join(parts)


def chunk_document(document: ParsedDocument, strategy: str, size: int, overlap: int) -> list[Chunk]:
    if strategy not in STRATEGIES:
        raise ValueError(f"Unknown chunk strategy {strategy!r}; use one of {STRATEGIES}")
    if not 0 <= overlap < size:
        raise ValueError("chunk_overlap must be at least 0 and smaller than chunk_size")

    groups: list[list[_Unit]] = []
    if strategy == "heading":
        for section in document.sections:
            groups.extend(_windows(_units(section, size), size, overlap))
    else:
        all_units = [unit for section in document.sections for unit in _units(section, size)]
        groups = _windows(all_units, size, overlap)

    chunks = []
    for index, group in enumerate(groups, start=1):
        text = _join(group)
        section = group[0].section
        chunks.append(
            Chunk(
                chunk_id=f"{document.doc_id}-{index:03d}",
                doc_id=document.doc_id,
                title=document.title,
                version=document.metadata.get("version", ""),
                section=section.heading,
                anchor=section.anchor,
                source_file=document.source_file,
                text=text,
                token_count=count_tokens(text),
            )
        )
    return chunks


def chunk_corpus(
    documents: list[ParsedDocument], strategy: str, size: int, overlap: int
) -> list[Chunk]:
    return [
        chunk
        for document in documents
        for chunk in chunk_document(document, strategy, size, overlap)
    ]
