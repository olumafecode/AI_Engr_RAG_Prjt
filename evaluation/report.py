"""Combine whatever evaluation results exist into evaluation/results/report.md."""

from __future__ import annotations

from pathlib import Path

from evaluation.common import RESULTS_DIR, read_json


def _value(name: str, value) -> str:
    if value is None:
        return "n/a"
    if name.endswith("_ms"):
        return f"{value:,.0f} ms"
    return f"{value:.0%}"


def _target(name: str, item: dict) -> str:
    comparison = "≥" if item["comparison"] == ">=" else "≤"
    return f"{comparison} {_value(name, item['target'])}"


def _met(item: dict) -> str:
    return {True: "Yes", False: "No", None: "n/a"}[item["met"]]


def metrics_table(metrics: dict) -> list[str]:
    lines = ["| Metric | Result | Target | Met | n |", "|---|---|---|---|---|"]
    for name, item in metrics.items():
        lines.append(
            f"| {item['description']} | {_value(name, item['value'])} | {_target(name, item)} "
            f"| {_met(item)} | {item['n']} |"
        )
    return lines


def answer_stats(records: list[dict]) -> dict | None:
    """What the answered in-scope questions looked like, to explain differences between runs."""
    answered = [r for r in records if r["in_scope"] and not r.get("error") and not r.get("refused")]
    if not answered:
        return None
    count = len(answered)
    return {
        "Mean words per answer": round(sum(r["words"] for r in answered) / count),
        "Mean citations per answer": round(sum(len(r["citations"]) for r in answered) / count, 1),
        "Mean documents cited per answer": round(
            sum(len(r["cited_docs"]) for r in answered) / count, 1
        ),
        "Answers citing a document outside the acceptable sources": sum(
            1 for r in answered if r.get("citation_docs_ok") is False
        ),
        "Answers whose citations the judge rejected": sum(
            1 for r in answered if r.get("judge") and not r["judge"]["citations_correct"]
        ),
    }


def stats_table(columns: list[tuple[str, list[dict]]]) -> list[str]:
    stats = [(name, answer_stats(records)) for name, records in columns]
    if not any(item for _, item in stats):
        return []
    lines = [
        "Answer characteristics (answered in-scope questions):",
        "",
        "| Measure | " + " | ".join(name for name, _ in stats) + " |",
        "|---|" + "---|" * len(stats),
    ]
    labels = next(item for _, item in stats if item)
    for label in labels:
        cells = [str(item[label]) if item else "not run" for _, item in stats]
        lines.append(f"| {label} | " + " | ".join(cells) + " |")
    return lines


def earlier_runs(base: Path) -> list[tuple[str, dict | None, dict | None, dict | None]]:
    """(name, quality summary, latency summary, judge agreement) for each archived run."""
    runs = []
    for folder in sorted(path for path in (base / "runs").glob("*") if path.is_dir()):
        runs.append(
            (
                folder.name,
                read_json("quality_summary.json", folder),
                read_json("latency_summary.json", folder),
                read_json("judge_agreement.json", folder),
            )
        )
    return runs


def comparison_table(runs: list, quality: dict | None, latency: dict | None) -> list[str]:
    columns = [(name, q, lat) for name, q, lat, _ in runs] + [("Current run", quality, latency)]
    header = "| Metric | " + " | ".join(name for name, _, _ in columns) + " | Target |"
    lines = [header, "|---|" + "---|" * len(columns) + "---|"]
    names = list((quality or runs[-1][1] or {}).get("metrics", {}))
    names += ["latency_p50_ms", "latency_p95_ms"]
    for name in names:
        cells, reference = [], None
        for _, q, lat in columns:
            source = (lat or {}) if name.startswith("latency") else (q or {})
            item = source.get("metrics", {}).get(name)
            reference = reference or item
            cells.append(_value(name, item["value"]) if item else "not run")
        if reference:
            label = reference["description"]
            lines.append(f"| {label} | " + " | ".join(cells) + f" | {_target(name, reference)} |")
    styles = [
        ((q or {}).get("settings") or {}).get("answer_style", "concise") for _, q, _ in columns
    ]
    lines += [
        "",
        "Answer style per run: "
        + ", ".join(f"{name}: {style}" for (name, _, _), style in zip(columns, styles, strict=True))
        + ".",
    ]
    return lines


def write_report(base: Path = RESULTS_DIR) -> None:
    quality = read_json("quality_summary.json", base)
    records = (read_json("quality_results.json", base) or {}).get("records", [])
    latency = read_json("latency_summary.json", base)
    ablation = read_json("ablation_results.json", base)
    agreement = read_json("judge_agreement.json", base)
    runs = earlier_runs(base)
    agreement_source = "this run"
    if not agreement:
        for name, _, _, archived in reversed(runs):
            if archived:
                agreement, agreement_source = archived, name
                break

    out = [
        "# Evaluation Report",
        "",
        "Generated by the scripts in `evaluation/`. Question set: `evaluation/questions.jsonl`.",
        "",
    ]

    if quality:
        counts = quality["counts"]
        settings = quality["settings"]
        out += [
            "## Answer quality",
            "",
            f"{counts['questions']} questions ({counts['in_scope']} in scope, "
            f"{counts['out_of_scope']} out of scope). Answer model {settings['answer_model']} "
            f"(reasoning effort {settings['reasoning_effort']}, answer style "
            f"{settings.get('answer_style', 'concise')}), judge {settings['judge_model']}, "
            f"{settings['retrieval_mode']} retrieval with k = {settings['top_k']}, "
            f"{settings['chunk_strategy']} chunks, relevance threshold "
            f"{settings['relevance_threshold']}.",
            "",
            *metrics_table(quality["metrics"]),
            "",
            "Mean token F1 against the reference answers: "
            f"{_value('f1', quality['token_f1_mean'])}. "
            f"Refusals by reason: {quality['refusal_reasons']}.",
            "",
            "By question type (in scope):",
            "",
            "| Type | Questions | Correct (full or partial) | Retrieval hit rate |",
            "|---|---|---|---|",
        ]
        for kind, item in quality["by_type"].items():
            out.append(
                f"| {kind} | {item['questions']} | {_value('x', item['correct_full_or_partial'])} "
                f"| {_value('x', item['retrieval_hit_rate'])} |"
            )
        gate = quality["gate_scores"]
        out += [
            "",
            f"Best similarity scores: in-scope minimum {gate['in_scope_min']}, median "
            f"{gate['in_scope_median']}; out-of-scope maximum {gate['out_of_scope_max']}, median "
            f"{gate['out_of_scope_median']}.",
            "",
        ]

    if records:
        out += [
            "### Per question",
            "",
            "| ID | Type | Outcome | Correctness | Grounded | Citations OK | Source retrieved "
            "| Token F1 |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for r in records:
            verdict = r.get("judge") or {}
            outcome = (
                "error"
                if r.get("error")
                else (f"refused ({r['refusal_reason']})" if r.get("refused") else "answered")
            )
            citations_ok = (
                ""
                if not verdict
                else ("yes" if verdict["citations_correct"] and r.get("citation_docs_ok") else "no")
            )
            grounded = "" if not verdict else ("yes" if verdict["grounded"] else "no")
            hit = {True: "yes", False: "no", None: ""}[r.get("retrieval_hit")]
            f1 = "" if r.get("token_f1") is None else f"{r['token_f1']:.2f}"
            out.append(
                f"| {r['id']} | {r['type']} | {outcome} | {verdict.get('correctness', '')} "
                f"| {grounded} | {citations_ok} | {hit} | {f1} |"
            )
        out.append("")

    if runs:
        run_records = [
            (
                name,
                (read_json("quality_results.json", base / "runs" / name) or {}).get("records", []),
            )
            for name, _, _, _ in runs
        ] + [("Current run", records)]
        out += [
            "## Comparison with earlier runs",
            "",
            *comparison_table(runs, quality, latency),
            "",
            *stats_table(run_records),
            "",
        ]

    if agreement:
        values = agreement["agreement"]
        source = (
            ""
            if agreement_source == "this run"
            else (
                f" These labels were made on the answers of {agreement_source}; "
                "the judge model and its instructions have not changed since."
            )
        )
        out += [
            "## Judge validation",
            "",
            f"Hand labels on {agreement['answers']} answers agree with the judge on groundedness "
            f"{values['grounded']:.0%}, citations {values['citations_correct']:.0%}, and "
            f"correctness {values['correctness']:.0%} of the time.{source}",
            "",
        ]

    if latency:
        first = latency["first_health"]
        out += [
            "## Latency (deployed app)",
            "",
            f"{latency['requests']} questions sent to {latency['url']}, "
            f"{latency['pause_seconds']:.0f} seconds apart, after the warm-up had finished.",
            "",
            *metrics_table(latency["metrics"]),
            "",
            f"End-to-end: min {latency['wall_ms']['min']} ms, "
            f"mean {latency['wall_ms']['mean']} ms, "
            f"max {latency['wall_ms']['max']} ms. Server-side total: p50 "
            f"{latency['server_ms']['p50']} ms, p95 {latency['server_ms']['p95']} ms. "
            f"The first /health call took {first['wall_ms']:,} ms, and the service had been up for "
            f"{first['uptime_seconds']} s; a small uptime means that call included a wake-up.",
            "",
        ]

    if ablation:
        out += [
            "## Retrieval ablations",
            "",
            f"{ablation['questions']} in-scope questions. Hit rate: an acceptable source document "
            "is among the excerpts. MRR: 1 / rank of the first such excerpt. Gate columns count "
            f"questions whose best similarity is below the {ablation['threshold']} threshold.",
            "",
            "| Configuration | Hit rate | MRR | Source coverage | Missed | In-scope gated "
            "| Out-of-scope gated |",
            "|---|---|---|---|---|---|---|",
        ]
        for row in ablation["rows"]:
            gate = row["gate"]
            out.append(
                f"| {row['config']} | {row['hit_rate']:.0%} | {row['mrr']:.2f} "
                f"| {row['source_coverage']:.0%} | {', '.join(row['missed']) or '-'} "
                f"| {gate['in_scope_below_threshold']} | {gate['out_of_scope_below_threshold']} |"
            )
        out.append("")

    base.mkdir(parents=True, exist_ok=True)
    (base / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
