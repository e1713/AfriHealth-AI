"""Generate current benchmark summaries from aggregate evaluation metrics."""

from __future__ import annotations

import argparse
import csv
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from evaluator import MODEL_NAMES


BENCHMARK_START = "<!-- BEGIN AUTO-GENERATED EVALUATION SUMMARY -->"
BENCHMARK_END = "<!-- END AUTO-GENERATED EVALUATION SUMMARY -->"
RECOMMENDATION_START = "<!-- BEGIN AUTO-GENERATED MODEL RECOMMENDATION -->"
RECOMMENDATION_END = "<!-- END AUTO-GENERATED MODEL RECOMMENDATION -->"


def load_evaluation_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"model_name", "evaluation_status", "mean_wer"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("Evaluation CSV is missing required summary columns")
        return list(reader)


def _metric(value: str | None, *, percent: bool = False) -> str:
    if value is None or not value.strip():
        return "N/A"
    try:
        numeric = float(value)
    except ValueError:
        return "N/A"
    if not math.isfinite(numeric):
        return "N/A"
    return f"{numeric:.2%}" if percent else f"{numeric:.3f}"


def _integer(value: str | None) -> str:
    if value is None or not value.strip():
        return "0"
    try:
        return str(int(float(value)))
    except ValueError:
        return "0"


def build_benchmark_section(rows: Sequence[dict[str, str]]) -> str:
    by_model = {row["model_name"]: row for row in rows}
    lines = [
        BENCHMARK_START,
        "## Current Evaluation Pipeline Summary",
        "",
        f"> Generated from `results/final_evaluation_metrics.csv` at "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}. "
        "The authoritative source corpus contains 100 cases; references and labels remain under review.",
        "",
        "| Model | Status | Live outputs | Mock outputs | Failed | Mean WER | Medical-term recall | Critical miss rate | Live mean latency (s) | Simulated mean latency (s) |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for model_name in MODEL_NAMES:
        row = by_model.get(model_name, {})
        lines.append(
            "| "
            + " | ".join(
                (
                    model_name,
                    row.get("evaluation_status", "no_outputs"),
                    _integer(row.get("live_success_count")),
                    _integer(row.get("mock_success_count")),
                    _integer(row.get("failed_case_count")),
                    _metric(row.get("mean_wer")),
                    _metric(row.get("mean_medical_term_recall"), percent=True),
                    _metric(row.get("critical_term_miss_rate"), percent=True),
                    _metric(row.get("mean_latency_seconds")),
                    _metric(row.get("mean_simulated_latency_seconds")),
                )
            )
            + " |"
        )
    lines.extend(
        (
            "",
            "**Interpretation:** Mock outputs are synthetic pipeline fixtures. "
            "Accuracy and critical-term metrics are intentionally `N/A` for mock-only runs; "
            "simulated latency is not measured inference latency.",
            "",
            "Code-switch category breakdown is available in "
            "`results/figures/codeswitch_breakdown.png` only when live outputs can be "
            "joined to manifest categories. Those categories are provisional script-share "
            "estimates until human confirmation.",
            BENCHMARK_END,
        )
    )
    return "\n".join(lines)


def build_recommendation_section(rows: Sequence[dict[str, str]]) -> str:
    by_model = {row["model_name"]: row for row in rows}
    lines = [
        RECOMMENDATION_START,
        "## Automated Evaluation Snapshot",
        "",
        "> Generated from `results/final_evaluation_metrics.csv`. This is a "
        "descriptive pipeline summary, not clinical approval or an autonomous-use recommendation.",
        "",
        "| Model | Evidence status | Live / mock outputs | WER | Medical-term recall | Critical-term miss rate | Live latency (s) |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for model_name in MODEL_NAMES:
        row = by_model.get(model_name, {})
        lines.append(
            "| "
            + " | ".join(
                (
                    model_name,
                    row.get("evaluation_status", "no_outputs"),
                    f"{_integer(row.get('live_success_count'))} / {_integer(row.get('mock_success_count'))}",
                    _metric(row.get("mean_wer")),
                    _metric(row.get("mean_medical_term_recall"), percent=True),
                    _metric(row.get("critical_term_miss_rate"), percent=True),
                    _metric(row.get("mean_latency_seconds")),
                )
            )
            + " |"
        )
    lines.extend(
        (
            "",
            "### Recommendation",
            "",
            "No model is ranked or recommended for clinical use by this generated summary. "
            "A mock-only run provides no evidence about model accuracy or clinical suitability. "
            "Live scores against references not independently verified against audio remain provisional.",
            "",
            "### Evidence required before selecting a model",
            "",
            "- Paired live outputs on the same audio cases with exact model/provider versions.",
            "- Independently audio-verified and adjudicated references and target terms.",
            "- Review of medication, dose, negation, and critical-term errors by qualified clinicians.",
            "- Hosted-data governance, privacy, latency, reliability, and deployment review.",
            "",
            RECOMMENDATION_END,
        )
    )
    return "\n".join(lines)


def update_marked_section(path: Path, start_marker: str, end_marker: str, section: str) -> None:
    """Replace a generated block idempotently, preserving surrounding document text."""
    if path.exists():
        original = path.read_text(encoding="utf-8").rstrip()
    else:
        original = f"# {path.stem.replace('_', ' ').title()}\n"

    start_index = original.find(start_marker)
    end_index = original.find(end_marker)
    if (start_index == -1) != (end_index == -1):
        raise ValueError(f"Unbalanced generated-section markers in {path}")
    if start_index >= 0:
        end_index += len(end_marker)
        updated = original[:start_index].rstrip() + "\n\n" + section + original[end_index:].lstrip()
    else:
        updated = original + "\n\n" + section
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(updated.rstrip() + "\n", encoding="utf-8")


def generate_reports(
    metrics_path: Path,
    benchmark_report_path: Path,
    recommendation_path: Path,
) -> None:
    rows = load_evaluation_rows(metrics_path)
    update_marked_section(
        benchmark_report_path,
        BENCHMARK_START,
        BENCHMARK_END,
        build_benchmark_section(rows),
    )
    update_marked_section(
        recommendation_path,
        RECOMMENDATION_START,
        RECOMMENDATION_END,
        build_recommendation_section(rows),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Update benchmark reports from evaluation metrics.")
    root = Path(__file__).resolve().parent
    parser.add_argument("--metrics", type=Path, default=root / "results" / "final_evaluation_metrics.csv")
    parser.add_argument("--benchmark-report", type=Path, default=root / "BENCHMARK_RESULTS.md")
    parser.add_argument("--recommendation-report", type=Path, default=root / "MODEL_RECOMMENDATION.md")
    args = parser.parse_args(argv)
    try:
        generate_reports(
            args.metrics.resolve(),
            args.benchmark_report.resolve(),
            args.recommendation_report.resolve(),
        )
    except (OSError, ValueError) as error:
        print(f"Report generation failed: {error}", file=sys.stderr)
        return 2
    print(f"Updated {args.benchmark_report}")
    print(f"Updated {args.recommendation_report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
