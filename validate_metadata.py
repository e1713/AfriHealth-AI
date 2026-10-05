"""Validate clinical vocabulary dictionary and ground truth metadata files."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, TextIO


EXPECTED_CASE_IDS = {f"CS-{i:02d}" for i in range(1, 101)}
EXPECTED_DICTIONARY_CATEGORIES = {
    "medications",
    "procedures",
    "critical_terms",
    "symptoms",
    "diagnoses",
    "lab_tests",
}
EXPECTED_METADATA_COLUMNS = {
    "case_id",
    "audio_filename",
    "reference_transcript",
    "focus_terms",
    "medical_domain",
    "speaker_id",
    "code_switch_category",
    "reference_review_status",
    "reference_source",
    "audio_presence_status",
    "consent_obtained",
    "de_identified",
    "hosted_inference_approved",
}
EXPECTED_CODE_SWITCH_CATEGORIES = {
    "Mostly Amharic",
    "Balanced Mix",
    "Mostly English Clinical Terms",
}


@dataclass(frozen=True)
class ValidationResult:
    file_path: Path
    is_valid: bool
    errors: list[str]
    warnings: list[str]


def validate_medical_dictionary(path: Path) -> ValidationResult:
    """Validate the clinical vocabulary dictionary structure and content."""
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return ValidationResult(
            file_path=path,
            is_valid=False,
            errors=[f"File not found: {path}"],
            warnings=[],
        )

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError) as error:
        return ValidationResult(
            file_path=path,
            is_valid=False,
            errors=[f"Invalid JSON: {error}"],
            warnings=[],
        )

    if not isinstance(data, dict):
        errors.append("Root element must be a JSON object")
        return ValidationResult(file_path=path, is_valid=False, errors=errors, warnings=warnings)

    if "categories" not in data:
        errors.append("Missing 'categories' key")
    else:
        categories = data["categories"]
        if not isinstance(categories, dict):
            errors.append("'categories' must be a JSON object")
        else:
            found_categories = set(categories.keys())
            if found_categories != EXPECTED_DICTIONARY_CATEGORIES:
                missing = EXPECTED_DICTIONARY_CATEGORIES - found_categories
                extra = found_categories - EXPECTED_DICTIONARY_CATEGORIES
                if missing:
                    errors.append(f"Missing categories: {', '.join(sorted(missing))}")
                if extra:
                    warnings.append(f"Extra categories (not required): {', '.join(sorted(extra))}")

            for category_name, category_obj in categories.items():
                if not isinstance(category_obj, dict):
                    errors.append(f"Category '{category_name}' must be a JSON object")
                    continue
                if "terms" not in category_obj:
                    errors.append(f"Category '{category_name}' missing 'terms' list")
                elif not isinstance(category_obj["terms"], list):
                    errors.append(f"Category '{category_name}' 'terms' must be a list")
                elif len(category_obj["terms"]) == 0:
                    warnings.append(f"Category '{category_name}' has no terms")

    return ValidationResult(
        file_path=path,
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def validate_ground_truth_metadata(path: Path) -> ValidationResult:
    """Validate the authoritative benchmark manifest without asserting gold status."""
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return ValidationResult(
            file_path=path,
            is_valid=False,
            errors=[f"File not found: {path}"],
            warnings=[],
        )

    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                errors.append("CSV has no header row")
                return ValidationResult(file_path=path, is_valid=False, errors=errors, warnings=warnings)

            found_columns = set(reader.fieldnames)
            if not EXPECTED_METADATA_COLUMNS.issubset(found_columns):
                missing = EXPECTED_METADATA_COLUMNS - found_columns
                if missing:
                    errors.append(f"Missing columns: {', '.join(sorted(missing))}")

            rows = list(reader)
    except (csv.Error, ValueError) as error:
        return ValidationResult(
            file_path=path,
            is_valid=False,
            errors=[f"CSV parsing error: {error}"],
            warnings=[],
        )

    if not rows:
        errors.append("CSV has no data rows")
        return ValidationResult(file_path=path, is_valid=False, errors=errors, warnings=warnings)

    found_case_ids = set()
    provisional_category_count = 0
    for row_num, row in enumerate(rows, start=2):
        case_id = row.get("case_id", "").strip()
        if not case_id:
            errors.append(f"Row {row_num}: missing or empty case_id")
            continue
        if case_id in found_case_ids:
            errors.append(f"Row {row_num}: duplicate case_id '{case_id}'")
        found_case_ids.add(case_id)
        if case_id not in EXPECTED_CASE_IDS:
            errors.append(f"Row {row_num}: invalid case_id '{case_id}' (expected CS-01 to CS-100)")

        expected_filename = f"{case_id}.wav"
        if row.get("audio_filename", "").strip() != expected_filename:
            errors.append(f"Row {row_num} ({case_id}): audio_filename must be {expected_filename}")
        for column in ("reference_transcript", "focus_terms", "reference_source"):
            if not row.get(column, "").strip():
                errors.append(f"Row {row_num} ({case_id}): missing {column}")
        if row.get("code_switch_category", "").strip() not in EXPECTED_CODE_SWITCH_CATEGORIES:
            errors.append(f"Row {row_num} ({case_id}): invalid code_switch_category")
        if not row.get("reference_review_status", "").strip():
            errors.append(f"Row {row_num} ({case_id}): missing reference_review_status")

        category_status = row.get("code_switch_annotation_status", "").casefold()
        if "provisional" in category_status:
            provisional_category_count += 1

    missing_case_ids = EXPECTED_CASE_IDS - found_case_ids
    if missing_case_ids:
        errors.append(f"Missing case IDs: {', '.join(sorted(missing_case_ids)[:10])}{'...' if len(missing_case_ids) > 10 else ''}")
    if provisional_category_count:
        warnings.append(
            f"{provisional_category_count} case(s) have provisional code-switch categories"
        )

    return ValidationResult(
        file_path=path,
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def run_validation(
    dictionary_path: Path,
    metadata_path: Path,
    output: TextIO = sys.stdout,
) -> int:
    """Run all validations and report results."""
    dict_result = validate_medical_dictionary(dictionary_path)
    meta_result = validate_ground_truth_metadata(metadata_path)

    print("=" * 70, file=output)
    print("Clinical Metadata Validation Report", file=output)
    print("=" * 70, file=output)
    print(file=output)

    for result in [dict_result, meta_result]:
        status = "✓ PASS" if result.is_valid else "✗ FAIL"
        print(f"{status}: {result.file_path.name}", file=output)
        for error in result.errors:
            print(f"  ERROR: {error}", file=output)
        for warning in result.warnings:
            print(f"  WARNING: {warning}", file=output)
        print(file=output)

    if dict_result.is_valid and meta_result.is_valid:
        print("All validations passed.", file=output)
        return 0
    else:
        print("One or more validations failed.", file=output)
        return 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the medical dictionary and authoritative benchmark manifest."
    )
    parser.add_argument(
        "--dictionary",
        type=Path,
        default=Path(__file__).resolve().parent / "dictionaries" / "medical_terms.json",
        help="Path to the medical vocabulary dictionary JSON file.",
    )
    parser.add_argument(
        "--metadata",
        type=Path,
        default=Path(__file__).resolve().parent
        / "benchmark"
        / "metadata"
        / "BENCHMARK_MANIFEST.csv",
        help="Path to the authoritative benchmark manifest CSV file.",
    )
    args = parser.parse_args(argv)
    return run_validation(args.dictionary.resolve(), args.metadata.resolve())


if __name__ == "__main__":
    sys.exit(main())
