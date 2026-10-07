"""Evaluate ASR transcripts against the benchmark manifest.

Mock outputs are tracked for pipeline coverage but never scored as clinical
transcripts, and their simulated latency is reported separately from measured
live inference latency.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, TextIO


MODEL_NAMES = (
    "Sahara",
    "Gemini",
    "Whisper",
    "Wav2Vec2",
    "SpeechBrain",
    "NeMo",
)
SUCCESS_STATUSES = {"200", "MOCK"}
LIVE_SUCCESS_STATUSES = {"200"}
TRUE_VALUES = {"true", "1", "yes"}
PUNCTUATION_OR_SPACE = re.compile(r"[^\w\u1200-\u137f]+", flags=re.UNICODE)
TERM_SPLIT = re.compile(r"[;,]")

OUTPUT_COLUMNS = (
    "model_name",
    "evaluation_status",
    "case_count",
    "live_success_count",
    "mock_success_count",
    "failed_case_count",
    "mean_wer",
    "mean_medical_term_recall",
    "critical_term_miss_rate",
    "critical_term_misses",
    "critical_term_count",
    "mean_latency_seconds",
    "mean_simulated_latency_seconds",
    "latency_source",
)


@dataclass(frozen=True)
class EvaluationInputs:
    references: dict[str, dict[str, str]]
    medical_terms: dict[str, list[str]]
    outputs: dict[tuple[str, str], dict[str, str]]


def normalize_text(text: str) -> str:
    """Lowercase and replace punctuation with spaces while preserving scripts."""
    normalized = text.casefold()
    normalized = PUNCTUATION_OR_SPACE.sub(" ", normalized)
    return " ".join(normalized.split())


def calculate_wer(reference: str, hypothesis: str) -> float:
    """Calculate normalized token WER using jiwer when available.

    A local Levenshtein implementation keeps evaluation usable in lightweight
    environments that do not have the optional ``jiwer`` package installed.
    """
    normalized_reference = normalize_text(reference)
    normalized_hypothesis = normalize_text(hypothesis)
    reference_tokens = normalized_reference.split()
    hypothesis_tokens = normalized_hypothesis.split()

    if not reference_tokens:
        return 0.0 if not hypothesis_tokens else 1.0

    try:
        import jiwer
    except ImportError:
        previous = list(range(len(hypothesis_tokens) + 1))
        for row_index, reference_token in enumerate(reference_tokens, start=1):
            current = [row_index]
            for column_index, hypothesis_token in enumerate(hypothesis_tokens, start=1):
                current.append(
                    min(
                        current[-1] + 1,
                        previous[column_index] + 1,
                        previous[column_index - 1]
                        + (reference_token != hypothesis_token),
                    )
                )
            previous = current
        return previous[-1] / len(reference_tokens)

    return float(jiwer.wer(" ".join(reference_tokens), " ".join(hypothesis_tokens)))


def contains_term(text: str, term: str) -> bool:
    """Return whether a normalized clinical phrase occurs as whole tokens."""
    normalized_text = normalize_text(text).split()
    normalized_term = normalize_text(term).split()
    if not normalized_term or len(normalized_term) > len(normalized_text):
        return False
    width = len(normalized_term)
    return any(
        normalized_text[index : index + width] == normalized_term
        for index in range(len(normalized_text) - width + 1)
    )


def parse_terms(value: str) -> list[str]:
    """Parse semicolon/comma-separated focus terms and discard empty entries."""
    return [term.strip().strip('"').strip("'") for term in TERM_SPLIT.split(value) if term.strip()]


def calculate_medical_term_recall(
    reference: str,
    hypothesis: str,
    target_terms: Sequence[str],
) -> tuple[float | None, int, int]:
    """Return case recall, matched count, and eligible reference-term count.

    Focus terms not found in the reference are excluded from the denominator,
    since they cannot be treated as reference mentions for ASR scoring.
    """
    eligible_terms = [
        term
        for term in target_terms
        if contains_term(reference, term)
    ]
    if not eligible_terms:
        return None, 0, 0
    matched = sum(contains_term(hypothesis, term) for term in eligible_terms)
    return matched / len(eligible_terms), matched, len(eligible_terms)


def load_manifest(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"case_id", "reference_transcript"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(
                f"Manifest must contain columns: {', '.join(sorted(required))}"
            )
        rows = list(reader)
    references: dict[str, dict[str, str]] = {}
    for row in rows:
        case_id = row.get("case_id", "").strip()
        if not case_id:
            raise ValueError("Manifest contains an empty case_id")
        if case_id in references:
            raise ValueError(f"Manifest contains duplicate case_id: {case_id}")
        references[case_id] = row
    if not references:
        raise ValueError(f"Manifest contains no cases: {path}")
    return references


def load_medical_terms(path: Path) -> dict[str, list[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("categories"), dict):
        raise ValueError("Medical dictionary must contain a categories object")
    categories = data["categories"]
    if not isinstance(categories.get("critical_terms"), dict):
        raise ValueError("Medical dictionary is missing critical_terms category")
    terms_by_category: dict[str, list[str]] = {}
    for category, definition in categories.items():
        if not isinstance(definition, dict) or not isinstance(definition.get("terms"), list):
            raise ValueError(f"Dictionary category {category!r} must contain a terms list")
        if not all(isinstance(term, str) and term.strip() for term in definition["terms"]):
            raise ValueError(f"Dictionary category {category!r} contains invalid terms")
        terms_by_category[category] = definition["terms"]
    return terms_by_category


def load_model_outputs(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    """Load latest attempt per case/model from the flattened inference CSV."""
    required = {
        "case_id",
        "model_name",
        "predicted_transcript",
        "latency_seconds",
        "status_code",
    }
    outputs: dict[tuple[str, str], dict[str, str]] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(
                f"Model output CSV must contain columns: {', '.join(sorted(required))}"
            )
        for line_number, row in enumerate(reader, start=2):
            case_id = row.get("case_id", "").strip()
            model_name = row.get("model_name", "").strip()
            if not case_id or not model_name:
                raise ValueError(f"Model output CSV has empty case/model at row {line_number}")
            if row.get("latency_seconds", "").strip():
                try:
                    latency = float(row["latency_seconds"])
                except ValueError as error:
                    raise ValueError(
                        f"Invalid latency at {path}:{line_number}"
                    ) from error
                if latency < 0:
                    raise ValueError(f"Negative latency at {path}:{line_number}")
            outputs[(case_id, model_name)] = row
    return outputs


def load_inputs(
    manifest_path: Path,
    dictionary_path: Path,
    outputs_path: Path,
) -> EvaluationInputs:
    references = load_manifest(manifest_path)
    medical_terms = load_medical_terms(dictionary_path)
    outputs = load_model_outputs(outputs_path)

    unknown_cases = sorted({case_id for case_id, _ in outputs} - set(references))
    if unknown_cases:
        raise ValueError(f"Model outputs contain unknown case IDs: {', '.join(unknown_cases[:10])}")
    unknown_models = sorted(
        {model_name for _, model_name in outputs}
        - set(MODEL_NAMES)
    )
    if unknown_models:
        raise ValueError(f"Unknown model names in output CSV: {', '.join(unknown_models)}")
    return EvaluationInputs(references, medical_terms, outputs)


def _reference_verified(reference_row: dict[str, str]) -> bool:
    status = reference_row.get("reference_review_status", "").strip().casefold()
    evidence = reference_row.get("reference_review_evidence", "").strip()
    audio_status = reference_row.get("audio_presence_status", "").strip().casefold()
    audio_evidence = reference_row.get("audio_presence_evidence_reference", "").strip()
    checksum_evidence = reference_row.get("audio_checksum_evidence_reference", "").strip()
    audio_checksum = reference_row.get("audio_checksum_sha256", "").strip().casefold()
    legacy_flag = reference_row.get("reference_verified", "").strip().casefold()
    return (
        status == "verified_against_audio"
        and bool(evidence)
        and audio_status == "verified_present"
        and bool(audio_evidence)
        and bool(checksum_evidence)
        and re.fullmatch(r"[0-9a-f]{64}", audio_checksum) is not None
        and legacy_flag not in {"false", "0", "no"}
    )


def _mean(values: Sequence[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def evaluate_model(
    model_name: str,
    references: dict[str, dict[str, str]],
    medical_terms: dict[str, list[str]],
    outputs: dict[tuple[str, str], dict[str, str]],
) -> dict[str, object]:
    selected = {
        case_id: output
        for (case_id, output_model), output in outputs.items()
        if output_model == model_name and case_id in references
    }
    live_outputs = [
        output
        for output in selected.values()
        if output.get("status_code", "").strip() in LIVE_SUCCESS_STATUSES
        and output.get("predicted_transcript", "").strip()
    ]
    mock_outputs = [
        output
        for output in selected.values()
        if output.get("status_code", "").strip() == "MOCK"
        and output.get("predicted_transcript", "").strip()
    ]
    failed_count = sum(
        output.get("status_code", "").strip() not in SUCCESS_STATUSES
        or not output.get("predicted_transcript", "").strip()
        for output in selected.values()
    )

    wer_values: list[float] = []
    recall_values: list[float] = []
    critical_misses = 0
    critical_term_count = 0
    eligible_reference_verified = 0

    for output in live_outputs:
        case_id = output["case_id"].strip()
        reference_row = references[case_id]
        reference = reference_row.get("reference_transcript", "").strip()
        hypothesis = output["predicted_transcript"].strip()
        if not reference:
            continue
        if _reference_verified(reference_row):
            eligible_reference_verified += 1
        wer_values.append(calculate_wer(reference, hypothesis))

        target_value = (
            reference_row.get("target_terms", "").strip()
            or reference_row.get("focus_terms", "").strip()
        )
        recall, _, _ = calculate_medical_term_recall(
            reference,
            hypothesis,
            parse_terms(target_value),
        )
        if recall is not None:
            recall_values.append(recall)

        reference_critical_terms = [
            term
            for term in medical_terms.get("critical_terms", [])
            if contains_term(reference, term)
        ]
        critical_term_count += len(reference_critical_terms)
        critical_misses += sum(
            not contains_term(hypothesis, term) for term in reference_critical_terms
        )

    live_latencies = [
        float(output["latency_seconds"])
        for output in live_outputs
        if output.get("latency_seconds", "").strip()
    ]
    mock_latencies = [
        float(output["latency_seconds"])
        for output in mock_outputs
        if output.get("latency_seconds", "").strip()
    ]
    if live_outputs and mock_outputs:
        latency_source = "measured_live_mean_with_mock_latency_separate"
    elif live_outputs:
        latency_source = "measured_live_wall_clock"
    elif mock_outputs:
        latency_source = "simulated_mock_only"
    else:
        latency_source = "unavailable"

    if not selected:
        evaluation_status = "no_outputs"
    elif not live_outputs and mock_outputs:
        evaluation_status = "mock_only_accuracy_not_scored"
    elif live_outputs and mock_outputs:
        evaluation_status = "provisional_live_metrics_mixed_with_mock"
    elif eligible_reference_verified == len(live_outputs):
        evaluation_status = "live_metrics_verified_references"
    else:
        evaluation_status = "provisional_live_metrics_unverified_references"

    return {
        "model_name": model_name,
        "evaluation_status": evaluation_status,
        "case_count": len(selected),
        "live_success_count": len(live_outputs),
        "mock_success_count": len(mock_outputs),
        "failed_case_count": failed_count,
        "mean_wer": _mean(wer_values),
        "mean_medical_term_recall": _mean(recall_values),
        "critical_term_miss_rate": (
            critical_misses / critical_term_count if critical_term_count else None
        ),
        "critical_term_misses": critical_misses,
        "critical_term_count": critical_term_count,
        "mean_latency_seconds": _mean(live_latencies),
        "mean_simulated_latency_seconds": _mean(mock_latencies),
        "latency_source": latency_source,
    }


def evaluate(inputs: EvaluationInputs) -> list[dict[str, object]]:
    return [
        evaluate_model(
            model_name,
            inputs.references,
            inputs.medical_terms,
            inputs.outputs,
        )
        for model_name in MODEL_NAMES
    ]


def write_results(path: Path, rows: Sequence[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: (
                        f"{value:.6f}"
                        if isinstance(value, float)
                        else value
                    )
                    for key, value in row.items()
                }
            )


def run_evaluation(
    manifest_path: Path,
    dictionary_path: Path,
    outputs_path: Path,
    results_path: Path,
    output: TextIO = sys.stdout,
) -> int:
    inputs = load_inputs(manifest_path, dictionary_path, outputs_path)
    results = evaluate(inputs)
    write_results(results_path, results)
    for row in results:
        print(
            f"{row['model_name']}: status={row['evaluation_status']}, "
            f"live={row['live_success_count']}, mock={row['mock_success_count']}, "
            f"failed={row['failed_case_count']}",
            file=output,
        )
    print(f"Evaluation summary written to {results_path}", file=output)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate benchmark model outputs and write aggregate metrics."
    )
    root = Path(__file__).resolve().parent
    parser.add_argument(
        "--manifest",
        type=Path,
        default=root / "benchmark" / "metadata" / "BENCHMARK_MANIFEST.csv",
    )
    parser.add_argument(
        "--dictionary",
        type=Path,
        default=root / "dictionaries" / "medical_terms.json",
    )
    parser.add_argument(
        "--outputs",
        type=Path,
        default=root / "results" / "model_comparisons.csv",
    )
    parser.add_argument(
        "--results",
        type=Path,
        default=root / "results" / "final_evaluation_metrics.csv",
    )
    args = parser.parse_args(argv)
    try:
        return run_evaluation(
            args.manifest.resolve(),
            args.dictionary.resolve(),
            args.outputs.resolve(),
            args.results.resolve(),
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Evaluation failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
