import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from inference_engine import (
    MOCK_TRANSCRIPT,
    InferenceEngine,
    MockASR,
    has_documented_hosted_inference_approval,
    load_manifest,
    parse_args,
    read_inference_log,
    successful_checkpoints,
)


class InferenceEngineTests(unittest.TestCase):
    def create_project(self, root: Path, case_ids: tuple[str, ...] = ("CS-01", "CS-02")) -> None:
        manifest_dir = root / "benchmark" / "metadata"
        manifest_dir.mkdir(parents=True)
        cleaned_dir = root / "cleaned_audio"
        cleaned_dir.mkdir()
        manifest_path = manifest_dir / "BENCHMARK_MANIFEST.csv"
        with manifest_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=("case_id", "audio_filename", "reference_transcript"),
            )
            writer.writeheader()
            for case_id in case_ids:
                filename = f"{case_id}.wav"
                writer.writerow(
                    {
                        "case_id": case_id,
                        "audio_filename": filename,
                        "reference_transcript": "reference must not be logged",
                    }
                )
                (cleaned_dir / filename).write_bytes(b"mock audio placeholder")

    def test_mock_mode_writes_synthetic_outputs_and_comparison_schema(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self.create_project(root)
            engine = InferenceEngine(
                root,
                environment="mock",
                model_keys=("sahara", "gemini"),
                mock_latency_factory=Mock(return_value=1.25),
            )

            self.assertEqual(engine.run(), 0)

            records = read_inference_log(root / "results" / "inference_log.jsonl")
            self.assertEqual(len(records), 4)
            self.assertTrue(all(record["predicted_transcript"] == MOCK_TRANSCRIPT for record in records))
            self.assertTrue(all(record["latency_seconds"] == 1.25 for record in records))
            self.assertTrue(all(record["status_code"] == "MOCK" for record in records))
            self.assertEqual(
                successful_checkpoints(records),
                {
                    ("CS-01", "Sahara"),
                    ("CS-01", "Gemini"),
                    ("CS-02", "Sahara"),
                    ("CS-02", "Gemini"),
                },
            )

            with (root / "results" / "model_comparisons.csv").open(
                encoding="utf-8",
                newline="",
            ) as handle:
                comparison_rows = list(csv.DictReader(handle))
            self.assertEqual(len(comparison_rows), 4)
            self.assertEqual(
                set(comparison_rows[0]),
                {
                    "case_id",
                    "model_name",
                    "predicted_transcript",
                    "latency_seconds",
                    "status_code",
                },
            )
            log_text = (root / "results" / "inference_log.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("reference must not be logged", log_text)

    def test_successful_pairs_are_skipped_on_resume(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self.create_project(root, case_ids=("CS-01",))
            engine = InferenceEngine(
                root,
                environment="mock",
                model_keys=("sahara",),
                mock_latency_factory=Mock(return_value=0.75),
            )

            self.assertEqual(engine.run(), 0)
            self.assertEqual(engine.run(), 0)
            records = read_inference_log(root / "results" / "inference_log.jsonl")
            self.assertEqual(len(records), 1)

    def test_failure_is_logged_and_remains_retryable(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self.create_project(root, case_ids=("CS-01",))
            engine = InferenceEngine(
                root,
                environment="live",
                model_keys=("whisper",),
            )

            self.assertEqual(engine.run(), 1)
            records = read_inference_log(root / "results" / "inference_log.jsonl")
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["status_code"], "ERROR")
            self.assertEqual(records[0]["error_type"], "NotImplementedError")
            self.assertEqual(successful_checkpoints(records), set())

    def test_mock_missing_audio_is_recorded_as_failure(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self.create_project(root, case_ids=("CS-01",))
            (root / "cleaned_audio" / "CS-01.wav").unlink()
            engine = InferenceEngine(
                root,
                environment="mock",
                model_keys=("sahara",),
                mock_latency_factory=Mock(return_value=1.0),
            )

            self.assertEqual(engine.run(), 1)
            records = read_inference_log(root / "results" / "inference_log.jsonl")
            self.assertEqual(records[0]["status_code"], "MOCK_ERROR")
            self.assertIn("Cleaned audio file not found", str(records[0]["error_message"]))

    def test_manifest_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            manifest_path = Path(temporary_directory) / "manifest.csv"
            manifest_path.write_text(
                "case_id,audio_filename\nCS-01,CS-01.wav\nCS-01,CS-01-copy.wav\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "duplicate case_id"):
                load_manifest(manifest_path)

    def test_malformed_jsonl_is_reported(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            log_path = Path(temporary_directory) / "inference_log.jsonl"
            log_path.write_text('{"case_id": "CS-01"}\n{broken\n', encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Invalid JSONL record"):
                read_inference_log(log_path)

    def test_api_adapters_are_not_built_in_mock_mode(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            engine = InferenceEngine(root, environment="mock", model_keys=("sahara",))

            with patch("inference_engine.SaharaASR", side_effect=AssertionError("must not instantiate")):
                model = engine._build_models()["sahara"]

            self.assertEqual(model.model_name, "Sahara")

    def test_mock_latency_is_randomized_within_requested_bounds(self):
        model = MockASR("Test Model")

        for _ in range(50):
            self.assertGreaterEqual(model.simulated_latency(), 0.5)
            self.assertLessEqual(model.simulated_latency(), 2.0)

    def test_cli_defaults_to_mock_environment(self):
        self.assertEqual(parse_args([]).env, "mock")

    def test_live_hosted_inference_requires_explicit_case_approval(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self.create_project(root, case_ids=("CS-01",))
            engine = InferenceEngine(
                root,
                environment="live",
                model_keys=("sahara",),
            )

            with self.assertRaisesRegex(ValueError, "Hosted inference blocked"):
                engine.run()
            self.assertFalse((root / "results" / "inference_log.jsonl").exists())

    def test_hosted_inference_requires_evidence_references(self):
        self.assertFalse(
            has_documented_hosted_inference_approval(
                {
                    "consent_obtained": "true",
                    "de_identified": "true",
                    "hosted_inference_approved": "true",
                }
            )
        )
        self.assertTrue(
            has_documented_hosted_inference_approval(
                {
                    "consent_obtained": "true",
                    "consent_evidence_reference": "restricted://consent/CS-01",
                    "de_identified": "true",
                    "de_identification_evidence_reference": "review://CS-01",
                    "hosted_inference_approved": "true",
                    "hosted_inference_approval_evidence_reference": "approval://CS-01",
                    "audio_presence_status": "verified_present",
                    "audio_presence_evidence_reference": "provenance://CS-01",
                    "audio_checksum_evidence_reference": "checksum://CS-01",
                    "audio_checksum_sha256": "a" * 64,
                }
            )
        )

if __name__ == "__main__":
    unittest.main()
