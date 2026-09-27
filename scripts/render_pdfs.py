"""Render the Markdown sources in corpus_src/ to PDF files in corpus/.

Run from the project root:  python -m scripts.render_pdfs

The parser handles only the Markdown features used in the policy sources:
headings (#, ##, ###), paragraphs, bullet and numbered lists, pipe tables,
and **bold** text. Output is byte-for-byte reproducible because ReportLab's
invariant mode removes timestamps and random document IDs.
"""

from __future__ import annotations

import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

rl_config.invariant = 1

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = PROJECT_ROOT / "corpus_src"
OUTPUT_DIR = PROJECT_ROOT / "corpus"

BULLET = re.compile(r"^- (.*)")
NUMBERED = re.compile(r"^\d+\. (.*)")
TABLE_SEPARATOR = re.compile(r"^\|[\s\-:|]+\|$")
DOC_ID = re.compile(r"\| Document ID \| (VB-[A-Z]+-\d{3}) \|")

BASE = getSampleStyleSheet()
STYLES = {
    "title": ParagraphStyle("title", parent=BASE["Title"], fontSize=18, spaceAfter=12),
    "h2": ParagraphStyle("h2", parent=BASE["Heading2"], fontSize=13, spaceBefore=10),
    "h3": ParagraphStyle("h3", parent=BASE["Heading3"], fontSize=11, spaceBefore=6),
    "body": ParagraphStyle("body", parent=BASE["BodyText"], fontSize=10, leading=14),
    "cell": ParagraphStyle("cell", parent=BASE["BodyText"], fontSize=9, leading=12),
}


def inline(text: str) -> str:
    """Escape text for ReportLab and convert **bold** to <b> tags."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escape(text))


def build_table(rows: list[list[str]], width: float) -> Table:
    column_count = len(rows[0])
    data = [[Paragraph(inline(cell), STYLES["cell"]) for cell in row] for row in rows]
    table = Table(data, colWidths=[width / column_count] * column_count, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E3ECE8")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#9DB3AB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def parse_markdown(markdown: str, width: float) -> list:
    story: list = []
    paragraph: list[str] = []
    list_items: list[str] = []
    list_kind = ""
    table_rows: list[list[str]] = []

    def flush() -> None:
        nonlocal paragraph, list_items, list_kind, table_rows
        if paragraph:
            story.append(Paragraph(inline(" ".join(paragraph)), STYLES["body"]))
            paragraph = []
        if list_items:
            items = [ListItem(Paragraph(inline(item), STYLES["body"])) for item in list_items]
            bullet_type = "bullet" if list_kind == "bullet" else "1"
            story.append(ListFlowable(items, bulletType=bullet_type, leftIndent=14))
            list_items, list_kind = [], ""
        if table_rows:
            story.append(build_table(table_rows, width))
            story.append(Spacer(1, 6))
            table_rows = []

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            flush()
        elif line.startswith("|"):
            if paragraph or list_items:
                flush()
            if not TABLE_SEPARATOR.match(line):
                table_rows.append([cell.strip() for cell in line.strip("|").split("|")])
        elif line.startswith("### "):
            flush()
            story.append(Paragraph(inline(line[4:]), STYLES["h3"]))
        elif line.startswith("## "):
            flush()
            story.append(Paragraph(inline(line[3:]), STYLES["h2"]))
        elif line.startswith("# "):
            flush()
            story.append(Paragraph(inline(line[2:]), STYLES["title"]))
        elif (match := BULLET.match(line)) or (match := NUMBERED.match(line)):
            kind = "bullet" if line.startswith("- ") else "numbered"
            if paragraph or table_rows or (list_items and kind != list_kind):
                flush()
            list_kind = kind
            list_items.append(match.group(1))
        else:
            if list_items or table_rows:
                flush()
            paragraph.append(line)
    flush()
    return story


def render(source: Path) -> Path:
    markdown = source.read_text(encoding="utf-8")
    doc_id_match = DOC_ID.search(markdown)
    if not doc_id_match:
        raise ValueError(f"{source.name} has no 'Document ID' row in its header table")
    doc_id = doc_id_match.group(1)
    title = markdown.splitlines()[0].lstrip("# ").strip()

    output = OUTPUT_DIR / f"{source.stem}.pdf"
    document = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=title,
        author="Veridane Bank",
        subject=doc_id,
    )

    def footer(canvas, doc) -> None:
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.drawString(2 * cm, 1.2 * cm, f"{doc_id} {title}")
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
        canvas.restoreState()

    document.build(
        parse_markdown(markdown, document.width),
        onFirstPage=footer,
        onLaterPages=footer,
    )
    return output


def main() -> None:
    sources = sorted(SOURCE_DIR.glob("*.md"))
    if not sources:
        raise SystemExit(f"No Markdown sources found in {SOURCE_DIR}")
    for source in sources:
        output = render(source)
        print(f"Rendered {source.name} -> {output.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
