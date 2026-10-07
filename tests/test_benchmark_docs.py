import csv
import json
import tempfile
import unittest
from pathlib import Path

from parse_docx_references import update_manifest


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
                self.assertIn("Google Sheet 1IQOdmAQxuiU2MgAqCAQ91rG-8TIS3UB_", row["reference_source"])
                self.assertEqual(
                    row["reference_review_status"],
                    "verified_against_audio",
                )
                self.assertIn("review_status=verified", row["reference_review_evidence"])
                self.assertEqual(row["audio_presence_status"], "verified_present")
                self.assertRegex(row["audio_checksum_sha256"], r"^[0-9a-f]{64}$")
                self.assertEqual(row["speaker_assignment_status"], "pending_review")
                self.assertEqual(row["reviewer"], "")
                self.assertEqual(row["review_date"], "")
                self.assertEqual(row["verification_method"], "manual_review")
                self.assertTrue(row["verification_notes"])
                self.assertEqual(row["dataset_version"], "v1.0")
                self.assertEqual(row["prepared_by"], "Ermias")

    def test_source_domains_and_pseudonymized_speakers_are_retained(self):
        self.assertIn("medical_domain", self.manifest_fields)
        self.assertIn("speaker_id", self.manifest_fields)
        self.assertIn("hosted_inference_approved", self.manifest_fields)
        for row in self.manifest:
            self.assertTrue(row["medical_domain"])
            self.assertEqual(
                row["medical_domain_status"],
                "provided_in_ground_truth_sheet",
            )
            self.assertRegex(row["speaker_id"], r"^Speaker-\d{2}$")
            self.assertEqual(
                row["speaker_assignment_status"],
                "pending_review",
            )
            self.assertEqual(row["consent_obtained"], "unknown")
            self.assertEqual(row["de_identified"], "unknown")
            self.assertEqual(row["hosted_inference_approved"], "unknown")
            self.assertEqual(row["consent_evidence_reference"], "")
            self.assertEqual(row["hosted_inference_approval_evidence_reference"], "")

    def test_manifest_matches_canonical_spreadsheet_transcripts(self):
        with (BENCHMARK_ROOT / "metadata" / "GROUND_TRUTH_SOURCE.csv").open(
            encoding="utf-8", newline=""
        ) as source_file:
            source = {row["case_id"]: row for row in csv.DictReader(source_file)}
        self.assertEqual(set(source), set(EXPECTED_CASE_IDS))
        for row in self.manifest:
            with self.subTest(case_id=row["case_id"]):
                self.assertEqual(row["reference_transcript"], source[row["case_id"]]["normalized_transcript"])
                self.assertEqual(row["audio_filename"], source[row["case_id"]]["audio_filename"])
                self.assertEqual(row["speaker_id"], source[row["case_id"]]["speaker_id"])
                self.assertEqual(row["medical_domain"], source[row["case_id"]]["clinical_domain"])

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

    def test_importing_source_text_resets_reference_review(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            manifest_path = Path(temporary_directory) / "manifest.csv"
            fields = (
                "case_id",
                "reference_transcript",
                "reference_review_status",
                "reference_review_evidence",
            )
            with manifest_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerow(
                    {
                        "case_id": "CS-01",
                        "reference_transcript": "old",
                        "reference_review_status": "verified_against_audio",
                        "reference_review_evidence": "review://old",
                    }
                )

            updated = update_manifest(manifest_path, {"CS-01": "new source text"})

            with manifest_path.open(encoding="utf-8", newline="") as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(updated, 1)
            self.assertEqual(row["reference_transcript"], "new source text")
            self.assertEqual(row["reference_review_status"], "pending_review")
            self.assertEqual(row["reference_review_evidence"], "")

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
            "metadata/GROUND_TRUTH_SOURCE.csv",
            "metadata/GROUND_TRUTH_SOURCE.xlsx",
            "metadata/SPEAKER_METADATA.md",
            "schemas/CLINICAL_ENTITY_SCHEMA.json",
        )
        for relative_path in expected_paths:
            with self.subTest(path=relative_path):
                self.assertTrue((BENCHMARK_ROOT / relative_path).is_file())
        self.assertTrue((REPOSITORY_ROOT / "METADATA_AUDIT_REPORT.md").is_file())
        self.assertTrue((REPOSITORY_ROOT / "GROUND_TRUTH_COVERAGE_REPORT.md").is_file())
        self.assertTrue((REPOSITORY_ROOT / "GROUND_TRUTH_AUDIT_REPORT.md").is_file())
        for report_name in (
            "GROUND_TRUTH_VERIFICATION_REPORT.md",
            "BENCHMARK_CERTIFICATION_REPORT.md",
            "AUDIO_ALIGNMENT_REPORT.md",
            "SPEAKER_DOMAIN_AUDIT.md",
            "CODESWITCH_READINESS_REPORT.md",
            "BENCHMARK_EXECUTION_READINESS.md",
        ):
            self.assertTrue((REPOSITORY_ROOT / report_name).is_file(), report_name)

    def test_dataset_card_includes_governance_sections(self):
        card = (BENCHMARK_ROOT / "DATASET_CARD.md").read_text(encoding="utf-8")
        for heading in (
            "## Dataset Summary",
            "## Verification Methodology",
            "## Known Limitations",
            "## Bias Considerations",
            "## Recommended Use",
            "## Unsupported Uses",
            "## Benchmark Scope",
        ):
            with self.subTest(heading=heading):
                self.assertIn(heading, card)

    def test_metadata_audit_report_states_current_uncertainties(self):
        report = (REPOSITORY_ROOT / "METADATA_AUDIT_REPORT.md").read_text(encoding="utf-8")
        ground_truth_audit = (REPOSITORY_ROOT / "GROUND_TRUTH_AUDIT_REPORT.md").read_text(encoding="utf-8")
        coverage = (REPOSITORY_ROOT / "GROUND_TRUTH_COVERAGE_REPORT.md").read_text(encoding="utf-8")
        self.assertIn("## Findings", report)
        self.assertIn("## Corrections Made", report)
        self.assertIn("## Current Dataset Status", report)
        self.assertIn("## Remaining Risks", report)
        self.assertIn("unknown", report)
        self.assertIn("pending_review", report)
        self.assertIn("on 19 cases", ground_truth_audit)
        self.assertIn("CS-81", ground_truth_audit)
        self.assertIn("zero current mapping mismatches", coverage)

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
