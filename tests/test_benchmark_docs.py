import csv
import json
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = REPOSITORY_ROOT / "benchmark"
EXPECTED_CASE_IDS = [f"CS-{number:02d}" for number in range(1, 101)]


class BenchmarkDocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (BENCHMARK_ROOT / "metadata" / "BENCHMARK_MANIFEST.csv").open(
            encoding="utf-8",
            newline="",
        ) as manifest_file:
            cls.manifest = list(csv.DictReader(manifest_file))
        cls.manifest_fields = set(cls.manifest[0]) if cls.manifest else set()
        cls.entity_schema = json.loads(
            (BENCHMARK_ROOT / "schemas" / "CLINICAL_ENTITY_SCHEMA.json").read_text(
                encoding="utf-8"
            )
        )

    def test_master_manifest_has_all_unique_case_ids_and_source_text(self):
        self.assertEqual(len(self.manifest), 100)
        self.assertEqual([row["case_id"] for row in self.manifest], EXPECTED_CASE_IDS)
        for row in self.manifest:
            with self.subTest(case_id=row["case_id"]):
                self.assertEqual(row["audio_filename"], f'{row["case_id"]}.wav')
                self.assertTrue(row["reference_transcript"])
                self.assertTrue(row["focus_terms"])
                self.assertIn("Google Docs export", row["reference_source"])
                self.assertEqual(
                    row["reference_review_status"],
                    "verified_against_audio",
                )

    def test_unprovided_domains_and_speakers_are_not_fabricated(self):
        self.assertIn("medical_domain", self.manifest_fields)
        self.assertIn("speaker_id", self.manifest_fields)
        self.assertIn("hosted_inference_approved", self.manifest_fields)
        for row in self.manifest:
            self.assertEqual(row["medical_domain"], "")
            self.assertEqual(
                row["medical_domain_status"],
                "not_provided_in_accessible_source",
            )
            self.assertEqual(row["speaker_id"], "")
            self.assertEqual(
                row["speaker_assignment_status"],
                "not_provided_in_accessible_source",
            )
            self.assertEqual(row["consent_obtained"], "false")
            self.assertEqual(row["de_identified"], "false")
            self.assertEqual(row["hosted_inference_approved"], "false")

    def test_switch_categories_are_explicitly_provisional(self):
        valid_categories = {
            "Mostly Amharic",
            "Balanced Mix",
            "Mostly English Clinical Terms",
        }
        for row in self.manifest:
            self.assertIn(row["code_switch_category"], valid_categories)
            self.assertEqual(
                row["code_switch_annotation_status"],
                "provisional_script_share_estimate_requires_human_confirmation",
            )

    def test_entity_schema_covers_requested_clinical_categories(self):
        entity_types = set(
            self.entity_schema["$defs"]["entity"]["properties"]["entity_type"]["enum"]
        )
        self.assertEqual(
            entity_types,
            {
                "symptom",
                "diagnosis",
                "medication",
                "procedure",
                "lab_test",
                "vital_sign",
            },
        )
        self.assertIn("start_char", self.entity_schema["$defs"]["entity"]["required"])
        self.assertIn("criticality", self.entity_schema["$defs"]["entity"]["required"])

    def test_all_requested_benchmark_documents_exist(self):
        expected_paths = (
            "BENCHMARK_PROTOCOL.md",
            "DATASET_CARD.md",
            "ANNOTATION_GUIDELINES.md",
            "EVALUATION_METRICS.md",
            "REPRODUCIBILITY_GUIDE.md",
            "BENCHMARK_LIMITATIONS.md",
            "SCORING_RUBRIC_ALIGNMENT.md",
            "RESULTS_TEMPLATE.md",
            "MODEL_RECOMMENDATION_TEMPLATE.md",
            "metadata/SPEAKER_METADATA.md",
            "schemas/CLINICAL_ENTITY_SCHEMA.json",
        )
        for relative_path in expected_paths:
            with self.subTest(path=relative_path):
                self.assertTrue((BENCHMARK_ROOT / relative_path).is_file())

    def test_ceas_formula_and_availability_gates_are_documented(self):
        metrics = (BENCHMARK_ROOT / "EVALUATION_METRICS.md").read_text(
            encoding="utf-8"
        )
        alignment = (BENCHMARK_ROOT / "SCORING_RUBRIC_ALIGNMENT.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Clinical Equity-Adjusted ASR Score (CEAS)", metrics)
        self.assertIn("0.50 * A_overall", metrics)
        self.assertIn("A_speaker_robustness", metrics)
        self.assertIn("A_codeswitch_consistency", metrics)
        self.assertIn("CEAS is currently unavailable", metrics)
        self.assertIn("CEAS", alignment.split("| Responsible AI |", 1)[1])


if __name__ == "__main__":
    unittest.main()
