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
            ["100 case(s) have provisional code-switch categories"],
        )

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
                "reference_source",
                "audio_presence_status",
                "consent_obtained",
                "de_identified",
                "hosted_inference_approved",
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
                "reference_source": "test",
                "audio_presence_status": "not_verified",
                "consent_obtained": "false",
                "de_identified": "false",
                "hosted_inference_approved": "false",
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
                "reference_source",
                "audio_presence_status",
                "consent_obtained",
                "de_identified",
                "hosted_inference_approved",
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
