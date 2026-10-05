"""Validate source WAVs and create mono, 16 kHz PCM benchmark copies."""

from __future__ import annotations

import argparse
import os
import statistics
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, TextIO


TARGET_SAMPLE_RATE = 16_000
PROJECT_DIRECTORIES = (
    "raw_audio",
    "cleaned_audio",
    "transcripts",
    "results",
    "dictionaries",
)


@dataclass(frozen=True)
class AudioMetadata:
    duration_seconds: float
    sample_rate: int
    channels: int


def create_project_directories(root: Path) -> dict[str, Path]:
    """Create and return the standard audio-benchmark directories."""
    directories = {name: root / name for name in PROJECT_DIRECTORIES}
    for directory in directories.values():
        directory.mkdir(parents=True, exist_ok=True)
    return directories


def find_wav_files(raw_audio_dir: Path) -> list[Path]:
    """Find WAV files recursively, without following directory symlinks."""
    return sorted(
        (
            path
            for path in raw_audio_dir.rglob("*")
            if path.is_file() and not path.is_symlink() and path.suffix.lower() == ".wav"
        ),
        key=lambda path: path.as_posix().casefold(),
    )


def prepare_audio_file(
    source: Path,
    destination: Path,
    *,
    light_normalize: bool = False,
    light_denoise: bool = False,
) -> AudioMetadata:
    """Decode, standardize, and atomically write one WAV file."""
    import librosa
    import numpy as np
    import soundfile as sf

    audio, sample_rate = sf.read(source, dtype="float32", always_2d=True)
    channels = int(audio.shape[1])
    if sample_rate <= 0 or audio.shape[0] == 0:
        raise ValueError("audio has no samples or an invalid sample rate")
    if not np.isfinite(audio).all():
        raise ValueError("audio contains non-finite sample values")

    duration = audio.shape[0] / sample_rate
    mono = librosa.to_mono(audio.T)
    if sample_rate != TARGET_SAMPLE_RATE:
        mono = librosa.resample(
            mono,
            orig_sr=sample_rate,
            target_sr=TARGET_SAMPLE_RATE,
        )

    if light_denoise:
        import noisereduce

        mono = noisereduce.reduce_noise(
            y=mono,
            sr=TARGET_SAMPLE_RATE,
            prop_decrease=0.3,
            stationary=False,
        )
        if not np.isfinite(mono).all():
            raise ValueError("light denoising produced non-finite sample values")

    if light_normalize:
        peak = float(np.max(np.abs(mono))) if mono.size else 0.0
        target_peak = 10 ** (-1 / 20)
        maximum_gain = 10 ** (3 / 20)
        if peak > 0:
            mono = mono * min(target_peak / peak, maximum_gain)

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{destination.stem}.",
            suffix=".wav",
            dir=destination.parent,
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)

        sf.write(
            temporary_path,
            mono,
            TARGET_SAMPLE_RATE,
            format="WAV",
            subtype="PCM_16",
        )
        output_info = sf.info(temporary_path)
        if (
            output_info.samplerate != TARGET_SAMPLE_RATE
            or output_info.channels != 1
            or output_info.format != "WAV"
            or output_info.subtype != "PCM_16"
        ):
            raise ValueError("standardized output did not pass format verification")
        os.replace(temporary_path, destination)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return AudioMetadata(
        duration_seconds=duration,
        sample_rate=int(sample_rate),
        channels=channels,
    )


def format_duration_distribution(durations: Sequence[float]) -> str:
    if not durations:
        return "Duration distribution: unavailable (no readable WAV files)"
    return (
        "Duration distribution (seconds): "
        f"min={min(durations):.2f}, "
        f"median={statistics.median(durations):.2f}, "
        f"mean={statistics.mean(durations):.2f}, "
        f"max={max(durations):.2f}"
    )


def run_validation(
    root: Path,
    *,
    light_normalize: bool = False,
    light_denoise: bool = False,
    output: TextIO = sys.stdout,
) -> int:
    directories = create_project_directories(root)
    files = find_wav_files(directories["raw_audio"])
    print(f"Created/verified benchmark folders under: {root}", file=output)
    print(f"Found {len(files)} WAV file(s) in {directories['raw_audio']}", file=output)

    if not files:
        print("ERROR: No WAV files found; add the source recordings and retry.", file=output)
        return 1
    if light_denoise:
        print(
            "NOTICE: Light spectral denoising is enabled (prop_decrease=0.3). "
            "Review outputs against the untouched recordings.",
            file=output,
        )
    if not light_normalize and not light_denoise:
        print("Gentle preprocessing is disabled; source acoustic levels are preserved.", file=output)

    durations: list[float] = []
    mono_count = 0
    stereo_count = 0
    other_channel_count = 0
    failure_count = 0

    for source in files:
        relative_path = source.relative_to(directories["raw_audio"])
        destination = directories["cleaned_audio"] / relative_path
        try:
            metadata = prepare_audio_file(
                source,
                destination,
                light_normalize=light_normalize,
                light_denoise=light_denoise,
            )
        except (ImportError, OSError, RuntimeError, ValueError) as error:
            failure_count += 1
            print(f"ERROR {relative_path}: {error}", file=output)
            continue

        durations.append(metadata.duration_seconds)
        if metadata.channels == 1:
            mono_count += 1
            layout = "mono"
        elif metadata.channels == 2:
            stereo_count += 1
            layout = "stereo"
        else:
            other_channel_count += 1
            layout = f"{metadata.channels}-channel"
        print(
            f"OK {relative_path}: {metadata.duration_seconds:.2f}s, "
            f"{metadata.sample_rate} Hz, {layout} -> {destination}",
            file=output,
        )

    print(
        f"Summary: prepared={len(durations)}, failed={failure_count}, "
        f"mono={mono_count}, stereo={stereo_count}, "
        f"other_channel_layouts={other_channel_count}",
        file=output,
    )
    print(format_duration_distribution(durations), file=output)
    return 1 if failure_count else 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate raw WAV files and create mono, 16 kHz, PCM WAV copies "
            "in cleaned_audio/."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Project root containing raw_audio/ (default: this script's directory).",
    )
    parser.add_argument(
        "--light-normalize",
        action="store_true",
        help="Apply peak normalization toward -1 dBFS, capped at +3 dB gain.",
    )
    parser.add_argument(
        "--light-denoise",
        action="store_true",
        help="Opt in to non-stationary spectral gating at prop_decrease=0.3.",
    )
    args = parser.parse_args(argv)
    return run_validation(
        args.root.resolve(),
        light_normalize=args.light_normalize,
        light_denoise=args.light_denoise,
    )


if __name__ == "__main__":
    sys.exit(main())
