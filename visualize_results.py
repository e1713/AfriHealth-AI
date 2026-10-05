"""Create mock-aware figures from AfriHealth benchmark evaluation artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns

from evaluator import MODEL_NAMES, calculate_medical_term_recall, calculate_wer, parse_terms


TIER_1_MODELS = ("Sahara", "Gemini", "Whisper")
TIER_2_MODELS = ("Wav2Vec2", "SpeechBrain", "NeMo")
CODE_SWITCH_CATEGORIES = (
    "Mostly Amharic",
    "Balanced Mix",
    "Mostly English Clinical Terms",
)
LIVE_STATUSES = {"200"}
SUCCESS_STATUSES = {"200", "MOCK"}


def _number(value: str | None) -> float | None:
    if value is None or not value.strip():
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def load_metrics(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not {"model_name", "evaluation_status"}.issubset(reader.fieldnames):
            raise ValueError("Evaluation metrics CSV must contain model_name and evaluation_status")
        rows = list(reader)
    known = {row["model_name"] for row in rows}
    return rows + [
        {
            "model_name": model_name,
            "evaluation_status": "no_outputs",
        }
        for model_name in MODEL_NAMES
        if model_name not in known
    ]


def load_attempts(path: Path | None) -> dict[tuple[str, str], dict[str, object]]:
    """Read JSONL inference attempts and retain the latest attempt per pair."""
    if path is None or not path.exists():
        return {}
    latest: dict[tuple[str, str], dict[str, object]] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                attempt = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid inference log at {path}:{line_number}: {error}") from error
            if not isinstance(attempt, dict):
                raise ValueError(f"Inference log row {line_number} must be a JSON object")
            case_id = str(attempt.get("case_id", "")).strip()
            model_name = str(attempt.get("model_name", "")).strip()
            if case_id and model_name:
                latest[(case_id, model_name)] = attempt
    return latest


def _placeholder(axis: plt.Axes, title: str, detail: str) -> None:
    axis.set_title(title)
    axis.text(
        0.5,
        0.5,
        detail,
        transform=axis.transAxes,
        ha="center",
        va="center",
        wrap=True,
        color="#475569",
        fontsize=11,
    )
    axis.set_xticks([])
    axis.set_yticks([])


def _save_figure(figure: plt.Figure, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.tight_layout()
    figure.savefig(destination, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def plot_wer_comparison(metrics: Sequence[dict[str, str]], destination: Path) -> None:
    values = {
        row["model_name"]: _number(row.get("mean_wer"))
        for row in metrics
    }
    figure, axis = plt.subplots(figsize=(10, 5.8))
    available = any(values.get(model) is not None for model in MODEL_NAMES)
    if not available:
        _placeholder(
            axis,
            "Normalized WER by model and tier",
            "WER unavailable: no eligible live transcript outputs.\nMock outputs are not scored.",
        )
    else:
        labels = list(TIER_1_MODELS + TIER_2_MODELS)
        scores = [values.get(model) for model in labels]
        colors = [
            *(sns.color_palette("Blues", n_colors=3)),
            *(sns.color_palette("Greens", n_colors=3)),
        ]
        bars = axis.bar(labels, [score if score is not None else 0 for score in scores], color=colors)
        for bar, score in zip(bars, scores):
            if score is None:
                axis.text(bar.get_x() + bar.get_width() / 2, 0.01, "N/A", ha="center", va="bottom")
        axis.set_ylabel("Mean normalized WER (lower is better)")
        axis.set_title("Normalized WER by model and tier")
        axis.tick_params(axis="x", rotation=20)
        axis.grid(axis="y", alpha=0.2)
        axis.text(
            0.01,
            -0.23,
            "Tier 1: Sahara, Gemini, Whisper     Tier 2: Wav2Vec2, SpeechBrain, NeMo",
            transform=axis.transAxes,
            fontsize=9,
        )
    _save_figure(figure, destination)


def plot_medical_recall_and_critical_misses(
    metrics: Sequence[dict[str, str]],
    destination: Path,
) -> None:
    by_model = {row["model_name"]: row for row in metrics}
    recall_values = {
        model: _number(by_model.get(model, {}).get("mean_medical_term_recall"))
        for model in MODEL_NAMES
    }
    critical_rates = {
        model: _number(by_model.get(model, {}).get("critical_term_miss_rate"))
        for model in MODEL_NAMES
    }
    figure, axis = plt.subplots(figsize=(10, 5.8))
    if not any(value is not None for value in (*recall_values.values(), *critical_rates.values())):
        _placeholder(
            axis,
            "Medical-term recall and critical-term miss rate",
            "Clinical metrics unavailable: no eligible live transcript outputs.\nMock outputs are not scored.",
        )
    else:
        labels = list(MODEL_NAMES)
        positions = list(range(len(labels)))
        width = 0.36
        recall_bars = axis.bar(
            [position - width / 2 for position in positions],
            [recall_values[label] if recall_values[label] is not None else 0 for label in labels],
            width,
            label="Medical-term recall",
            color="#2563eb",
        )
        miss_bars = axis.bar(
            [position + width / 2 for position in positions],
            [critical_rates[label] if critical_rates[label] is not None else 0 for label in labels],
            width,
            label="Critical-term miss rate",
            color="#dc2626",
        )
        for bars, series in (
            (recall_bars, recall_values),
            (miss_bars, critical_rates),
        ):
            for bar, label in zip(bars, labels):
                if series[label] is None:
                    axis.text(bar.get_x() + bar.get_width() / 2, 0.012, "N/A", ha="center", fontsize=8)
        axis.set_xticks(positions, labels, rotation=20)
        axis.set_ylim(0, 1)
        axis.set_ylabel("Rate")
        axis.set_title("Medical-term recall and critical-term miss rate")
        axis.legend()
        axis.grid(axis="y", alpha=0.2)
    _save_figure(figure, destination)


def plot_latency_vs_accuracy(
    metrics: Sequence[dict[str, str]],
    attempts: dict[tuple[str, str], dict[str, object]],
    destination: Path,
) -> None:
    by_model = {row["model_name"]: row for row in metrics}
    p95_latency: dict[str, float] = {}
    samples: dict[str, list[float]] = {model: [] for model in MODEL_NAMES}
    for (_, model_name), record in attempts.items():
        if (
            model_name in samples
            and str(record.get("status_code", "")) in LIVE_STATUSES
        ):
            try:
                latency = float(record["latency_seconds"])
            except (KeyError, TypeError, ValueError):
                continue
            if math.isfinite(latency) and latency >= 0:
                samples[model_name].append(latency)
    for model_name, latencies in samples.items():
        if latencies:
            ordered = sorted(latencies)
            index = max(0, math.ceil(0.95 * len(ordered)) - 1)
            p95_latency[model_name] = ordered[index]

    figure, axis = plt.subplots(figsize=(9, 5.8))
    points = [
        (
            model,
            p95_latency.get(model),
            _number(by_model.get(model, {}).get("mean_medical_term_recall")),
        )
        for model in MODEL_NAMES
    ]
    valid = [(model, latency, accuracy) for model, latency, accuracy in points if latency is not None and accuracy is not None]
    if not valid:
        _placeholder(
            axis,
            "P95 latency vs medical-term recall",
            "Trade-off unavailable: requires per-call live latency and eligible accuracy metrics.\n"
            "The current summary has only mean latency; mock latency is simulated.",
        )
    else:
        palette = dict(zip(MODEL_NAMES, sns.color_palette("colorblind", n_colors=len(MODEL_NAMES))))
        for model, latency, accuracy in valid:
            axis.scatter(latency, accuracy, s=90, color=palette[model], label=model)
            axis.annotate(model, (latency, accuracy), xytext=(5, 5), textcoords="offset points", fontsize=8)
        axis.set_xlabel("P95 live latency (seconds)")
        axis.set_ylabel("Medical-term recall")
        axis.set_ylim(0, 1)
        axis.set_title("P95 live latency vs medical-term recall")
        axis.grid(alpha=0.25)
        axis.legend()
    _save_figure(figure, destination)


def compute_codeswitch_breakdown(
    manifest_path: Path,
    outputs_path: Path,
) -> dict[str, dict[str, list[float]]]:
    """Compute category-specific metrics from live outputs only."""
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"case_id", "reference_transcript", "code_switch_category"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("Manifest lacks fields needed for code-switch breakdown")
        references = {row["case_id"].strip(): row for row in reader}

    latest_outputs: dict[tuple[str, str], dict[str, str]] = {}
    with outputs_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required_outputs = {
            "case_id",
            "model_name",
            "predicted_transcript",
            "status_code",
        }
        if not reader.fieldnames or not required_outputs.issubset(reader.fieldnames):
            raise ValueError("Model output CSV lacks fields needed for code-switch breakdown")
        for row in reader:
            latest_outputs[(row["case_id"].strip(), row["model_name"].strip())] = row

    breakdown = {
        category: {metric: [] for metric in ("wer", "medical_term_recall")}
        for category in CODE_SWITCH_CATEGORIES
    }
    for (case_id, model_name), output in latest_outputs.items():
        reference_row = references.get(case_id)
        if (
            model_name not in MODEL_NAMES
            or reference_row is None
            or output.get("status_code", "").strip() not in LIVE_STATUSES
            or not output.get("predicted_transcript", "").strip()
        ):
            continue
        category = reference_row.get("code_switch_category", "").strip()
        if category not in breakdown:
            continue
        reference = reference_row.get("reference_transcript", "").strip()
        hypothesis = output["predicted_transcript"].strip()
        if not reference:
            continue
        breakdown[category]["wer"].append(calculate_wer(reference, hypothesis))
        focus_terms = parse_terms(
            reference_row.get("focus_terms", "").strip()
            or reference_row.get("target_terms", "").strip()
        )
        recall, _, _ = calculate_medical_term_recall(reference, hypothesis, focus_terms)
        if recall is not None:
            breakdown[category]["medical_term_recall"].append(recall)
    return breakdown


def plot_codeswitch_breakdown(
    breakdown: dict[str, dict[str, list[float]]],
    destination: Path,
) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    metric_specs = (
        ("wer", "Mean normalized WER (lower is better)"),
        ("medical_term_recall", "Mean medical-term recall"),
    )
    has_any = any(values for category in breakdown.values() for values in category.values())
    if not has_any:
        _placeholder(
            axes[0],
            "WER by code-switch category",
            "Unavailable: no live outputs scored.\nMock transcripts are not included.",
        )
        _placeholder(
            axes[1],
            "Medical-term recall by code-switch category",
            "Unavailable: no live outputs scored.\nMock transcripts are not included.",
        )
    else:
        for axis, (metric, title) in zip(axes, metric_specs):
            means = [
                sum(breakdown[category][metric]) / len(breakdown[category][metric])
                if breakdown[category][metric]
                else None
                for category in CODE_SWITCH_CATEGORIES
            ]
            bars = axis.bar(
                range(len(CODE_SWITCH_CATEGORIES)),
                [value if value is not None else 0 for value in means],
                color=sns.color_palette("Set2", n_colors=3),
            )
            for bar, value in zip(bars, means):
                if value is None:
                    axis.text(bar.get_x() + bar.get_width() / 2, 0.012, "N/A", ha="center", fontsize=8)
            axis.set_xticks(range(len(CODE_SWITCH_CATEGORIES)), CODE_SWITCH_CATEGORIES, rotation=22, ha="right")
            axis.set_title(title)
            axis.grid(axis="y", alpha=0.2)
            if metric == "medical_term_recall":
                axis.set_ylim(0, 1)
    figure.suptitle("Live metrics by provisional code-switch category")
    _save_figure(figure, destination)


def generate_figures(
    metrics_path: Path,
    output_dir: Path,
    *,
    manifest_path: Path | None = None,
    outputs_path: Path | None = None,
    inference_log_path: Path | None = None,
) -> list[Path]:
    metrics = load_metrics(metrics_path)
    attempts = load_attempts(inference_log_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    destinations = [
        output_dir / "wer_comparison.png",
        output_dir / "medical_term_recall.png",
        output_dir / "latency_vs_accuracy.png",
        output_dir / "codeswitch_breakdown.png",
    ]
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.05)
    plot_wer_comparison(metrics, destinations[0])
    plot_medical_recall_and_critical_misses(metrics, destinations[1])
    plot_latency_vs_accuracy(metrics, attempts, destinations[2])
    if manifest_path and outputs_path and manifest_path.exists() and outputs_path.exists():
        breakdown = compute_codeswitch_breakdown(manifest_path, outputs_path)
    else:
        breakdown = {
            category: {metric: [] for metric in ("wer", "medical_term_recall")}
            for category in CODE_SWITCH_CATEGORIES
        }
    plot_codeswitch_breakdown(breakdown, destinations[3])
    return destinations


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate publication-ready benchmark figures.")
    root = Path(__file__).resolve().parent
    parser.add_argument("--metrics", type=Path, default=root / "results" / "final_evaluation_metrics.csv")
    parser.add_argument("--output-dir", type=Path, default=root / "results" / "figures")
    parser.add_argument("--manifest", type=Path, default=root / "benchmark" / "metadata" / "BENCHMARK_MANIFEST.csv")
    parser.add_argument("--outputs", type=Path, default=root / "results" / "model_comparisons.csv")
    parser.add_argument("--inference-log", type=Path, default=root / "results" / "inference_log.jsonl")
    args = parser.parse_args(argv)
    try:
        paths = generate_figures(
            args.metrics.resolve(),
            args.output_dir.resolve(),
            manifest_path=args.manifest.resolve(),
            outputs_path=args.outputs.resolve(),
            inference_log_path=args.inference_log.resolve(),
        )
    except (OSError, ValueError) as error:
        print(f"Visualization failed: {error}", file=sys.stderr)
        return 2
    for path in paths:
        print(f"Generated {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
