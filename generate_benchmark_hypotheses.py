import argparse
import asyncio
import csv
import gc
import importlib.metadata
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


MODEL_COLUMNS = {
    "intron": "intron_hypothesis",
    "whisper": "whisper_hypothesis",
    "wav2vec": "wav2vec2_hypothesis",
    "openai": "openai_hypothesis",
    "gemini": "gemini_hypothesis",
}
DEFAULT_MODEL_IDS = {
    "whisper": "openai/whisper-tiny",
    "wav2vec": "facebook/wav2vec2-base-960h",
}
MAX_TRANSIENT_RETRIES = 3
INITIAL_RETRY_DELAY_SECONDS = 2.0
MAX_RETRY_DELAY_SECONDS = 30.0
DEFAULT_GEMINI_REQUEST_INTERVAL_SECONDS = 15.0


def load_manifest(manifest_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with manifest_path.open(encoding="utf-8", newline="") as manifest_file:
        reader = csv.DictReader(manifest_file)
        if not reader.fieldnames:
            raise ValueError(f"Manifest has no header: {manifest_path}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"Manifest has no samples: {manifest_path}")
    fieldnames = list(reader.fieldnames)
    for column in MODEL_COLUMNS.values():
        if column not in fieldnames:
            fieldnames.append(column)
    for row in rows:
        for column in MODEL_COLUMNS.values():
            row.setdefault(column, "")
    return fieldnames, rows


def save_manifest(manifest_path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="", dir=manifest_path.parent, delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
        writer = csv.DictWriter(temporary, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary_path, manifest_path)


def require_authorized_dataset(rows: list[dict[str, str]], include_intron: bool = False) -> None:
    required_fields = ["consent_obtained", "de_identified", "reference_verified", "verified_gold_standard"]
    invalid = [
        row.get("sample_id", "unknown")
        for row in rows
        if any(row.get(field, "").strip().lower() not in {"true", "1", "yes"} for field in required_fields)
    ]
    if invalid:
        sample_ids = ", ".join(invalid[:5])
        raise ValueError(f"Required consent/de-identification/reference approvals are missing for: {sample_ids}")


def require_provider_api_keys(provider_kinds: set[str]) -> None:
    import main as gateway

    missing = []
    for provider_kind, key in (
        ("intron", gateway.INTRON_API_KEY),
        ("openai", gateway.OPENAI_API_KEY),
        ("gemini", gateway.get_gemini_api_keys()),
    ):
        if provider_kind in provider_kinds and not key:
            missing.append(provider_kind)
    if missing:
        raise RuntimeError(f"Missing server-side API key configuration for: {', '.join(missing)}")


def get_audio_path(dataset_dir: Path, row: dict[str, str]) -> Path:
    audio_path = (dataset_dir / row["audio_file"]).resolve()
    try:
        audio_path.relative_to(dataset_dir.resolve())
    except ValueError as error:
        raise ValueError(f"Audio path escapes dataset directory: {row['audio_file']}") from error
    if not audio_path.is_file():
        raise FileNotFoundError(audio_path)
    return audio_path


def save_success(
    manifest_path: Path,
    fieldnames: list[str],
    rows: list[dict[str, str]],
    row: dict[str, str],
    column: str,
    text: str,
) -> None:
    if not text.strip():
        raise ValueError("Model returned an empty transcript")
    row[column] = text.strip()
    save_manifest(manifest_path, fieldnames, rows)


async def call_with_transient_retries(provider, *args, max_retries: int = MAX_TRANSIENT_RETRIES) -> str:
    for attempt in range(max_retries + 1):
        try:
            return await provider(*args)
        except Exception as error:
            if getattr(error, "stop_retries", False):
                raise
            response = getattr(error, "response", None)
            status_code = getattr(response, "status_code", None)
            if status_code not in {429, 503} or attempt >= max_retries:
                raise

            retry_after = getattr(response, "headers", {}).get("Retry-After")
            try:
                delay = float(retry_after) if retry_after else INITIAL_RETRY_DELAY_SECONDS * (2 ** attempt)
            except (TypeError, ValueError):
                delay = INITIAL_RETRY_DELAY_SECONDS * (2 ** attempt)
            delay = min(delay, MAX_RETRY_DELAY_SECONDS)
            print(f"Hosted provider returned {status_code}; retrying in {delay:g}s ({attempt + 1}/{max_retries}).")
            await asyncio.sleep(delay)
    raise RuntimeError("Transient provider retry loop exited unexpectedly")


async def run_intron(
    manifest_path: Path,
    dataset_dir: Path,
    fieldnames: list[str],
    rows: list[dict[str, str]],
    overwrite: bool,
) -> tuple[int, list[dict[str, str]]]:
    import main as gateway

    if not gateway.INTRON_API_KEY:
        raise RuntimeError("INTRON_API_KEY is not configured")
    completed = 0
    errors = []
    for row in rows:
        column = MODEL_COLUMNS["intron"]
        if row.get(column, "").strip() and not overwrite:
            continue
        audio_path = get_audio_path(dataset_dir, row)
        try:
            response = await gateway._post_intron_sync_upload(
                audio_path.read_bytes(),
                audio_path.name,
                "audio/wav",
                "am",
                disable_llm_corrections="TRUE",
            )
            data = response.get("data", {}) if isinstance(response, dict) else {}
            text = str(data.get("audio_transcript") or data.get("transcript") or "").strip()
            save_success(manifest_path, fieldnames, rows, row, column, text)
            completed += 1
            print(f"Intron complete: {row['sample_id']} ({len(text)} chars)")
        except Exception as error:
            response = getattr(error, "response", None)
            status_code = getattr(response, "status_code", None)
            errors.append({
                "model": "intron",
                "sample_id": row["sample_id"],
                "error_type": type(error).__name__,
                "status_code": status_code,
            })
            print(f"Intron failed: {row['sample_id']} ({type(error).__name__})")
            if status_code in {401, 403}:
                print("Stopping Intron batch after authentication/permission failure.")
                break
        await asyncio.sleep(1)
    return completed, errors


async def run_hosted_provider(
    provider_kind: str,
    manifest_path: Path,
    dataset_dir: Path,
    fieldnames: list[str],
    rows: list[dict[str, str]],
    overwrite: bool,
    request_interval_seconds: float = 1.0,
) -> tuple[int, list[dict[str, str]]]:
    import main as gateway

    column = MODEL_COLUMNS[provider_kind]
    provider = gateway._benchmark_openai if provider_kind == "openai" else gateway._benchmark_gemini
    completed = 0
    errors = []
    for row in rows:
        if row.get(column, "").strip() and not overwrite:
            continue
        audio_path = get_audio_path(dataset_dir, row)
        try:
            contents = audio_path.read_bytes()
            if provider_kind == "openai":
                text = await call_with_transient_retries(provider, contents, audio_path.name, "audio/wav")
            else:
                text = await call_with_transient_retries(provider, contents, "audio/wav")
            save_success(manifest_path, fieldnames, rows, row, column, str(text))
            completed += 1
            print(f"{provider_kind.title()} complete: {row['sample_id']} ({len(str(text))} chars)")
        except Exception as error:
            response = getattr(error, "response", None)
            status_code = getattr(response, "status_code", None)
            errors.append({
                "model": provider_kind,
                "sample_id": row["sample_id"],
                "error_type": type(error).__name__,
                "status_code": status_code,
            })
            print(f"{provider_kind.title()} failed: {row['sample_id']} ({type(error).__name__})")
            if status_code in {401, 403}:
                print(f"Stopping {provider_kind.title()} batch after authentication/permission failure.")
                break
            if status_code == 429:
                print(f"Stopping {provider_kind.title()} batch after exhausting retries for rate limiting.")
                break
        await asyncio.sleep(request_interval_seconds)
    return completed, errors


def run_local_model(
    model_kind: str,
    model_id: str,
    manifest_path: Path,
    dataset_dir: Path,
    fieldnames: list[str],
    rows: list[dict[str, str]],
    overwrite: bool,
) -> tuple[int, list[dict[str, str]]]:
    import torch
    from transformers import pipeline

    torch.set_num_threads(1)
    column = MODEL_COLUMNS[model_kind]
    asr = pipeline("automatic-speech-recognition", model=model_id, device=-1)
    completed = 0
    errors = []
    for row in rows:
        if row.get(column, "").strip() and not overwrite:
            continue
        audio_path = get_audio_path(dataset_dir, row)
        try:
            if model_kind == "whisper":
                result = asr(str(audio_path), generate_kwargs={"task": "transcribe"})
            else:
                result = asr(str(audio_path))
            text = str(result.get("text", "")).strip()
            save_success(manifest_path, fieldnames, rows, row, column, text)
            completed += 1
            print(f"{model_id} complete: {row['sample_id']} ({len(text)} chars)")
        except Exception as error:
            errors.append({"model": model_id, "sample_id": row["sample_id"], "error_type": type(error).__name__})
            print(f"{model_id} failed: {row['sample_id']} ({type(error).__name__})")
    del asr
    gc.collect()
    return completed, errors


def write_run_metadata(
    manifest_path: Path,
    model_ids: dict[str, str],
    generated_this_run: dict[str, int],
    rows: list[dict[str, str]],
    errors: list[dict[str, str]],
    required_model_kinds: set[str],
) -> None:
    import main as gateway

    completed_samples = {
        model_kind: sum(bool(row.get(column, "").strip()) for row in rows)
        for model_kind, column in MODEL_COLUMNS.items()
    }
    metadata = {
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_status": "complete" if all(completed_samples[kind] == len(rows) for kind in required_model_kinds) and not errors else "partial",
        "device": "cpu",
        "torch_threads": 1,
        "models": {
            "intron": {
                "service": "Intron synchronous ASR upload",
                "language_code": "am",
                "llm_corrections_disabled": True,
            },
            "whisper": {
                "model_id": model_ids["whisper"],
                "task": "transcribe",
                "language_selection": "automatic",
            },
            "wav2vec": {
                "model_id": model_ids["wav2vec"],
                "language_limitation": "English-only checkpoint; Amharic/code-switch performance may be poor.",
            },
            "openai": {
                "model_id": model_ids["openai"],
                "task": "audio transcription",
                "language": "am",
                "hosted_provider": True,
            },
            "gemini": {
                "model_id": model_ids["gemini"],
                "task": "verbatim audio transcription",
                "hosted_provider": True,
                "configured_key_slots": len(gateway.get_gemini_api_keys()),
                "fallback_on_http_429": True,
            },
        },
        "completed_samples": completed_samples,
        "generated_this_run": generated_this_run,
        "errors": errors,
        "library_versions": {
            "torch": importlib.metadata.version("torch"),
            "transformers": importlib.metadata.version("transformers"),
        },
    }
    output_path = manifest_path.parent / "inference_metadata.json"
    output_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate genuine ASR hypotheses for the verified benchmark manifest.")
    parser.add_argument("--manifest", type=Path, default=Path("benchmark_data/manifest.csv"))
    parser.add_argument("--only", choices=["all", "intron", "whisper", "wav2vec", "openai", "gemini"], default="all")
    parser.add_argument(
        "--include-hosted-providers",
        "--include-hosted-intron",
        dest="include_hosted_providers",
        action="store_true",
        help="Allow sending consented/de-identified audio to hosted ASR providers.",
    )
    parser.add_argument("--whisper-model-id", default=DEFAULT_MODEL_IDS["whisper"])
    parser.add_argument("--wav2vec-model-id", default=DEFAULT_MODEL_IDS["wav2vec"])
    parser.add_argument(
        "--gemini-request-interval-seconds",
        type=float,
        default=DEFAULT_GEMINI_REQUEST_INTERVAL_SECONDS,
        help="Delay between Gemini sample requests to reduce rate-limit pressure.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Regenerate existing hypotheses.")
    args = parser.parse_args()

    hosted_providers = {"intron", "openai", "gemini"}
    selected_providers = hosted_providers if args.only == "all" else ({args.only} if args.only in hosted_providers else set())
    if selected_providers and not args.include_hosted_providers:
        parser.error("--include-hosted-providers is required to send audio to hosted ASR services")
    manifest_path = args.manifest.resolve()
    dataset_dir = manifest_path.parent
    fieldnames, rows = load_manifest(manifest_path)
    require_authorized_dataset(rows, "intron" in selected_providers)
    require_provider_api_keys(selected_providers)
    model_ids = {
        "whisper": args.whisper_model_id,
        "wav2vec": args.wav2vec_model_id,
        "openai": os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe"),
        "gemini": os.getenv("GEMINI_TRANSCRIBE_MODEL", "gemini-flash-latest"),
    }
    completed = {kind: 0 for kind in MODEL_COLUMNS}
    errors = []

    if "intron" in selected_providers:
        completed["intron"], model_errors = asyncio.run(
            run_intron(manifest_path, dataset_dir, fieldnames, rows, args.overwrite)
        )
        errors.extend(model_errors)
    for provider_kind in ("openai", "gemini"):
        if provider_kind in selected_providers:
            completed[provider_kind], model_errors = asyncio.run(
                run_hosted_provider(
                    provider_kind,
                    manifest_path,
                    dataset_dir,
                    fieldnames,
                    rows,
                    args.overwrite,
                    request_interval_seconds=(
                        args.gemini_request_interval_seconds if provider_kind == "gemini" else 1.0
                    ),
                )
            )
            errors.extend(model_errors)
    if args.only in {"all", "whisper"}:
        completed["whisper"], model_errors = run_local_model(
            "whisper", model_ids["whisper"], manifest_path, dataset_dir, fieldnames, rows, args.overwrite
        )
        errors.extend(model_errors)
    if args.only in {"all", "wav2vec"}:
        completed["wav2vec"], model_errors = run_local_model(
            "wav2vec", model_ids["wav2vec"], manifest_path, dataset_dir, fieldnames, rows, args.overwrite
        )
        errors.extend(model_errors)

    required_model_kinds = {"intron", "whisper", "wav2vec"} | selected_providers
    write_run_metadata(manifest_path, model_ids, completed, rows, errors, required_model_kinds)
    print(f"Run complete: {completed}; errors: {len(errors)}")


if __name__ == "__main__":
    main()