import csv
import json
import tempfile
import unittest
from pathlib import Path

from validate_metadata import (
    EXPECTED_DICTIONARY_CATEGORIES,
    validate_ground_truth_metadata,
    validate_medical_dictionary,
)
from apply_governance_flags import apply_governance_flags


class MedicalDictionaryTests(unittest.TestCase):
    def test_valid_dictionary_structure_passes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            dictionary_path = Path(temporary_directory) / "medical_terms.json"
            data = {
                "categories": {
                    category: {"terms": [f"{category}_term"]}
                    for category in EXPECTED_DICTIONARY_CATEGORIES
                }
            }
            dictionary_path.write_text(json.dumps(data), encoding="utf-8")

            result = validate_medical_dictionary(dictionary_path)

            self.assertTrue(result.is_valid)
            self.assertEqual(result.errors, [])

    def test_missing_category_is_error(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            dictionary_path = Path(temporary_directory) / "medical_terms.json"
            dictionary_path.write_text(
                json.dumps({"categories": {"medications": {"terms": ["drug"]}}}),
                encoding="utf-8",
            )

            result = validate_medical_dictionary(dictionary_path)

            self.assertFalse(result.is_valid)
            self.assertTrue(any("Missing categories" in error for error in result.errors))

    def test_invalid_json_is_error(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            dictionary_path = Path(temporary_directory) / "medical_terms.json"
            dictionary_path.write_text("{ invalid json", encoding="utf-8")

            result = validate_medical_dictionary(dictionary_path)

            self.assertFalse(result.is_valid)
            self.assertTrue(any("Invalid JSON" in error for error in result.errors))

    def test_empty_terms_list_is_warning(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            dictionary_path = Path(temporary_directory) / "medical_terms.json"
            data = {
                "categories": {
                    category: {"terms": [] if category == "medications" else ["term"]}
                    for category in EXPECTED_DICTIONARY_CATEGORIES
                }
            }
            dictionary_path.write_text(json.dumps(data), encoding="utf-8")

            result = validate_medical_dictionary(dictionary_path)

            self.assertTrue(result.is_valid)
            self.assertTrue(any("no terms" in warning for warning in result.warnings))


class MasterManifestValidationTests(unittest.TestCase):
    def test_authoritative_manifest_passes_validation(self):
        manifest_path = (
            Path(__file__).resolve().parents[1]
            / "benchmark"
            / "metadata"
            / "BENCHMARK_MANIFEST.csv"
        )

        result = validate_ground_truth_metadata(manifest_path)

        self.assertTrue(result.is_valid, result.errors)
        self.assertEqual(
            result.warnings,
            [
                "100 case(s) have provisional code-switch categories",
                "100 case(s) lack documented affirmative consent",
                "100 case(s) lack documented de-identification",
                "100 case(s) lack documented hosted-inference approval",
                "100 speaker assignment(s) remain pending independent review",
                "100 case(s) have no named reviewer recorded",
                "100 case(s) have no review date recorded",
            ],
        )

    def test_missing_dataset_version_is_error(self):
        self.assert_manifest_status_rejected(
            {"dataset_version": ""},
            "missing dataset_version",
        )

    def test_missing_reviewer_and_review_date_are_warnings(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            manifest_path = root / "BENCHMARK_MANIFEST.csv"
            source_path = root / "GROUND_TRUTH_SOURCE.csv"
            source_metadata = Path(__file__).resolve().parents[1] / "benchmark" / "metadata"
            for filename, destination in (
                ("BENCHMARK_MANIFEST.csv", manifest_path),
                ("GROUND_TRUTH_SOURCE.csv", source_path),
            ):
                with (source_metadata / filename).open(encoding="utf-8", newline="") as source_file:
                    reader = csv.DictReader(source_file)
                    fields = reader.fieldnames
                    rows = list(reader)
                for row in rows:
                    row["reviewer"] = "Test Reviewer"
                    row["review_date"] = "2026-10-07"
                if filename == "BENCHMARK_MANIFEST.csv":
                    rows[0]["reviewer"] = ""
                    rows[0]["review_date"] = ""
                else:
                    rows[0]["reviewer"] = ""
                    rows[0]["review_date"] = ""
                with destination.open("w", encoding="utf-8", newline="") as output_file:
                    writer = csv.DictWriter(output_file, fieldnames=fields)
                    writer.writeheader()
                    writer.writerows(rows)

            result = validate_ground_truth_metadata(manifest_path)

            self.assertTrue(result.is_valid, result.errors)
            self.assertIn("1 case(s) have no named reviewer recorded", result.warnings)
            self.assertIn("1 case(s) have no review date recorded", result.warnings)

    def test_manifest_transcript_mismatch_with_canonical_source_is_error(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            manifest_path = root / "BENCHMARK_MANIFEST.csv"
            source_path = root / "GROUND_TRUTH_SOURCE.csv"
            repository_metadata = Path(__file__).resolve().parents[1] / "benchmark" / "metadata"
            for filename, destination in (
                ("BENCHMARK_MANIFEST.csv", manifest_path),
                ("GROUND_TRUTH_SOURCE.csv", source_path),
            ):
                with (repository_metadata / filename).open(encoding="utf-8", newline="") as source_file:
                    reader = csv.DictReader(source_file)
                    fields = reader.fieldnames
                    rows = list(reader)
                if filename == "BENCHMARK_MANIFEST.csv":
                    rows[0]["reference_transcript"] = "changed transcript"
                with destination.open("w", encoding="utf-8", newline="") as output_file:
                    writer = csv.DictWriter(output_file, fieldnames=fields)
                    writer.writeheader()
                    writer.writerows(rows)

            result = validate_ground_truth_metadata(manifest_path)

            self.assertFalse(result.is_valid)
            self.assertTrue(
                any("does not match canonical source normalized_transcript" in error for error in result.errors),
                result.errors,
            )

    def test_invalid_canonical_source_review_status_is_error(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            manifest_path = root / "BENCHMARK_MANIFEST.csv"
            source_path = root / "GROUND_TRUTH_SOURCE.csv"
            repository_metadata = Path(__file__).resolve().parents[1] / "benchmark" / "metadata"
            for filename, destination in (
                ("BENCHMARK_MANIFEST.csv", manifest_path),
                ("GROUND_TRUTH_SOURCE.csv", source_path),
            ):
                with (repository_metadata / filename).open(encoding="utf-8", newline="") as source_file:
                    reader = csv.DictReader(source_file)
                    fields = reader.fieldnames
                    rows = list(reader)
                if filename == "GROUND_TRUTH_SOURCE.csv":
                    rows[0]["review_status"] = "verified_by_import"
                with destination.open("w", encoding="utf-8", newline="") as output_file:
                    writer = csv.DictWriter(output_file, fieldnames=fields)
                    writer.writeheader()
                    writer.writerows(rows)

            result = validate_ground_truth_metadata(manifest_path)

            self.assertFalse(result.is_valid)
            self.assertTrue(
                any("invalid review_status 'verified_by_import'" in error for error in result.errors),
                result.errors,
            )

    def test_verified_reference_requires_evidence(self):
        self.assert_manifest_status_rejected(
            {"reference_review_status": "verified_against_audio"},
            "requires reference_review_evidence",
        )

    def test_verified_reference_requires_verified_audio_presence(self):
        self.assert_manifest_status_rejected(
            {
                "reference_review_status": "verified_against_audio",
                "reference_review_evidence": "review://CS-01",
            },
            "verified_against_audio requires verified audio presence, evidence, and checksum",
        )

    def test_unrecognized_code_switch_status_is_error(self):
        self.assert_manifest_status_rejected(
            {"code_switch_annotation_status": "verified_by_import"},
            "invalid code_switch_annotation_status",
        )

    def test_adjudicated_code_switch_status_requires_evidence(self):
        self.assert_manifest_status_rejected(
            {"code_switch_annotation_status": "adjudicated"},
            "verified code-switch annotation requires evidence",
        )

    def test_affirmative_consent_requires_evidence(self):
        self.assert_manifest_status_rejected(
            {"consent_obtained": "true"},
            "consent_obtained=true requires its evidence reference",
        )

    def test_hosted_approval_requires_all_governance_evidence(self):
        self.assert_manifest_status_rejected(
            {
                "consent_obtained": "true",
                "de_identified": "true",
                "hosted_inference_approved": "true",
                "audio_presence_status": "verified_present",
                "audio_presence_evidence_reference": "provenance://CS-01",
                "audio_checksum_evidence_reference": "checksum://CS-01",
                "audio_checksum_sha256": "a" * 64,
            },
            "hosted_inference_approved=true requires its evidence reference",
        )

    def assert_manifest_status_rejected(self, updates, expected_error):
        with tempfile.TemporaryDirectory() as temporary_directory:
            manifest_path = Path(temporary_directory) / "manifest.csv"
            with (Path(__file__).resolve().parents[1] / "benchmark" / "metadata" / "BENCHMARK_MANIFEST.csv").open(
                encoding="utf-8", newline=""
            ) as source:
                reader = csv.DictReader(source)
                fields = reader.fieldnames
                rows = list(reader)
            rows[0].update(
                {
                    "reference_review_status": "pending_review",
                    "reference_review_evidence": "",
                    "audio_presence_status": "file_present_provenance_unverified",
                    "audio_presence_evidence_reference": "",
                    "audio_checksum_evidence_reference": "",
                    "audio_checksum_sha256": "",
                    "consent_obtained": "unknown",
                    "consent_evidence_reference": "",
                    "de_identified": "unknown",
                    "de_identification_evidence_reference": "",
                    "hosted_inference_approved": "unknown",
                    "hosted_inference_approval_evidence_reference": "",
                    "speaker_assignment_status": "pending_review",
                    "code_switch_annotation_status": "provisional_script_share_estimate_requires_human_confirmation",
                }
            )
            rows[0].update(updates)
            with manifest_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)

            result = validate_ground_truth_metadata(manifest_path)

            self.assertFalse(result.is_valid)
            self.assertTrue(any(expected_error in error for error in result.errors), result.errors)

    def test_governance_flags_reject_positive_claim_without_evidence(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            manifest_path = root / "manifest.csv"
            flags_path = root / "approvals.csv"
            fields = ("case_id", "consent_obtained", "de_identified", "hosted_inference_approved")
            with manifest_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerow({"case_id": "CS-01"})
            with flags_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerow({"case_id": "CS-01", "consent_obtained": "true"})

            with self.assertRaisesRegex(ValueError, "consent_obtained=true requires consent_evidence_reference"):
                apply_governance_flags(manifest_path, flags_path)

    def test_governance_flags_preserve_unknown_and_evidence(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            manifest_path = root / "manifest.csv"
            flags_path = root / "approvals.csv"
            fields = ("case_id", "consent_obtained", "de_identified", "hosted_inference_approved")
            evidence_fields = (
                "consent_evidence_reference",
                "de_identification_evidence_reference",
                "hosted_inference_approval_evidence_reference",
            )
            with manifest_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerow({"case_id": "CS-01"})
            with flags_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=("case_id", *fields[1:], *evidence_fields))
                writer.writeheader()
                writer.writerow({"case_id": "CS-01", "consent_obtained": "unknown"})

            apply_governance_flags(manifest_path, flags_path)

            with manifest_path.open(encoding="utf-8", newline="") as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(row["consent_obtained"], "unknown")
            self.assertEqual(row["consent_evidence_reference"], "")

    def test_duplicate_case_id_is_error(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            manifest_path = Path(temporary_directory) / "manifest.csv"
            fields = (
                "case_id",
                "audio_filename",
                "reference_transcript",
                "focus_terms",
                "medical_domain",
                "speaker_id",
                "code_switch_category",
                "reference_review_status",
                "reference_review_evidence",
                "reference_source",
                "audio_presence_status",
                "audio_presence_evidence_reference",
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
            )
            row = {
                "case_id": "CS-01",
                "audio_filename": "CS-01.wav",
                "reference_transcript": "Fever",
                "focus_terms": "Fever",
                "medical_domain": "",
                "speaker_id": "",
                "code_switch_category": "Balanced Mix",
                "reference_review_status": "pending",
                "reference_review_evidence": "",
                "reference_source": "test",
                "audio_presence_status": "not_verified",
                "audio_presence_evidence_reference": "",
                "consent_obtained": "false",
                "consent_evidence_reference": "",
                "de_identified": "false",
                "de_identification_evidence_reference": "",
                "hosted_inference_approved": "false",
                "hosted_inference_approval_evidence_reference": "",
                "speaker_assignment_status": "not_provided_in_accessible_source",
                "speaker_assignment_evidence": "",
                "code_switch_annotation_status": "provisional",
                "code_switch_annotation_evidence": "",
            }
            with manifest_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerow(row)
                writer.writerow(row)

            result = validate_ground_truth_metadata(manifest_path)

            self.assertFalse(result.is_valid)
            self.assertTrue(any("duplicate case_id" in error for error in result.errors))

    def test_missing_case_ids_is_error(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            manifest_path = Path(temporary_directory) / "manifest.csv"
            fields = (
                "case_id",
                "audio_filename",
                "reference_transcript",
                "focus_terms",
                "medical_domain",
                "speaker_id",
                "code_switch_category",
                "reference_review_status",
                "reference_review_evidence",
                "reference_source",
                "audio_presence_status",
                "audio_presence_evidence_reference",
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
            )
            with manifest_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerow({
                    "case_id": "CS-01",
                    "audio_filename": "CS-01.wav",
                    "reference_transcript": "Fever",
                    "focus_terms": "Fever",
                    "code_switch_category": "Mostly Amharic",
                    "reference_review_status": "pending",
                    "reference_source": "test",
                })

            result = validate_ground_truth_metadata(manifest_path)

            self.assertFalse(result.is_valid)
            self.assertTrue(any("Missing case IDs" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
