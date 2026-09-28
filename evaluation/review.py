"""Check the LLM judge against your own labels on 10 answers.

Run from the project root after evaluation.quality:
    python -m evaluation.review            # writes the review sheet and a label file
    python -m evaluation.review --score    # compares your labels with the judge

Step 1 writes evaluation/results/review_sheet.md (each sampled question with the
reference answer, the system's answer, its citations, and the full excerpts) and
evaluation/results/hand_labels.csv. The judge's verdicts are left out of the sheet
so they cannot influence you. Fill in the three label columns in the CSV:
    your_grounded           yes or no
    your_citations_correct  yes or no
    your_correctness        full, partial, or incorrect
Step 2 reports how often you and the judge agree on each of the three labels.
"""

from __future__ import annotations

import argparse
import csv
import random
import sys

from app.config import Settings
from evaluation.common import RESULTS_DIR, load_chunk_texts, read_json, write_json
from evaluation.judge import format_citations, format_excerpts
from evaluation.report import write_report

SAMPLE_SIZE = 10
LABELS = RESULTS_DIR / "hand_labels.csv"
SHEET = RESULTS_DIR / "review_sheet.md"
YES = {"yes", "y", "true", "1"}
NO = {"no", "n", "false", "0"}


def judged_records() -> list[dict]:
    data = read_json("quality_results.json")
    if not data:
        sys.exit("Run python -m evaluation.quality first.")
    return [r for r in data["records"] if r.get("judge")]


def write_sheet(settings: Settings) -> None:
    records = judged_records()
    chosen = sorted(
        random.Random(settings.seed).sample(records, min(SAMPLE_SIZE, len(records))),
        key=lambda r: r["id"],
    )
    chunks = load_chunk_texts(settings)
    parts = [
        "# Judge validation sheet",
        "",
        "For each question, read the excerpts, then record in `hand_labels.csv`:",
        "- **grounded**: is every statement in the answer supported by the excerpts? (yes/no)",
        "- **citations correct**: does each citation point to an excerpt that supports its "
        "statement? (yes/no)",
        "- **correctness**: compared with the reference answer: full, partial, or incorrect",
        "",
    ]
    for record in chosen:
        parts += [
            f"## {record['id']}: {record['question']}",
            "",
            f"**Reference answer:** {record['gold_answer']}",
            "",
            f"**System answer:** {record['answer']}",
            "",
            "**Citations:**",
            "```",
            format_citations(record["citations"], record["retrieved"]),
            "```",
            "",
            "**Excerpts the system was given:**",
            "```",
            format_excerpts(record["retrieved"], chunks),
            "```",
            "",
        ]
    SHEET.write_text("\n".join(parts), encoding="utf-8")
    with LABELS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["id", "question", "your_grounded", "your_citations_correct", "your_correctness"]
        )
        for record in chosen:
            writer.writerow([record["id"], record["question"], "", "", ""])
    print(f"Wrote {SHEET} and {LABELS}. Fill in the three 'your_' columns, then run:")
    print("    python -m evaluation.review --score")


def yes_no(value: str, where: str) -> bool:
    value = value.strip().lower()
    if value in YES:
        return True
    if value in NO:
        return False
    sys.exit(f"Expected yes or no for {where}, found {value!r}.")


def score() -> None:
    if not LABELS.is_file():
        sys.exit("No labels found. Run python -m evaluation.review first.")
    judged = {r["id"]: r["judge"] for r in judged_records()}
    with LABELS.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    comparisons = []
    for row in rows:
        verdict = judged[row["id"]]
        correctness = row["your_correctness"].strip().lower()
        if correctness not in ("full", "partial", "incorrect"):
            sys.exit(
                f"Expected full, partial, or incorrect for {row['id']}, found {correctness!r}."
            )
        comparisons.append(
            {
                "id": row["id"],
                "grounded": yes_no(row["your_grounded"], row["id"]) == verdict["grounded"],
                "citations_correct": yes_no(row["your_citations_correct"], row["id"])
                == verdict["citations_correct"],
                "correctness": correctness == verdict["correctness"],
            }
        )
    count = len(comparisons)
    agreement = {
        field: round(sum(c[field] for c in comparisons) / count, 3)
        for field in ("grounded", "citations_correct", "correctness")
    }
    write_json(
        "judge_agreement.json", {"answers": count, "agreement": agreement, "details": comparisons}
    )
    write_report()
    for field, value in agreement.items():
        print(f"{field:18} you and the judge agree on {value:.0%} of {count} answers")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate the LLM judge against hand labels.")
    parser.add_argument("--score", action="store_true", help="compare your labels with the judge")
    args = parser.parse_args(argv)
    if args.score:
        score()
    else:
        write_sheet(Settings.from_env())


if __name__ == "__main__":
    main()
