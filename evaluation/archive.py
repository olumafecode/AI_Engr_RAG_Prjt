"""Keep a finished evaluation run before starting another one.

Run from the project root:
    python -m evaluation.archive run1

Moves the run's result files into evaluation/results/runs/run1/, so the next
quality and latency runs start fresh and the report can compare the runs side
by side. The ablation results stay where they are: they measure retrieval only,
which a change to the answer prompt does not affect.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

from evaluation.common import RESULTS_DIR
from evaluation.report import write_report

RUN_FILES = (
    "quality_results.json",
    "quality_summary.json",
    "latency_results.json",
    "latency_summary.json",
    "judge_agreement.json",
    "hand_labels.csv",
    "review_sheet.md",
    "report.md",
)


def archive_run(name: str, base: Path = RESULTS_DIR) -> list[str]:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        raise ValueError("Use letters, digits, - or _ for the run name, e.g. run1")
    target = base / "runs" / name
    if target.exists():
        raise FileExistsError(f"{target} already exists; choose another name")
    present = [file for file in RUN_FILES if (base / file).is_file()]
    if "quality_summary.json" not in present:
        raise FileNotFoundError("No finished quality run to archive (quality_summary.json)")
    target.mkdir(parents=True)
    for file in present:
        shutil.move(str(base / file), str(target / file))
    write_report(base)
    return present


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        sys.exit("Usage: python -m evaluation.archive <run name>, e.g. run1")
    try:
        moved = archive_run(args[0])
    except (ValueError, FileExistsError, FileNotFoundError) as error:
        sys.exit(str(error))
    print(f"Moved {', '.join(moved)} to evaluation/results/runs/{args[0]}/")


if __name__ == "__main__":
    main()
