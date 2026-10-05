"""Compatibility entry point for the authoritative 100-case benchmark pipeline.

Use ``evaluator.py`` for clinical benchmark scoring. The small metric helpers
remain available for the separate general-purpose AfriSwitch experiment.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from clinical_validation_evaluator import (
    calculate_target_term_recall,
    normalize_clinical_text,
)
from evaluator import calculate_wer as calculate_pipeline_wer
from evaluator import contains_term, load_medical_terms
from evaluator import main as evaluator_main


def calculate_wer(reference: str, hypothesis: str) -> float:
    """Calculate normalized WER with the established clinical normalizer."""
    return calculate_pipeline_wer(
        normalize_clinical_text(reference),
        normalize_clinical_text(hypothesis),
    )


def calculate_entity_recall(
    reference: str,
    hypothesis: str,
    target_terms: str | list[str] | None = None,
) -> float:
    """Calculate recall for dictionary terms present in the reference."""
    if target_terms is not None:
        terms = (
            [term.strip().strip('"') for term in target_terms.split(";") if term.strip()]
            if isinstance(target_terms, str)
            else target_terms
        )
        return calculate_target_term_recall(reference, hypothesis, terms)
    dictionary_path = Path(__file__).resolve().parent / "dictionaries" / "medical_terms.json"
    categories = load_medical_terms(dictionary_path)
    reference_terms = {
        term
        for terms in categories.values()
        for term in terms
        if contains_term(reference, term)
    }
    if not reference_terms:
        return 1.0
    return sum(contains_term(hypothesis, term) for term in reference_terms) / len(reference_terms)


def calculate_entity_accuracy(reference: str, hypothesis: str) -> float:
    """Retain the legacy AfriSwitch helper name; this is entity recall, not accuracy."""
    return calculate_entity_recall(reference, hypothesis)


def main(argv: Sequence[str] | None = None) -> int:
    """Delegate benchmark scoring to the evaluator's manifest-based pipeline."""
    parser = argparse.ArgumentParser(
        description="Run evaluation using benchmark/metadata/BENCHMARK_MANIFEST.csv."
    )
    parser.add_argument(
        "--afriswitch-pilot",
        action="store_true",
        help="Removed: AfriSwitch pilot scoring is separate from this clinical benchmark.",
    )
    args, remaining = parser.parse_known_args(argv)
    if args.afriswitch_pilot:
        print(
            "AfriSwitch is a separate non-clinical dataset. Use "
            "afriswitch_asr_benchmark.py for that experiment.",
            file=sys.stderr,
        )
        return 2
    return evaluator_main(remaining)


if __name__ == "__main__":
    raise SystemExit(main())
