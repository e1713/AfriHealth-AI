"""Validate clinical vocabulary dictionary and ground truth metadata files."""

from __future__ import annotations

import argparse
import csv
import json
import re
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
    "language_mix",
    "code_switch_category",
    "reference_review_status",
    "reference_review_evidence",
    "reviewer",
    "review_date",
    "verification_method",
    "verification_notes",
    "dataset_version",
    "prepared_by",
    "reference_source",
    "audio_presence_status",
    "audio_presence_evidence_reference",
    "audio_checksum_evidence_reference",
    "audio_checksum_sha256",
    "consent_obtained",
    "consent_evidence_reference",
    "de_identified",
    "de_identification_evidence_reference",
    "hosted_inference_approved",
    "hosted_inference_approval_evidence_reference",
    "speaker_assignment_status",
    "speaker_assignment_evidence",
    "code_switch_annotation_status",
    "code_switch_annotation_evidence",
}
EXPECTED_CODE_SWITCH_CATEGORIES = {
    "Mostly Amharic",
    "Balanced Mix",
    "Mostly English Clinical Terms",
}
REVIEW_STATUSES = {
    "not_reviewed",
    "pending_review",
    "partially_reviewed",
    "verified_against_audio",
}
SOURCE_REVIEW_STATUSES = {"verified", "pending_review", "rejected"}
CODE_SWITCH_STATUSES = {
    "provisional_script_share_estimate_requires_human_confirmation",
    "pending_review",
    "partially_reviewed",
    "verified_from_audio",
    "adjudicated",
}
VERIFIED_CODE_SWITCH_STATUSES = {"verified_from_audio", "adjudicated"}
BOOLEAN_OR_UNKNOWN_VALUES = {"true", "false", "unknown"}
TRUE_VALUES = {"true", "1", "yes"}


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

    source_path = path.with_name("GROUND_TRUTH_SOURCE.csv")
    if source_path.is_file():
        try:
            with source_path.open(encoding="utf-8-sig", newline="") as source_file:
                source_reader = csv.DictReader(source_file)
                source_rows = list(source_reader)
                source_fields = set(source_reader.fieldnames or ())
        except (OSError, csv.Error, ValueError) as error:
            errors.append(f"Could not read canonical ground-truth source {source_path}: {error}")
            source_rows = []
            source_fields = set()

        required_source_fields = {
            "case_id",
            "audio_filename",
            "speaker_id",
            "clinical_domain",
            "normalized_transcript",
            "medical_entities",
            "review_status",
            "reviewer",
            "review_date",
            "verification_method",
            "verification_notes",
            "dataset_version",
            "prepared_by",
        }
        missing_source_fields = required_source_fields - source_fields
        if missing_source_fields:
            errors.append(
                f"Canonical source is missing columns: {', '.join(sorted(missing_source_fields))}"
            )

        source_by_id: dict[str, dict[str, str]] = {}
        for source_row_num, source_row in enumerate(source_rows, start=2):
            source_case_id = source_row.get("case_id", "").strip()
            if not source_case_id:
                errors.append(f"Canonical source row {source_row_num}: missing case_id")
            elif source_case_id in source_by_id:
                errors.append(f"Canonical source row {source_row_num}: duplicate case_id '{source_case_id}'")
            else:
                source_by_id[source_case_id] = source_row
            source_review_status = source_row.get("review_status", "").strip().casefold()
            if source_review_status not in SOURCE_REVIEW_STATUSES:
                errors.append(
                    f"Canonical source row {source_row_num} ({source_case_id}): invalid review_status '{source_review_status}'"
                )
            for column in ("normalized_transcript", "audio_filename"):
                if not source_row.get(column, "").strip():
                    errors.append(
                        f"Canonical source row {source_row_num} ({source_case_id}): missing {column}"
                    )

        manifest_by_id = {row.get("case_id", "").strip(): row for row in rows}
        if set(source_by_id) != set(manifest_by_id):
            errors.append(
                "Manifest case IDs do not match canonical ground-truth source IDs "
                f"(source-only: {len(set(source_by_id) - set(manifest_by_id))}; "
                f"manifest-only: {len(set(manifest_by_id) - set(source_by_id))})"
            )

        def normalized(value: str) -> str:
            return " ".join(value.split())

        for case_id in sorted(set(source_by_id) & set(manifest_by_id)):
            source_row = source_by_id[case_id]
            manifest_row = manifest_by_id[case_id]
            source_review = source_row.get("review_status", "").strip().casefold()
            manifest_review = manifest_row.get("reference_review_status", "").strip().casefold()
            if source_review == "verified" and manifest_review != "verified_against_audio":
                errors.append(
                    f"{case_id}: source review_status=verified but manifest reference_review_status is {manifest_review!r}"
                )
            elif source_review != "verified" and manifest_review == "verified_against_audio":
                errors.append(
                    f"{case_id}: manifest claims verified_against_audio but canonical source review_status is {source_review!r}"
                )
            comparisons = (
                ("normalized_transcript", "reference_transcript"),
                ("audio_filename", "audio_filename"),
                ("speaker_id", "speaker_id"),
                ("clinical_domain", "medical_domain"),
                ("medical_entities", "focus_terms"),
                ("reviewer", "reviewer"),
                ("review_date", "review_date"),
                ("verification_method", "verification_method"),
                ("verification_notes", "verification_notes"),
                ("dataset_version", "dataset_version"),
                ("prepared_by", "prepared_by"),
            )
            for source_field, manifest_field in comparisons:
                if normalized(source_row.get(source_field, "")) != normalized(
                    manifest_row.get(manifest_field, "")
                ):
                    errors.append(
                        f"{case_id}: manifest {manifest_field} does not match canonical source {source_field}"
                    )
    else:
        warnings.append(f"Canonical source CSV not found beside manifest: {source_path}")

    found_case_ids = set()
    provisional_category_count = 0
    pending_reference_count = 0
    undocumented_consent_count = 0
    unverified_deidentification_count = 0
    unapproved_hosted_inference_count = 0
    missing_audio_checksum_count = 0
    missing_speaker_count = 0
    pending_speaker_review_count = 0
    missing_reviewer_count = 0
    missing_review_date_count = 0
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
        for column in ("reviewer", "review_date"):
            if not row.get(column, "").strip():
                if column == "reviewer":
                    missing_reviewer_count += 1
                else:
                    missing_review_date_count += 1
        verification_method = row.get("verification_method", "").strip().casefold()
        if verification_method and verification_method not in {"manual_review"}:
            errors.append(
                f"Row {row_num} ({case_id}): unsupported verification_method '{verification_method}'"
            )
        if not row.get("dataset_version", "").strip():
            errors.append(f"Row {row_num} ({case_id}): missing dataset_version")
        if not row.get("audio_filename", "").strip():
            errors.append(f"Row {row_num} ({case_id}): missing audio mapping")
        if row.get("code_switch_category", "").strip() not in EXPECTED_CODE_SWITCH_CATEGORIES:
            errors.append(f"Row {row_num} ({case_id}): invalid code_switch_category")
        review_status = row.get("reference_review_status", "").strip().casefold()
        review_evidence = row.get("reference_review_evidence", "").strip()
        if review_status not in REVIEW_STATUSES:
            errors.append(f"Row {row_num} ({case_id}): invalid reference_review_status '{review_status}'")
        elif review_status in {"verified_against_audio", "partially_reviewed"} and not review_evidence:
            errors.append(
                f"Row {row_num} ({case_id}): {review_status} requires reference_review_evidence"
            )
        if review_status != "verified_against_audio":
            pending_reference_count += 1

        audio_status = row.get("audio_presence_status", "").strip().casefold()
        audio_evidence = row.get("audio_presence_evidence_reference", "").strip()
        checksum_evidence = row.get("audio_checksum_evidence_reference", "").strip()
        audio_checksum = row.get("audio_checksum_sha256", "").strip().casefold()
        if audio_status not in {
            "not_verified_in_workspace",
            "file_present_provenance_unverified",
            "verified_present",
            "missing",
        }:
            errors.append(f"Row {row_num} ({case_id}): invalid audio_presence_status '{audio_status}'")
        if re.fullmatch(r"[0-9a-f]{64}", audio_checksum) is None:
            missing_audio_checksum_count += 1
        if audio_status == "verified_present" and (
            not audio_evidence
            or not checksum_evidence
            or re.fullmatch(r"[0-9a-f]{64}", audio_checksum) is None
        ):
            errors.append(
                f"Row {row_num} ({case_id}): verified_present requires audio evidence and a documented 64-character SHA-256 checksum"
            )
        if review_status == "verified_against_audio" and (
            audio_status != "verified_present"
            or not audio_evidence
            or not checksum_evidence
            or re.fullmatch(r"[0-9a-f]{64}", audio_checksum) is None
        ):
            errors.append(
                f"Row {row_num} ({case_id}): verified_against_audio requires verified audio presence, evidence, and checksum"
            )

        governance_values = {
            "consent_obtained": row.get("consent_obtained", "").strip().casefold(),
            "de_identified": row.get("de_identified", "").strip().casefold(),
            "hosted_inference_approved": row.get("hosted_inference_approved", "").strip().casefold(),
        }
        governance_evidence = {
            "consent_obtained": row.get("consent_evidence_reference", "").strip(),
            "de_identified": row.get("de_identification_evidence_reference", "").strip(),
            "hosted_inference_approved": row.get(
                "hosted_inference_approval_evidence_reference", ""
            ).strip(),
        }
        for field, value in governance_values.items():
            if value not in BOOLEAN_OR_UNKNOWN_VALUES:
                errors.append(f"Row {row_num} ({case_id}): {field} must be true, false, or unknown")
            if value in TRUE_VALUES and not governance_evidence[field]:
                errors.append(f"Row {row_num} ({case_id}): {field}=true requires its evidence reference")
        if governance_values["hosted_inference_approved"] in TRUE_VALUES and any(
            governance_values[field] not in TRUE_VALUES
            for field in ("consent_obtained", "de_identified")
        ):
            errors.append(
                f"Row {row_num} ({case_id}): hosted inference approval requires documented consent and de-identification"
            )
        if governance_values["hosted_inference_approved"] in TRUE_VALUES and (
            audio_status != "verified_present"
            or not checksum_evidence
            or re.fullmatch(r"[0-9a-f]{64}", audio_checksum) is None
        ):
            errors.append(
                f"Row {row_num} ({case_id}): hosted inference approval requires verified audio presence and checksum"
            )
        if governance_values["consent_obtained"] != "true":
            undocumented_consent_count += 1
        if governance_values["de_identified"] != "true":
            unverified_deidentification_count += 1
        if governance_values["hosted_inference_approved"] != "true":
            unapproved_hosted_inference_count += 1

        speaker_status = row.get("speaker_assignment_status", "").strip().casefold()
        speaker_id = row.get("speaker_id", "").strip()
        speaker_evidence = row.get("speaker_assignment_evidence", "").strip()
        if speaker_status not in {"not_provided_in_accessible_source", "pending_review", "assigned_verified"}:
            errors.append(f"Row {row_num} ({case_id}): invalid speaker_assignment_status '{speaker_status}'")
        if speaker_status == "assigned_verified" and (not speaker_id or not speaker_evidence):
            errors.append(
                f"Row {row_num} ({case_id}): assigned_verified requires speaker_id and speaker_assignment_evidence"
            )
        if not speaker_id:
            missing_speaker_count += 1
        if speaker_status != "assigned_verified":
            pending_speaker_review_count += 1

        switch_status = row.get("code_switch_annotation_status", "").strip().casefold()
        if switch_status not in CODE_SWITCH_STATUSES:
            errors.append(f"Row {row_num} ({case_id}): invalid code_switch_annotation_status '{switch_status}'")
        elif switch_status in VERIFIED_CODE_SWITCH_STATUSES and not row.get(
            "code_switch_annotation_evidence", ""
        ).strip():
            errors.append(
                f"Row {row_num} ({case_id}): verified code-switch annotation requires evidence"
            )

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
    if pending_reference_count:
        warnings.append(f"{pending_reference_count} reference(s) are not verified against audio")
    if undocumented_consent_count:
        warnings.append(f"{undocumented_consent_count} case(s) lack documented affirmative consent")
    if unverified_deidentification_count:
        warnings.append(f"{unverified_deidentification_count} case(s) lack documented de-identification")
    if unapproved_hosted_inference_count:
        warnings.append(f"{unapproved_hosted_inference_count} case(s) lack documented hosted-inference approval")
    if missing_audio_checksum_count:
        warnings.append(f"{missing_audio_checksum_count} case(s) lack a valid audio SHA-256 checksum")
    if missing_speaker_count:
        warnings.append(f"{missing_speaker_count} case(s) have no speaker assignment")
    if pending_speaker_review_count:
        warnings.append(
            f"{pending_speaker_review_count} speaker assignment(s) remain pending independent review"
        )
    if missing_reviewer_count:
        warnings.append(f"{missing_reviewer_count} case(s) have no named reviewer recorded")
    if missing_review_date_count:
        warnings.append(f"{missing_review_date_count} case(s) have no review date recorded")

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
