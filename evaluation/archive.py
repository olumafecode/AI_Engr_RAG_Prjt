"""Keep a finished evaluation run before starting another one.

Run from the project root:
    python -m evaluation.archive run1

Moves the run's result files into evaluation/results/runs/run1/, so the next
quality and latency runs start fresh and the report can compare the runs side
by side. The ablation results stay where they are: they measure retrieval only,
which a change to the answer prompt does not affect.

To make an archived run the current one again (for example, after deciding to
keep its settings), archive the current run first, then restore:
    python -m evaluation.archive run2-complete
    python -m evaluation.archive --restore run1
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


def restore_run(name: str, base: Path = RESULTS_DIR) -> list[str]:
    source = base / "runs" / name
    if not source.is_dir():
        raise FileNotFoundError(f"No archived run called {name!r}")
    if (base / "quality_summary.json").is_file():
        raise FileExistsError("Archive the current run first, so it is not overwritten")
    present = [file for file in RUN_FILES if (source / file).is_file()]
    for file in present:
        shutil.move(str(source / file), str(base / file))
    if not any(source.iterdir()):
        source.rmdir()
    write_report(base)
    return present


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    restore = bool(args) and args[0] == "--restore"
    names = args[1:] if restore else args
    if len(names) != 1:
        sys.exit("Usage: python -m evaluation.archive [--restore] <run name>, e.g. run1")
    try:
        moved = restore_run(names[0]) if restore else archive_run(names[0])
    except (ValueError, FileExistsError, FileNotFoundError) as error:
        sys.exit(str(error))
    where = "evaluation/results/" if restore else f"evaluation/results/runs/{names[0]}/"
    print(f"Moved {', '.join(moved)} to {where}")


if __name__ == "__main__":
    main()
