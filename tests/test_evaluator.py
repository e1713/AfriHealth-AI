import csv
import json
import tempfile
import unittest
from pathlib import Path

from evaluator import (
    MODEL_NAMES,
    calculate_medical_term_recall,
    calculate_wer,
    contains_term,
    evaluate,
    load_inputs,
    run_evaluation,
)


class EvaluatorMetricTests(unittest.TestCase):
    def test_wer_normalizes_case_and_punctuation(self):
        self.assertEqual(calculate_wer("Fever, and cough!", "fever and cough."), 0.0)

    def test_wer_counts_substitution_deletion_and_insertion(self):
        self.assertAlmostEqual(calculate_wer("a b c", "a x"), 2 / 3)

    def test_wer_handles_empty_reference(self):
        self.assertEqual(calculate_wer("", ""), 0.0)
        self.assertEqual(calculate_wer("", "extra words"), 1.0)

    def test_term_matching_is_case_and_punctuation_insensitive_and_token_bounded(self):
        self.assertTrue(contains_term("Start METFORMIN 500mg, BID.", "Metformin 500mg"))
        self.assertFalse(contains_term("patient has feverish feeling", "fever"))

    def test_medical_term_recall_excludes_terms_absent_from_reference(self):
        recall, matched, eligible = calculate_medical_term_recall(
            "Patient has fever and cough.",
            "Patient has fever.",
            ["fever", "cough", "stroke"],
        )
        self.assertEqual(recall, 0.5)
        self.assertEqual(matched, 1)
        self.assertEqual(eligible, 2)

    def test_term_recall_without_reference_terms_is_not_scored(self):
        self.assertEqual(
            calculate_medical_term_recall("no relevant terms", "fever", ["stroke"]),
            (None, 0, 0),
        )


class EvaluatorIntegrationTests(unittest.TestCase):
    def create_inputs(self, root: Path, status: str = "200") -> tuple[Path, Path, Path]:
        manifest_path = root / "manifest.csv"
        dictionary_path = root / "medical_terms.json"
        outputs_path = root / "model_comparisons.csv"

        with manifest_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=(
                    "case_id",
                    "reference_transcript",
                    "focus_terms",
                    "reference_review_status",
                ),
            )
            writer.writeheader()
            writer.writerow(
                {
                    "case_id": "CS-01",
                    "reference_transcript": "Patient has fever and sepsis.",
                    "focus_terms": "fever; sepsis",
                    "reference_review_status": "source_corpus_text_not_independently_audio_verified",
                }
            )

        dictionary_path.write_text(
            json.dumps(
                {
                    "categories": {
                        "critical_terms": {
                            "terms": ["Sepsis", "Stroke", "Hemorrhage"]
                        }
                    }
                }
            ),
            encoding="utf-8",
        )

        with outputs_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=(
                    "case_id",
                    "model_name",
                    "predicted_transcript",
                    "latency_seconds",
                    "status_code",
                ),
            )
            writer.writeheader()
            writer.writerow(
                {
                    "case_id": "CS-01",
                    "model_name": "Sahara",
                    "predicted_transcript": (
                        "MOCK TRANSCRIPT ONLY: Amharic-English clinical speech sample"
                        if status == "MOCK"
                        else "Patient has fever."
                    ),
                    "latency_seconds": "1.25",
                    "status_code": status,
                }
            )
        return manifest_path, dictionary_path, outputs_path

    def test_mock_outputs_do_not_receive_accuracy_scores(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            manifest, dictionary, outputs = self.create_inputs(root, status="MOCK")
            inputs = load_inputs(manifest, dictionary, outputs)
            results = {row["model_name"]: row for row in evaluate(inputs)}

            sahara = results["Sahara"]
            self.assertEqual(sahara["evaluation_status"], "mock_only_accuracy_not_scored")
            self.assertIsNone(sahara["mean_wer"])
            self.assertIsNone(sahara["mean_medical_term_recall"])
            self.assertEqual(sahara["mean_latency_seconds"], None)
            self.assertEqual(sahara["mean_simulated_latency_seconds"], 1.25)
            self.assertEqual(results["Gemini"]["evaluation_status"], "no_outputs")

    def test_live_outputs_are_labeled_provisional_and_critical_miss_counted(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            manifest, dictionary, outputs = self.create_inputs(root, status="200")
            inputs = load_inputs(manifest, dictionary, outputs)
            results = {row["model_name"]: row for row in evaluate(inputs)}

            sahara = results["Sahara"]
            self.assertEqual(
                sahara["evaluation_status"],
                "provisional_live_metrics_unverified_references",
            )
            self.assertAlmostEqual(sahara["mean_wer"], 0.4)
            self.assertEqual(sahara["mean_medical_term_recall"], 0.5)
            self.assertEqual(sahara["critical_term_misses"], 1)
            self.assertEqual(sahara["critical_term_count"], 1)
            self.assertEqual(sahara["critical_term_miss_rate"], 1.0)
            self.assertEqual(sahara["mean_latency_seconds"], 1.25)

    def test_evaluation_writes_six_model_rows(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            manifest, dictionary, outputs = self.create_inputs(root, status="MOCK")
            output_path = root / "results" / "metrics.csv"

            result = run_evaluation(manifest, dictionary, outputs, output_path)

            self.assertEqual(result, 0)
            with output_path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual([row["model_name"] for row in rows], list(MODEL_NAMES))
            self.assertEqual(len(rows), 6)

    def test_latest_attempt_supersedes_an_earlier_failure(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            manifest, dictionary, outputs = self.create_inputs(root, status="MOCK_ERROR")
            with outputs.open("a", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(
                    (
                        "CS-01",
                        "Sahara",
                        "MOCK TRANSCRIPT ONLY: successful retry",
                        "1.1",
                        "MOCK",
                    )
                )

            inputs = load_inputs(manifest, dictionary, outputs)
            results = {row["model_name"]: row for row in evaluate(inputs)}

            self.assertEqual(results["Sahara"]["mock_success_count"], 1)
            self.assertEqual(results["Sahara"]["failed_case_count"], 0)


if __name__ == "__main__":
    unittest.main()
