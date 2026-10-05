"""Backward-compatible entry point to the unified inference engine.

Model hypotheses are stored in results/, never written back into the master
benchmark manifest.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from inference_engine import InferenceEngine, MODEL_TYPES


LEGACY_MODEL_MAP = {
    "intron": "sahara",
    "whisper": "whisper",
    "wav2vec": "wav2vec2",
    "gemini": "gemini",
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run model inference against the authoritative 100-case manifest."
    )
    parser.add_argument(
        "--only",
        choices=("all", *LEGACY_MODEL_MAP),
        default="all",
        help="Optional legacy model selector; results are written under results/.",
    )
    parser.add_argument(
        "--env",
        choices=("mock", "live"),
        default="mock",
        help="mock is safe/offline; live requires manifest approvals and provider keys.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Repository root.",
    )
    args = parser.parse_args(argv)
    model_keys = (
        tuple(MODEL_TYPES)
        if args.only == "all"
        else (LEGACY_MODEL_MAP[args.only],)
    )
    engine = InferenceEngine(
        args.root,
        environment=args.env,
        model_keys=model_keys,
    )
    try:
        return engine.run()
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Inference failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
