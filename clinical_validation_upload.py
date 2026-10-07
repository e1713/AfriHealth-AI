"""Upload explicitly approved benchmark recordings through the local Intron bridge."""

import argparse
import hashlib
import json
from pathlib import Path

import requests

from inference_engine import has_documented_hosted_inference_approval, load_manifest


def load_references(path: Path) -> dict[str, dict[str, str]]:
    return {
        row["case_id"]: row
        for row in load_manifest(path)
    }


def canonical_audio(root: Path, audio_filename: str) -> Path:
    audio_path = (root / audio_filename).resolve()
    try:
        audio_path.relative_to(root.resolve())
    except ValueError as error:
        raise ValueError(f"Audio path escapes the audio directory: {audio_filename}") from error
    if not audio_path.is_file():
        raise FileNotFoundError(f"No canonical recording found: {audio_path}")
    return audio_path


def main() -> None:
    project_root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Upload only explicitly approved cases from the master benchmark manifest."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=project_root / "benchmark" / "metadata" / "BENCHMARK_MANIFEST.csv",
        help="Authoritative benchmark manifest",
    )
    parser.add_argument(
        "--audio-dir",
        type=Path,
        default=project_root / "cleaned_audio",
        help="Directory containing standardized WAV recordings",
    )
    parser.add_argument("--endpoint", default="http://127.0.0.1:8000/api/intron/stt/upload-sync")
    parser.add_argument("--output", default="benchmark_upload_results.json")
    parser.add_argument("--upload", action="store_true", help="Perform external inference; otherwise validate only")
    args = parser.parse_args()

    audio_root = args.audio_dir.resolve()
    references = load_references(args.manifest.resolve())
    cases = sorted(references)
    results = []
    for case_id in cases:
        row = references[case_id]
        audio_filename = row.get("audio_filename", "").strip()
        if not audio_filename:
            raise ValueError(f"Manifest case {case_id} has no audio_filename")
        audio_path = canonical_audio(audio_root, audio_filename)
        result = {
            "case_id": case_id,
            "audio_file": audio_path.name,
            "reference_transcript": row.get("reference_transcript", ""),
            "target_terms": row.get("focus_terms", ""),
            "upload_status": "validated_only",
        }
        if args.upload:
            if not has_documented_hosted_inference_approval(row):
                raise ValueError(
                    f"Hosted inference blocked for {case_id}: consent, de-identification, "
                    "and hosted inference approval must be true with evidence references."
                )
            actual_checksum = hashlib.sha256(audio_path.read_bytes()).hexdigest()
            if actual_checksum != row.get("audio_checksum_sha256", "").strip().casefold():
                raise ValueError(f"Hosted inference blocked for {case_id}: audio checksum does not match manifest")
            with audio_path.open("rb") as audio_file:
                response = requests.post(
                    args.endpoint,
                    files={
                        "audio_file_blob": (
                            audio_path.name,
                            audio_file,
                            "audio/wav",
                        )
                    },
                    data={
                        "audio_file_name": audio_path.name,
                        "use_language_asr_input": "am",
                        "use_category": "file_category_telehealth",
                        "use_disable_llm_corrections": "FALSE",
                    },
                    timeout=130,
                )
            try:
                body = response.json()
            except ValueError:
                body = {"raw_response": response.text[:1000]}
            result["http_status"] = response.status_code
            result["response"] = body
            result["upload_status"] = "uploaded" if response.ok else "failed"
        results.append(result)
        print(f"{case_id}: {result['upload_status']} ({audio_path.name})")

    output_path = Path(args.output).resolve()
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Results written to {output_path}")
    if args.upload and any(item["upload_status"] != "uploaded" for item in results):
        raise SystemExit("One or more clinical uploads failed.")


if __name__ == "__main__":
    main()
