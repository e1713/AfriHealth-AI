"""Resumable multi-model ASR inference for the clinical benchmark.

Live provider calls are opt-in with ``--env live``. The default mock mode never
loads a model or accesses credentials; its latency is simulated, not measured.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import os
import random
import sys
import tempfile
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Sequence, TextIO


MOCK_TRANSCRIPT = (
    "MOCK TRANSCRIPT ONLY: Amharic-English clinical speech sample for pipeline testing."
)
HOSTED_APPROVAL_REQUIREMENTS = (
    ("consent_obtained", "consent_evidence_reference"),
    ("de_identified", "de_identification_evidence_reference"),
    ("hosted_inference_approved", "hosted_inference_approval_evidence_reference"),
)
COMPARISON_COLUMNS = (
    "case_id",
    "model_name",
    "predicted_transcript",
    "latency_seconds",
    "status_code",
)


@dataclass(frozen=True)
class InferenceRecord:
    """One model attempt for one case; contains no reference transcript."""

    case_id: str
    model_name: str
    predicted_transcript: str
    latency_seconds: float
    status_code: str
    timestamp_utc: str
    error_type: str = ""
    error_message: str = ""


def has_documented_hosted_inference_approval(row: dict[str, str]) -> bool:
    """Require affirmative flags and evidence references before hosted inference."""
    return all(
        row.get(flag, "").strip().casefold() == "true"
        and bool(row.get(evidence_field, "").strip())
        for flag, evidence_field in HOSTED_APPROVAL_REQUIREMENTS
    ) and (
        row.get("audio_presence_status", "").strip().casefold() == "verified_present"
        and bool(row.get("audio_presence_evidence_reference", "").strip())
        and bool(row.get("audio_checksum_evidence_reference", "").strip())
        and len(row.get("audio_checksum_sha256", "").strip()) == 64
        and all(character in "0123456789abcdefABCDEF" for character in row["audio_checksum_sha256"].strip())
    )


class ClinicalASRModel(ABC):
    """Common interface for clinical ASR systems."""

    model_name: str

    @abstractmethod
    def transcribe(self, audio_path: Path) -> str:
        """Transcribe one audio file and return the unmodified hypothesis."""


class _GatewayASR(ClinicalASRModel):
    """Adapter for the application's configured, server-side provider clients."""

    provider: str

    def transcribe(self, audio_path: Path) -> str:
        # Reuse the project's existing gateway adapters so key handling,
        # provider payloads, and endpoint configuration remain centralized.
        import main as gateway

        audio = audio_path.read_bytes()
        if self.provider == "sahara":
            response = asyncio.run(
                gateway._post_intron_sync_upload(
                    audio,
                    audio_path.name,
                    "audio/wav",
                    "am",
                    disable_llm_corrections="TRUE",
                )
            )
            response_data = response.get("data", {}) if isinstance(response, dict) else {}
            transcript = response_data.get("audio_transcript") or response_data.get("transcript")
        elif self.provider == "gemini":
            transcript = asyncio.run(gateway._benchmark_gemini(audio, "audio/wav"))
        else:
            raise RuntimeError(f"Unsupported gateway provider: {self.provider}")

        result = str(transcript or "").strip()
        if not result:
            raise ValueError(f"{self.model_name} returned an empty transcript")
        return result


class SaharaASR(_GatewayASR):
    """Sahara/Intron ASR using the application's INTRON_API_KEY configuration."""

    model_name = "Sahara"
    provider = "sahara"


class GeminiASR(_GatewayASR):
    """Gemini ASR using the application's GEMINI_API_KEY configuration."""

    model_name = "Gemini"
    provider = "gemini"


class _LocalModelPlaceholder(ClinicalASRModel):
    """Explicit placeholder for a local model adapter not yet implemented."""

    def transcribe(self, audio_path: Path) -> str:
        del audio_path
        raise NotImplementedError(
            f"{self.model_name} local model loading/inference is not implemented"
        )


class WhisperASR(_LocalModelPlaceholder):
    """Tier 1 local Whisper adapter placeholder."""

    model_name = "Whisper"


class Wav2Vec2ASR(_LocalModelPlaceholder):
    """Tier 2 local Wav2Vec2 adapter placeholder."""

    model_name = "Wav2Vec2"


class SpeechBrainASR(_LocalModelPlaceholder):
    """Tier 2 local SpeechBrain adapter placeholder."""

    model_name = "SpeechBrain"


class NeMoASR(_LocalModelPlaceholder):
    """Tier 2 local NVIDIA NeMo adapter placeholder."""

    model_name = "NeMo"


MODEL_TYPES: dict[str, type[ClinicalASRModel]] = {
    "sahara": SaharaASR,
    "gemini": GeminiASR,
    "whisper": WhisperASR,
    "wav2vec2": Wav2Vec2ASR,
    "speechbrain": SpeechBrainASR,
    "nemo": NeMoASR,
}


class MockASR(ClinicalASRModel):
    """Safe offline test adapter with generated (not measured) latency."""

    def __init__(
        self,
        model_name: str,
        latency_factory: Callable[[float, float], float] = random.uniform,
    ) -> None:
        self.model_name = model_name
        self._latency_factory = latency_factory

    def transcribe(self, audio_path: Path) -> str:
        del audio_path
        return MOCK_TRANSCRIPT

    def simulated_latency(self) -> float:
        return round(self._latency_factory(0.5, 2.0), 6)


def load_manifest(manifest_path: Path) -> list[dict[str, str]]:
    """Read manifest rows and fail fast on malformed or duplicate case IDs."""
    try:
        with manifest_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or not {"case_id", "audio_filename"}.issubset(reader.fieldnames):
                raise ValueError("Manifest must contain case_id and audio_filename columns")
            rows = list(reader)
    except OSError as error:
        raise OSError(f"Could not read benchmark manifest {manifest_path}: {error}") from error

    if not rows:
        raise ValueError(f"Manifest contains no cases: {manifest_path}")
    case_ids = [row["case_id"].strip() for row in rows]
    if any(not case_id for case_id in case_ids):
        raise ValueError("Manifest contains an empty case_id")
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("Manifest contains duplicate case_id values")
    if any(not row.get("audio_filename", "").strip() for row in rows):
        raise ValueError("Manifest contains an empty audio_filename")
    return rows


def resolve_audio_path(cleaned_audio_dir: Path, audio_filename: str) -> Path:
    """Resolve a manifest audio path while preventing directory traversal."""
    audio_path = (cleaned_audio_dir / audio_filename).resolve()
    try:
        audio_path.relative_to(cleaned_audio_dir.resolve())
    except ValueError as error:
        raise ValueError(f"Audio path escapes cleaned_audio/: {audio_filename}") from error
    if not audio_path.is_file():
        raise FileNotFoundError(f"Cleaned audio file not found: {audio_path}")
    return audio_path


def read_inference_log(log_path: Path) -> list[dict[str, object]]:
    """Parse the append-only log, surfacing malformed records explicitly."""
    if not log_path.exists():
        return []
    records: list[dict[str, object]] = []
    with log_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSONL record at {log_path}:{line_number}: {error}"
                ) from error
            if not isinstance(record, dict):
                raise ValueError(f"JSONL record at {log_path}:{line_number} must be an object")
            records.append(record)
    return records


def successful_checkpoints(records: Sequence[dict[str, object]]) -> set[tuple[str, str]]:
    """Return case/model pairs with a successful prior result."""
    return {
        (str(record["case_id"]), str(record["model_name"]))
        for record in records
        if record.get("status_code") in {"200", "MOCK"}
        and isinstance(record.get("predicted_transcript"), str)
        and bool(str(record["predicted_transcript"]).strip())
    }


def write_comparison_csv(csv_path: Path, records: Sequence[dict[str, object]]) -> None:
    """Atomically regenerate the flattened comparison CSV from the log."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=csv_path.parent,
            prefix=f".{csv_path.name}.",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            writer = csv.DictWriter(temporary, fieldnames=COMPARISON_COLUMNS)
            writer.writeheader()
            for record in records:
                writer.writerow(
                    {column: record.get(column, "") for column in COMPARISON_COLUMNS}
                )
        os.replace(temporary_path, csv_path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


class InferenceEngine:
    """Sequential, resumable inference runner with per-attempt telemetry."""

    def __init__(
        self,
        project_root: Path,
        *,
        environment: str = "mock",
        model_keys: Sequence[str] | None = None,
        output: TextIO = sys.stdout,
        mock_latency_factory: Callable[[float, float], float] = random.uniform,
    ) -> None:
        if environment not in {"mock", "live"}:
            raise ValueError("environment must be 'mock' or 'live'")
        self.project_root = project_root.resolve()
        self.environment = environment
        self.model_keys = tuple(model_keys or MODEL_TYPES)
        unknown_models = set(self.model_keys) - set(MODEL_TYPES)
        if unknown_models:
            raise ValueError(f"Unknown model(s): {', '.join(sorted(unknown_models))}")
        if not self.model_keys:
            raise ValueError("At least one model must be selected")
        self.output = output
        self.mock_latency_factory = mock_latency_factory
        self.manifest_path = self.project_root / "benchmark" / "metadata" / "BENCHMARK_MANIFEST.csv"
        self.cleaned_audio_dir = self.project_root / "cleaned_audio"
        self.results_dir = self.project_root / "results"
        self.log_path = self.results_dir / "inference_log.jsonl"
        self.csv_path = self.results_dir / "model_comparisons.csv"

    def _build_models(self) -> dict[str, ClinicalASRModel]:
        """Instantiate stubs only in live mode; mock mode cannot load providers."""
        if self.environment == "mock":
            return {
                key: MockASR(
                    MODEL_TYPES[key].model_name,
                    latency_factory=self.mock_latency_factory,
                )
                for key in self.model_keys
            }
        return {key: MODEL_TYPES[key]() for key in self.model_keys}

    def _append_record(self, record: InferenceRecord) -> list[dict[str, object]]:
        self.results_dir.mkdir(parents=True, exist_ok=True)
        serialized = asdict(record)
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(serialized, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        records = read_inference_log(self.log_path)
        write_comparison_csv(self.csv_path, records)
        return records

    @staticmethod
    def _status_code(error: Exception) -> str:
        response = getattr(error, "response", None)
        status_code = getattr(response, "status_code", None)
        return str(status_code) if status_code is not None else "ERROR"

    def run(self) -> int:
        rows = load_manifest(self.manifest_path)
        hosted_models = {"sahara", "gemini"}.intersection(self.model_keys)
        if self.environment == "live" and hosted_models:
            unauthorized = [
                row["case_id"]
                for row in rows
                if not has_documented_hosted_inference_approval(row)
            ]
            if unauthorized:
                raise ValueError(
                    "Hosted inference blocked: consent, de-identification, and hosted approval "
                    "must be true with evidence references for every case. "
                    f"First blocked cases: {', '.join(unauthorized[:5])}"
                )
            checksum_mismatches = []
            for row in rows:
                audio_path = resolve_audio_path(self.cleaned_audio_dir, row["audio_filename"])
                actual_checksum = hashlib.sha256(audio_path.read_bytes()).hexdigest()
                if actual_checksum != row.get("audio_checksum_sha256", "").strip().casefold():
                    checksum_mismatches.append(row["case_id"])
            if checksum_mismatches:
                raise ValueError(
                    "Hosted inference blocked: cleaned audio checksum does not match the approved manifest for "
                    + ", ".join(checksum_mismatches[:5])
                )
            import main as gateway

            missing_credentials = []
            if "sahara" in hosted_models and not gateway.INTRON_API_KEY:
                missing_credentials.append("INTRON_API_KEY")
            if "gemini" in hosted_models and not gateway.get_gemini_api_keys():
                missing_credentials.append("GEMINI_API_KEY")
            if missing_credentials:
                raise ValueError(
                    "Live provider configuration is missing: "
                    + ", ".join(missing_credentials)
                )
        self.results_dir.mkdir(parents=True, exist_ok=True)
        records = read_inference_log(self.log_path)
        checkpoints = successful_checkpoints(records)
        # Rebuild the flattened file on startup too, so it recovers from a
        # process interruption after a flushed JSONL append.
        write_comparison_csv(self.csv_path, records)
        models = self._build_models()

        attempted = 0
        skipped = 0
        for row in rows:
            case_id = row["case_id"].strip()
            for model in models.values():
                model_name = model.model_name
                if (case_id, model_name) in checkpoints:
                    skipped += 1
                    continue

                attempted += 1
                started = time.perf_counter()
                try:
                    audio_path = resolve_audio_path(
                        self.cleaned_audio_dir,
                        row["audio_filename"].strip(),
                    )
                    transcript = model.transcribe(audio_path).strip()
                    if not transcript:
                        raise ValueError("Model returned an empty transcript")
                    if self.environment == "mock":
                        if not isinstance(model, MockASR):
                            raise TypeError("Mock mode constructed a non-mock model")
                        latency = model.simulated_latency()
                        status_code = "MOCK"
                    else:
                        latency = time.perf_counter() - started
                        status_code = "200"
                    record = InferenceRecord(
                        case_id=case_id,
                        model_name=model_name,
                        predicted_transcript=transcript,
                        latency_seconds=round(latency, 6),
                        status_code=status_code,
                        timestamp_utc=datetime.now(timezone.utc).isoformat(),
                    )
                    records = self._append_record(record)
                    checkpoints.add((case_id, model_name))
                    print(
                        f"{status_code} {case_id} {model_name}: "
                        f"{record.latency_seconds:.6f}s",
                        file=self.output,
                    )
                except Exception as error:
                    latency = (
                        model.simulated_latency()
                        if isinstance(model, MockASR)
                        else time.perf_counter() - started
                    )
                    error_message = str(error).replace("\n", " ")[:500]
                    record = InferenceRecord(
                        case_id=case_id,
                        model_name=model_name,
                        predicted_transcript="",
                        latency_seconds=round(latency, 6),
                        status_code=(
                            "MOCK_ERROR"
                            if self.environment == "mock"
                            else self._status_code(error)
                        ),
                        timestamp_utc=datetime.now(timezone.utc).isoformat(),
                        error_type=type(error).__name__,
                        error_message=error_message,
                    )
                    records = self._append_record(record)
                    print(
                        f"{record.status_code} {case_id} {model_name}: "
                        f"{record.error_type}: {error_message}",
                        file=self.output,
                    )

        write_comparison_csv(self.csv_path, records)
        print(
            f"Run complete: {attempted} attempt(s), {skipped} checkpointed case/model "
            f"pair(s). Results: {self.results_dir}",
            file=self.output,
        )
        attempted_records = records[-attempted:] if attempted else []
        return 1 if any(
            record.get("status_code") not in {"200", "MOCK"}
            for record in attempted_records
        ) else 0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run resumable ASR inference on the benchmark manifest."
    )
    parser.add_argument(
        "--env",
        choices=("mock", "live"),
        default="mock",
        help="mock is safe/offline and default; live makes configured provider calls.",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        choices=tuple(MODEL_TYPES),
        default=list(MODEL_TYPES),
        help="One or more model adapters to run (default: all six).",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Repository root (default: directory containing this script).",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    engine = InferenceEngine(
        args.root,
        environment=args.env,
        model_keys=args.models,
    )
    try:
        return engine.run()
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Fatal inference setup error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
