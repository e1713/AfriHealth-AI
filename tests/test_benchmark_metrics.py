import json
import tempfile
import unittest
from pathlib import Path

import benchmark_suite
from clinical_validation_evaluator import calculate_mwer, contains_term, normalize_clinical_text
from clinical_validation_evaluator import evaluate as evaluate_clinical_results
from evaluator import load_manifest
import run_full_evaluation


class BenchmarkMetricTests(unittest.TestCase):
    def test_entity_metrics_are_reference_recall(self):
        self.assertEqual(benchmark_suite.calculate_entity_recall("fever cough", "fever"), 0.5)
        self.assertEqual(run_full_evaluation.clinical_entity_recall("fever cough", "fever"), 0.5)

    def test_entity_recall_uses_annotated_terms_and_bilingual_alternatives(self):
        recall = benchmark_suite.calculate_entity_recall(
            "fever and ሳል", "The patient has fever.", "fever; ሳል (Cough)"
        )
        self.assertEqual(recall, 0.5)

    def test_clinical_text_normalization_standardizes_units_and_transliterations(self):
        self.assertEqual(
            normalize_clinical_text("500mg, 94%, ras matat; rasmathat"),
            "500 milligrams 94 percent ras mathat ras mathat",
        )
        self.assertEqual(benchmark_suite.calculate_wer("Take 500mg.", "Take 500 milligrams"), 0.0)

    def test_clinical_alias_matching_accepts_amharic_and_brand_aliases(self):
        self.assertTrue(contains_term("ራስ ምታት", "headache"))
        self.assertTrue(contains_term("acetaminophen", "paracetamol"))
        self.assertTrue(contains_term("ትኩሳት", "fever"))
        self.assertTrue(contains_term("ከምግብ በኋላ።", "ከምግብ በኋላ"))

    def test_mwer_is_one_minus_annotated_target_recall(self):
        self.assertEqual(
            calculate_mwer("fever and cough", "fever", ["fever", "cough"]),
            0.5,
        )

    def test_clinical_evaluator_reports_normalized_wer_and_mwer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            results = root / "results.json"
            results.write_text(json.dumps([{
                "case_id": "CS-01",
                "transcript": "patient has fever",
            }]), encoding="utf-8")
            manifest = root / "manifest.csv"
            manifest.write_text(
                "case_id,reference_transcript,focus_terms\n"
                "CS-01,patient has fever and cough,fever;cough\n",
                encoding="utf-8",
            )
            dictionary = root / "medical_terms.json"
            dictionary.write_text(
                json.dumps({"categories": {"critical_terms": {"terms": ["shock"]}}}),
                encoding="utf-8",
            )
            report = evaluate_clinical_results(
                results,
                "test-model",
                manifest_path=manifest,
                dictionary_path=dictionary,
            )

        metrics = report["models"]["test-model"]
        self.assertEqual(metrics["mean_normalized_wer"], 0.4)
        self.assertEqual(metrics["mean_target_term_recall"], 0.5)
        self.assertEqual(metrics["mean_mwer"], 0.5)

    def test_active_benchmark_uses_the_100_case_master_manifest(self):
        manifest_path = (
            Path(__file__).resolve().parents[1]
            / "benchmark"
            / "metadata"
            / "BENCHMARK_MANIFEST.csv"
        )
        references = load_manifest(manifest_path)
        expected_cases = {f"CS-{number:02d}" for number in range(1, 101)}

        self.assertEqual(set(references), expected_cases)
        self.assertTrue(all(row["reference_transcript"] for row in references.values()))

    def test_first_partial_metric_is_latency_not_faas(self):
        result = run_full_evaluation.evaluate_case(
            "fever cough",
            "fever",
            first_frame_sent_ms=100,
            first_partial_token_ms=350,
        )

        self.assertEqual(result["first_partial_latency_ms"], 250)
        self.assertTrue(result["first_partial_latency_sla_met"])
        self.assertNotIn("faas_ms", result)


if __name__ == "__main__":
    unittest.main()