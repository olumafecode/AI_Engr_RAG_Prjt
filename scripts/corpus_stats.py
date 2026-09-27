"""Report word counts and estimated page counts for the policy corpus.

Run from the project root:  python -m scripts.corpus_stats

The brief asks for 30 to 120 pages. Pages are estimated at 500 words each,
and PDFs also show their real page count.
"""

from __future__ import annotations

from pypdf import PdfReader

from app.config import Settings
from app.corpus_utils import list_documents, read_text, word_count

WORDS_PER_PAGE = 500
MIN_PAGES, MAX_PAGES = 30, 120


def main() -> None:
    documents = list_documents(Settings.from_env().corpus_dir)
    if not documents:
        raise SystemExit("No documents found in the corpus folder.")

    total_words = 0
    print(f"{'Document':52} {'Words':>7} {'Est. pages':>11}")
    for path in documents:
        words = word_count(read_text(path))
        total_words += words
        note = f"  ({len(PdfReader(path).pages)} PDF pages)" if path.suffix == ".pdf" else ""
        print(f"{path.name:52} {words:7} {words / WORDS_PER_PAGE:11.1f}{note}")

    pages = total_words / WORDS_PER_PAGE
    within = MIN_PAGES <= pages <= MAX_PAGES
    print(f"\n{len(documents)} documents, {total_words} words, about {pages:.0f} pages.")
    print(f"Brief requires {MIN_PAGES} to {MAX_PAGES} pages: {'OK' if within else 'OUT OF RANGE'}")


if __name__ == "__main__":
    main()
