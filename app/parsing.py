"""Parse and clean corpus documents in every supported format.

Each file becomes a ParsedDocument: its metadata plus an ordered list of
sections. A section has a heading path (for example "6. Key Control
Requirements > 6.5 Mandatory block leave"), an anchor used to build citation
links, and cleaned plain text.

Format notes:
- Markdown: metadata from YAML front matter; sections from ## and ### headings.
- Plain text: metadata from the "Key: Value" header block; sections from
  numbered upper-case headings such as "4. PASSWORD REQUIREMENTS".
- HTML: metadata from <meta> tags; sections from <section id="..."> blocks.
- PDF: metadata from the header table; tables are extracted row by row with
  pdfplumber so their structure survives; running footers are removed.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import pdfplumber
from bs4 import BeautifulSoup

from app.corpus_utils import doc_id_from_filename, list_documents

METADATA_LABELS = {
    "doc_id": "Document ID",
    "title": "Title",
    "version": "Version",
    "effective_date": "Effective date",
    "owner": "Owner",
    "approved_by": "Approved by",
    "review_cycle": "Review cycle",
    "classification": "Classification",
}
SMALL_WORDS = {"a", "an", "and", "as", "at", "by", "for", "in", "of", "on", "or", "the", "to"}

MD_HEADING = re.compile(r"^(#{1,6})\s+(.+)$")
MD_TABLE_SEPARATOR = re.compile(r"^\|[\s\-:|]+\|$")
TXT_SECTION = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 ,&/'()\-]+)$")
SUBHEADING = re.compile(r"^\d+\.\d+\s+[A-Z][^.]{0,70}$")
PDF_HEADING = re.compile(r"^(?:\d+\.|\d+\.\d+)\s+[A-Z][^.]{0,70}$")
PDF_FOOTER = re.compile(r"^VB-[A-Z]+-\d{3}\s.*\sPage \d+$")
PDF_GLYPH = re.compile(r"\(cid:\d+\)")


@dataclass(frozen=True)
class Section:
    heading: str
    anchor: str
    text: str


@dataclass(frozen=True)
class ParsedDocument:
    doc_id: str
    title: str
    source_file: str
    file_format: str
    metadata: dict[str, str]
    sections: list[Section]


# ---------------------------------------------------------------- helpers


def slugify(text: str) -> str:
    """GitHub-style heading anchor: '6.5 Mandatory block leave' -> '65-mandatory-block-leave'."""
    text = re.sub(r"[^\w\- ]", "", text.lower()).strip()
    return re.sub(r"\s+", "-", text)


def title_case(text: str) -> str:
    """'JOINERS, MOVERS, AND LEAVERS' -> 'Joiners, Movers, and Leavers'."""
    words = text.lower().split()
    return " ".join(
        word if index > 0 and word in SMALL_WORDS else word[:1].upper() + word[1:]
        for index, word in enumerate(words)
    )


def clean_text(text: str) -> str:
    """Normalize Unicode and whitespace, and drop empty lines."""
    text = unicodedata.normalize("NFKC", text)
    lines = []
    for line in text.splitlines():
        line = re.sub(r"[ \t]+", " ", line).strip()
        line = re.sub(r"\s+([,.;:)])", r"\1", line)
        if line:
            lines.append(line)
    return "\n".join(lines)


def _md_inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"\1", text)
    return text.replace("`", "")


def _table_row(cells: list[str]) -> str:
    return " | ".join(clean_text(cell).replace("\n", " ") for cell in cells)


class _SectionBuilder:
    """Collects lines under the current heading and emits non-empty sections."""

    def __init__(self) -> None:
        self.sections: list[Section] = []
        self._heading = ""
        self._anchor = ""
        self._lines: list[str] = []

    def start(self, heading: str, anchor: str) -> None:
        self.flush()
        self._heading, self._anchor = heading, anchor

    def add(self, line: str) -> None:
        self._lines.append(line)

    def flush(self) -> None:
        text = clean_text("\n".join(self._lines))
        if self._heading and text:
            self.sections.append(Section(self._heading, self._anchor, text))
        self._lines = []


# ---------------------------------------------------------------- Markdown


def _split_front_matter(raw: str) -> tuple[dict[str, str], str]:
    if not raw.startswith("---"):
        return {}, raw
    end = raw.find("\n---", 3)
    metadata = {}
    for line in raw[3:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"')
    return metadata, raw[end + 4 :]


def parse_markdown(path: Path) -> tuple[dict[str, str], list[Section]]:
    metadata, body = _split_front_matter(path.read_text(encoding="utf-8"))
    builder = _SectionBuilder()
    parent = ""
    for line in body.splitlines():
        stripped = line.strip()
        heading = MD_HEADING.match(stripped)
        if heading:
            level, text = len(heading.group(1)), _md_inline(heading.group(2)).strip()
            if level == 1:
                metadata.setdefault("title", text)
                builder.start("Introduction", "")
            elif level == 2:
                parent = text
                builder.start(text, slugify(text))
            else:
                builder.start(f"{parent} > {text}" if parent else text, slugify(text))
        elif MD_TABLE_SEPARATOR.match(stripped):
            continue
        elif stripped.startswith("|"):
            builder.add(_table_row(_md_inline(stripped).strip("|").split("|")))
        else:
            builder.add(_md_inline(line))
    builder.flush()
    return metadata, builder.sections


# ---------------------------------------------------------------- Plain text


def parse_text(path: Path) -> tuple[dict[str, str], list[Section]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    body_start = next(i for i, line in enumerate(lines) if TXT_SECTION.match(line.strip()))

    metadata: dict[str, str] = {}
    title_lines = []
    for line in lines[:body_start]:
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip().lower().replace(" ", "_")
            metadata["doc_id" if key == "document_id" else key] = value.strip()
        elif line.strip():
            title_lines.append(line.strip())
    if title_lines:
        metadata["title"] = title_case(title_lines[-1])

    builder = _SectionBuilder()
    parent = ""
    for line in lines[body_start:]:
        stripped = line.strip()
        section = TXT_SECTION.match(stripped)
        if section:
            parent = f"{section.group(1)}. {title_case(section.group(2))}"
            builder.start(parent, slugify(parent))
        elif SUBHEADING.match(stripped) and len(stripped) <= 60:
            builder.start(f"{parent} > {stripped}", slugify(stripped))
        else:
            builder.add(stripped)
    builder.flush()
    return metadata, builder.sections


# ---------------------------------------------------------------- HTML


def parse_html(path: Path) -> tuple[dict[str, str], list[Section]]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    metadata = {
        tag["name"]: tag.get("content", "") for tag in soup.find_all("meta") if tag.get("name")
    }
    if soup.h1:
        metadata.setdefault("title", soup.h1.get_text(" ", strip=True))

    builder = _SectionBuilder()
    for block in soup.find_all("section"):
        anchor = block.get("id", "")
        parent = ""
        for element in block.find_all(["h2", "h3", "p", "li", "tr"]):
            text = element.get_text(" ", strip=True)
            if element.name == "h2":
                parent = text
                builder.start(text, anchor)
            elif element.name == "h3":
                builder.start(f"{parent} > {text}", anchor)
            elif element.name == "tr":
                cells = [cell.get_text(" ", strip=True) for cell in element.find_all(["th", "td"])]
                builder.add(_table_row(cells))
            elif element.name == "li":
                siblings = element.parent.find_all("li", recursive=False)
                if element.parent.name == "ol":
                    builder.add(f"{siblings.index(element) + 1}. {text}")
                else:
                    builder.add(f"- {text}")
            else:
                builder.add(text)
    builder.flush()
    return metadata, builder.sections


# ---------------------------------------------------------------- PDF


def _pdf_page_blocks(page) -> list[tuple[str, str]]:
    """Return ("text", line) and ("row", cells) items for one page, top to bottom."""
    blocks: list[tuple[str, str]] = []
    top = 0.0
    for table in sorted(page.find_tables(), key=lambda t: t.bbox[1]):
        if table.bbox[1] - top > 1:
            text = page.crop((0, top, page.width, table.bbox[1])).extract_text() or ""
            blocks.extend(("text", line) for line in text.splitlines())
        blocks.extend(("row", _table_row([cell or "" for cell in row])) for row in table.extract())
        top = table.bbox[3]
    if page.height - top > 1:
        text = page.crop((0, top, page.width, page.height)).extract_text() or ""
        blocks.extend(("text", line) for line in text.splitlines())
    return blocks


def parse_pdf(path: Path) -> tuple[dict[str, str], list[Section]]:
    metadata: dict[str, str] = {}
    builder = _SectionBuilder()
    parent = ""
    started = False
    paragraph: list[str] = []

    def end_paragraph() -> None:
        if paragraph:
            builder.add(" ".join(paragraph))
            paragraph.clear()

    with pdfplumber.open(path) as pdf:
        metadata["title"] = (pdf.metadata or {}).get("Title", "")
        for page_number, page in enumerate(pdf.pages, start=1):
            for kind, content in _pdf_page_blocks(page):
                line = PDF_GLYPH.sub("-", content).strip()
                if kind == "row" and not started:
                    label, _, value = line.partition(" | ")
                    for key, known in METADATA_LABELS.items():
                        if label == known:
                            metadata[key] = value
                    continue
                if not line or PDF_FOOTER.match(line):
                    continue
                is_heading = kind == "text" and (
                    (PDF_HEADING.match(line) and len(line) <= 80) or line == "Revision History"
                )
                if is_heading:
                    end_paragraph()
                    started = True
                    if re.match(r"^\d+\.\s", line) or line == "Revision History":
                        parent = line
                        heading = line
                    else:
                        heading = f"{parent} > {line}"
                    builder.start(heading, f"page={page_number}")
                elif not started:
                    continue
                elif kind == "row":
                    end_paragraph()
                    builder.add(line)
                elif line.startswith("- "):
                    end_paragraph()
                    paragraph.append(line)
                else:
                    paragraph.append(line)
            end_paragraph()
    builder.flush()
    return metadata, builder.sections


# ---------------------------------------------------------------- entry points

PARSERS = {
    ".md": parse_markdown,
    ".txt": parse_text,
    ".html": parse_html,
    ".pdf": parse_pdf,
}


def _information_section(metadata: dict[str, str]) -> Section:
    lines = [
        f"{label}: {metadata[key]}" for key, label in METADATA_LABELS.items() if metadata.get(key)
    ]
    return Section("Document information", "", "\n".join(lines))


def parse_document(path: Path) -> ParsedDocument:
    metadata, sections = PARSERS[path.suffix](path)
    expected_id = doc_id_from_filename(path)
    if metadata.get("doc_id") != expected_id:
        raise ValueError(f"{path.name}: metadata doc_id {metadata.get('doc_id')!r} != file name")
    return ParsedDocument(
        doc_id=expected_id,
        title=metadata.get("title", ""),
        source_file=path.name,
        file_format=path.suffix.lstrip("."),
        metadata=metadata,
        sections=[_information_section(metadata), *sections],
    )


def parse_corpus(corpus_dir: Path) -> list[ParsedDocument]:
    """Parse every corpus document in a stable, sorted order."""
    return [parse_document(path) for path in list_documents(corpus_dir)]
