import csv
import tempfile
import unittest
from pathlib import Path

from generate_results_doc import generate_reports
from visualize_results import (
    CODE_SWITCH_CATEGORIES,
    compute_codeswitch_breakdown,
    generate_figures,
    load_metrics,
)


class VisualizationAndReportingTests(unittest.TestCase):
    def create_metrics(self, path: Path, rows: list[dict[str, str]]) -> None:
        fields = (
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
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_mock_metrics_generate_all_figures_without_accuracy_scores(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            metrics_path = root / "metrics.csv"
            self.create_metrics(
                metrics_path,
                [
                    {
                        "model_name": "Sahara",
                        "evaluation_status": "mock_only_accuracy_not_scored",
                        "case_count": "100",
                        "live_success_count": "0",
                        "mock_success_count": "100",
                        "failed_case_count": "0",
                        "mean_wer": "",
                        "mean_medical_term_recall": "",
                        "critical_term_miss_rate": "",
                        "critical_term_misses": "0",
                        "critical_term_count": "0",
                        "mean_latency_seconds": "",
                        "mean_simulated_latency_seconds": "1.25",
                        "latency_source": "simulated_mock_only",
                    }
                ],
            )
            loaded_metrics = load_metrics(metrics_path)
            self.assertEqual(len(loaded_metrics), 6)
            figures = generate_figures(metrics_path, root / "figures")

            self.assertEqual(len(figures), 4)
            self.assertEqual(
                {path.name for path in figures},
                {
                    "wer_comparison.png",
                    "medical_term_recall.png",
                    "latency_vs_accuracy.png",
                    "codeswitch_breakdown.png",
                },
            )
            for figure in figures:
                with self.subTest(figure=figure.name):
                    self.assertGreater(figure.stat().st_size, 1000)

    def test_live_metrics_and_code_switch_breakdown_generate(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            metrics_path = root / "metrics.csv"
            manifest_path = root / "manifest.csv"
            outputs_path = root / "outputs.csv"
            inference_log = root / "inference.jsonl"
            self.create_metrics(
                metrics_path,
                [
                    {
                        "model_name": "Sahara",
                        "evaluation_status": "provisional_live_metrics_unverified_references",
                        "case_count": "3",
                        "live_success_count": "3",
                        "mock_success_count": "0",
                        "failed_case_count": "0",
                        "mean_wer": "0.2",
                        "mean_medical_term_recall": "0.75",
                        "critical_term_miss_rate": "0.1",
                        "critical_term_misses": "1",
                        "critical_term_count": "10",
                        "mean_latency_seconds": "2.4",
                        "mean_simulated_latency_seconds": "",
                        "latency_source": "measured_live_wall_clock",
                    }
                ],
            )
            with manifest_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=(
                        "case_id",
                        "reference_transcript",
                        "focus_terms",
                        "code_switch_category",
                    ),
                )
                writer.writeheader()
                writer.writerows(
                    [
                        {
                            "case_id": "CS-01",
                            "reference_transcript": "Patient has fever.",
                            "focus_terms": "fever",
                            "code_switch_category": CODE_SWITCH_CATEGORIES[0],
                        },
                        {
                            "case_id": "CS-02",
                            "reference_transcript": "ሕመምተኛው has cough.",
                            "focus_terms": "cough",
                            "code_switch_category": CODE_SWITCH_CATEGORIES[1],
                        },
                    ]
                )
            with outputs_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=("case_id", "model_name", "predicted_transcript", "status_code"),
                )
                writer.writeheader()
                writer.writerows(
                    [
                        {
                            "case_id": "CS-01",
                            "model_name": "Sahara",
                            "predicted_transcript": "Patient has fever.",
                            "status_code": "200",
                        },
                        {
                            "case_id": "CS-02",
                            "model_name": "Sahara",
                            "predicted_transcript": "ሕመምተኛው has cough.",
                            "status_code": "200",
                        },
                        {
                            "case_id": "CS-02",
                            "model_name": "Gemini",
                            "predicted_transcript": "MOCK output",
                            "status_code": "MOCK",
                        },
                    ]
                )
            inference_log.write_text(
                '\n'.join(
                    (
                        '{"case_id":"CS-01","model_name":"Sahara","status_code":"200","latency_seconds":1.0}',
                        '{"case_id":"CS-02","model_name":"Sahara","status_code":"200","latency_seconds":3.0}',
                        '{"case_id":"CS-02","model_name":"Gemini","status_code":"MOCK","latency_seconds":1.5}',
                    )
                )
                + "\n",
                encoding="utf-8",
            )

            breakdown = compute_codeswitch_breakdown(manifest_path, outputs_path)
            self.assertEqual(len(breakdown[CODE_SWITCH_CATEGORIES[0]]["wer"]), 1)
            self.assertEqual(len(breakdown[CODE_SWITCH_CATEGORIES[1]]["medical_term_recall"]), 1)
            figures = generate_figures(
                metrics_path,
                root / "figures",
                manifest_path=manifest_path,
                outputs_path=outputs_path,
                inference_log_path=inference_log,
            )
            self.assertTrue(all(path.is_file() for path in figures))

    def test_reporting_updates_generated_sections_idempotently(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            metrics_path = root / "metrics.csv"
            benchmark_report = root / "BENCHMARK_RESULTS.md"
            recommendation_report = root / "MODEL_RECOMMENDATION.md"
            self.create_metrics(
                metrics_path,
                [
                    {
                        "model_name": "Sahara",
                        "evaluation_status": "mock_only_accuracy_not_scored",
                        "case_count": "100",
                        "live_success_count": "0",
                        "mock_success_count": "100",
                        "failed_case_count": "0",
                        "mean_wer": "",
                        "mean_medical_term_recall": "",
                        "critical_term_miss_rate": "",
                        "critical_term_misses": "0",
                        "critical_term_count": "0",
                        "mean_latency_seconds": "",
                        "mean_simulated_latency_seconds": "1.25",
                        "latency_source": "simulated_mock_only",
                    }
                ],
            )
            benchmark_report.write_text("# Existing report\n\nKeep this section.\n", encoding="utf-8")

            generate_reports(metrics_path, benchmark_report, recommendation_report)
            first_output = benchmark_report.read_text(encoding="utf-8")
            generate_reports(metrics_path, benchmark_report, recommendation_report)
            second_output = benchmark_report.read_text(encoding="utf-8")

            self.assertIn("Keep this section.", second_output)
            self.assertIn("mock_only_accuracy_not_scored", second_output)
            self.assertIn("N/A", second_output)
            self.assertEqual(
                first_output.count("<!-- BEGIN AUTO-GENERATED EVALUATION SUMMARY -->"),
                1,
            )
            self.assertEqual(
                second_output.count("<!-- BEGIN AUTO-GENERATED EVALUATION SUMMARY -->"),
                1,
            )
            self.assertTrue(recommendation_report.is_file())
            self.assertIn(
                "No model is ranked or recommended for clinical use",
                recommendation_report.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
