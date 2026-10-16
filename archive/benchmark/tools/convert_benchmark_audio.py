import argparse
import csv
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path


def is_expected_wav(path: Path) -> bool:
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_name,sample_fmt,sample_rate,channels",
            "-of", "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    streams = json.loads(result.stdout).get("streams", [])
    return bool(streams) and all(
        stream.get("codec_name") == "pcm_s16le"
        and stream.get("sample_fmt") == "s16"
        and stream.get("sample_rate") == "16000"
        and stream.get("channels") == 1
        for stream in streams
    )


def convert_manifest_audio(
    manifest_path: Path,
    output_dir: Path,
    force: bool = False,
) -> int:
    manifest_path = manifest_path.resolve()
    dataset_dir = manifest_path.parent
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    with manifest_path.open(encoding="utf-8", newline="") as manifest_file:
        reader = csv.DictReader(manifest_file)
        fieldnames = reader.fieldnames
        rows = list(reader)
    if not fieldnames or not rows:
        raise ValueError(f"Manifest is empty: {manifest_path}")
    if "audio_file" not in fieldnames or "sample_id" not in fieldnames:
        raise ValueError("Manifest must contain sample_id and audio_file columns")

    converted = []
    for row in rows:
        sample_id = row["sample_id"].strip()
        if not re.fullmatch(r"[A-Za-z0-9._-]+", sample_id):
            raise ValueError(f"Unsupported sample_id for output filename: {sample_id!r}")

        source_relative = (row.get("source_audio_file") or row["audio_file"]).strip()
        source_path = (dataset_dir / source_relative).resolve()
        try:
            source_path.relative_to(dataset_dir.resolve())
        except ValueError as error:
            raise ValueError(f"Audio path escapes dataset directory: {source_relative}") from error
        if not source_path.is_file():
            raise FileNotFoundError(source_path)

        output_path = output_dir / f"{sample_id}.wav"
        if output_path.exists() and not force:
            if not is_expected_wav(output_path):
                raise ValueError(f"Existing WAV has unexpected format: {output_path}; use --force")
        else:
            with tempfile.NamedTemporaryFile(suffix=".wav", dir=output_dir, delete=False) as temporary:
                temporary_path = Path(temporary.name)
            try:
                subprocess.run(
                    [
                        "ffmpeg", "-nostdin", "-v", "error", "-y",
                        "-i", str(source_path),
                        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
                        str(temporary_path),
                    ],
                    check=True,
                )
                if not is_expected_wav(temporary_path):
                    raise ValueError(f"Converted WAV failed format validation: {temporary_path}")
                os.replace(temporary_path, output_path)
            finally:
                temporary_path.unlink(missing_ok=True)

        converted.append((row, source_relative, output_path))

    if "source_audio_file" not in fieldnames:
        audio_index = fieldnames.index("audio_file")
        fieldnames.insert(audio_index + 1, "source_audio_file")
    for row, source_relative, output_path in converted:
        row["source_audio_file"] = source_relative
        row["audio_file"] = output_path.relative_to(dataset_dir).as_posix()

    with manifest_path.open("w", encoding="utf-8", newline="") as manifest_file:
        writer = csv.DictWriter(manifest_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return len(converted)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert benchmark manifest audio to mono 16 kHz PCM WAV.")
    parser.add_argument("--manifest", type=Path, default=Path("benchmark_data/manifest.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("benchmark_data/wav"))
    parser.add_argument("--force", action="store_true", help="Replace existing WAV outputs.")
    args = parser.parse_args()
    count = convert_manifest_audio(args.manifest, args.output_dir, force=args.force)
    print(f"Converted and validated {count} manifest recordings.")


if __name__ == "__main__":
    main()