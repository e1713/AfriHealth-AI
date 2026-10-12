import os
import json
import re
import asyncio
import argparse
import csv
from pathlib import Path
from statistics import fmean

from clinical_validation_evaluator import (
    calculate_mwer as clinical_calculate_mwer,
    calculate_target_term_recall,
    contains_term,
    normalize_clinical_text,
)

try:
    import jiwer
except ImportError:
    jiwer = None

DATASET_INDEX_PATH = os.getenv("DATASET_INDEX", "./evaluation_dataset.json")
OUTPUT_REPORT_PATH = os.getenv("OUTPUT_REPORT", "./benchmark_report.json")
OUTPUT_MARKDOWN_PATH = os.getenv("OUTPUT_MARKDOWN", "./BENCHMARK_RESULTS.md")
AFRISWITCH_ROOT = Path(os.getenv("AFRISWITCH_ROOT", "./clinical_validation/afriswitch"))

INTRON_API_KEY = os.getenv("INTRON_API_KEY", "")

CLINICAL_ENTITIES = [
    "fever", "cough", "headache", "hypertension", "diabetes", "paracetamol",
    "amoxicillin", "metformin", "bp", "pulse", "chills", "tb", "malaria",
    "pneumonia", "dyspnea", "tachycardia", "tuberculosis", "mg", "ml"
]

def calculate_wer(reference: str, hypothesis: str) -> float:
    normalized_reference = normalize_clinical_text(reference)
    normalized_hypothesis = normalize_clinical_text(hypothesis)
    if jiwer is not None:
        return float(jiwer.wer(normalized_reference, normalized_hypothesis))
    ref_words = normalized_reference.split()
    hyp_words = normalized_hypothesis.split()
    if not ref_words:
        return 0.0 if not hyp_words else 1.0
    distances = list(range(len(hyp_words) + 1))
    for ref_word in ref_words:
        next_distances = [distances[0] + 1]
        for index, hyp_word in enumerate(hyp_words, start=1):
            substitution = distances[index - 1] + (ref_word != hyp_word)
            insertion = next_distances[index - 1] + 1
            deletion = distances[index] + 1
            next_distances.append(min(substitution, insertion, deletion))
        distances = next_distances
    return distances[-1] / len(ref_words)

def calculate_entity_recall(
    reference: str,
    hypothesis: str,
    target_terms: str | list[str] | None = None,
) -> float:
    if target_terms is not None:
        terms = (
            [term.strip().strip('"') for term in target_terms.split(";") if term.strip()]
            if isinstance(target_terms, str)
            else target_terms
        )
        return calculate_target_term_recall(reference, hypothesis, terms)

    target_entities = [entity for entity in CLINICAL_ENTITIES if contains_term(reference, entity)]
    if not target_entities:
        return 1.0
    return calculate_target_term_recall(reference, hypothesis, target_entities)


def calculate_mwer(
    reference: str,
    hypothesis: str,
    target_terms: str | list[str] | None = None,
) -> float:
    if target_terms is None:
        target_terms = [entity for entity in CLINICAL_ENTITIES if contains_term(reference, entity)]
        if not target_terms:
            return 0.0
    terms = (
        [term.strip().strip('"') for term in target_terms.split(";") if term.strip()]
        if isinstance(target_terms, str)
        else target_terms
    )
    return clinical_calculate_mwer(reference, hypothesis, terms)

DEFAULT_BENCHMARK_SAMPLES = [
    {
        "id": "sample_001",
        "audio_path": "./samples/sample_001.wav",
        "reference": "patient unique identification. patient presents with severe headache and fever spanning 3 days. prescribed paracetamol 500mg twice daily.",
        "language_pair": "English-Amharic Code-Switch",
        "hypotheses": {
            "Intron Sahara v2.5": "patient unique identification. patient presents with severe headache and fever spanning 3 days. prescribed paracetamol 500mg twice daily.",
            "OpenAI Whisper Tiny": "patient unique identification patient present with severe headache and high fever 3 days prescribed paracetamol 500 daily",
            "Meta Wav2Vec2 Base 960h (English)": "patient unique identification patient severe headache fever 3 days prescribed paracetamol"
        }
    },
    {
        "id": "sample_002",
        "audio_path": "./samples/sample_002.wav",
        "reference": "የጤና ተቋም። chief complaint is chest pain with short breath. clinical assessment shows blood pressure 140 over 90.",
        "language_pair": "English-Amharic Code-Switch",
        "hypotheses": {
            "Intron Sahara v2.5": "የጤና ተቋም። chief complaint is chest pain with short breath. clinical assessment shows blood pressure 140 over 90.",
            "OpenAI Whisper Tiny": "የጤና ተቋም chief complaint chest pain short breath blood pressure 140 over 90",
            "Meta Wav2Vec2 Base 960h (English)": "chief complaint chest pain short breath blood pressure 140 90"
        }
    },
    {
        "id": "sample_003",
        "audio_path": "./samples/sample_003.wav",
        "reference": "patient has suspected malaria and pneumonia. recommended amoxicillin 500mg and urgent lab workup.",
        "language_pair": "English Clinical Standard",
        "hypotheses": {
            "Intron Sahara v2.5": "patient has suspected malaria and pneumonia. recommended amoxicillin 500mg and urgent lab workup.",
            "OpenAI Whisper Tiny": "patient suspected malaria and pneumonia recommended amoxicillin 500mg urgent lab workup",
            "Meta Wav2Vec2 Base 960h (English)": "patient suspect malaria pneumonia recommended amoxicillin lab workup"
        }
    },
    {
        "id": "sample_004",
        "audio_path": "./samples/sample_004.wav",
        "reference": "patient reports fever and cough for 2 days. oxygen saturation is low and there is wheezing in the lungs.",
        "language_pair": "English Clinical Standard",
        "hypotheses": {
            "Intron Sahara v2.5": "patient reports fever and cough for 2 days. oxygen saturation is low and there is wheezing in the lungs.",
            "OpenAI Whisper Tiny": "patient reports fever cough for 2 days oxygen saturation low wheezing in lungs",
            "Meta Wav2Vec2 Base 960h (English)": "patient fever cough 2 days low oxygen saturation wheezing lungs"
        }
    },
    {
        "id": "sample_005",
        "audio_path": "./samples/sample_005.wav",
        "reference": "የህሙም በሽታ አብዛኛውን ጊዜ በእግር ህመም እና በቫይታሚን እጥረት ተገኝቷል። doctor advised metformin 500mg once daily and hydration.",
        "language_pair": "English-Amharic Code-Switch",
        "hypotheses": {
            "Intron Sahara v2.5": "የህሙም በሽታ አብዛኛውን ጊዜ በእግር ህመም እና በቫይታሚን እጥረት ተገኝቷል። doctor advised metformin 500mg once daily and hydration.",
            "OpenAI Whisper Tiny": "ህመም በእግር ህመም እና ቫይታሚን እጥረት ተገኝቷል doctor advised metformin 500 once daily hydration",
            "Meta Wav2Vec2 Base 960h (English)": "ህመም በእግር ህመም እና ቫይታሚን እጥረት doctor advised metformin once daily"
        }
    },
    {
        "id": "sample_006",
        "audio_path": "./samples/sample_006.wav",
        "reference": "patient reports abdominal pain and diarrhea for 4 days. blood pressure is 110 over 70 and pulse is elevated.",
        "language_pair": "English Clinical Standard",
        "hypotheses": {
            "Intron Sahara v2.5": "patient reports abdominal pain and diarrhea for 4 days. blood pressure is 110 over 70 and pulse is elevated.",
            "OpenAI Whisper Tiny": "patient reports abdominal pain diarrhea 4 days blood pressure 110 over 70 pulse elevated",
            "Meta Wav2Vec2 Base 960h (English)": "patient abdominal pain diarrhea 4 days blood pressure 110 70 pulse elevated"
        }
    }
]


def load_benchmark_samples() -> list[dict]:
    dataset_dir = Path(os.getenv("BENCHMARK_DATASET_DIR", "./benchmark_data"))
    manifest_path = dataset_dir / "manifest.csv"
    if manifest_path.exists():
        with manifest_path.open(encoding="utf-8", newline="") as manifest_file:
            rows = list(csv.DictReader(manifest_file))
        inference_metadata_path = dataset_dir / "inference_metadata.json"
        inference_models = {}
        if inference_metadata_path.is_file():
            inference_models = json.loads(inference_metadata_path.read_text(encoding="utf-8")).get("models", {})
        openai_model_id = inference_models.get("openai", {}).get("model_id", "gpt-4o-mini-transcribe")
        gemini_model_id = inference_models.get("gemini", {}).get("model_id", "gemini-flash-latest")
        items = []
        model_columns = {
            "Intron Sahara v2.5": "intron_hypothesis",
            "OpenAI Whisper Tiny": "whisper_hypothesis",
            "Meta Wav2Vec2 Base 960h (English)": "wav2vec2_hypothesis",
            f"OpenAI {openai_model_id}": "openai_hypothesis",
            f"Google Gemini {gemini_model_id}": "gemini_hypothesis",
        }
        for row in rows:
            sample_id = (row.get("sample_id") or row.get("id") or "").strip()
            audio_file = (row.get("audio_file") or row.get("audio_path") or "").strip()
            if not sample_id or not audio_file:
                continue
            audio_path = (dataset_dir / audio_file).as_posix() if not audio_file.startswith("/") else audio_file
            items.append({
                "id": sample_id,
                "case_id": (row.get("case_id") or sample_id).strip(),
                "audio_path": audio_path,
                "source_audio_file": (row.get("source_audio_file") or "").strip(),
                "reference": (row.get("reference") or row.get("gold_standard") or "").strip(),
                "target_terms": (row.get("target_terms") or "").strip(),
                "language_pair": (row.get("language_pair") or "Not provided").strip(),
                "reference_source": (row.get("reference_source") or "").strip(),
                "consent_obtained": (row.get("consent_obtained") or "").strip(),
                "de_identified": (row.get("de_identified") or "").strip(),
                "annotator_count": (row.get("annotator_count") or "").strip(),
                "reference_verified": (row.get("reference_verified") or "").strip().lower() in {"true", "1", "yes"},
                "verified_gold_standard": (row.get("verified_gold_standard") or "").strip().lower() in {"true", "1", "yes"},
                "duplicate_of": (row.get("duplicate_of") or "").strip(),
                "hypotheses": {
                    model: row[column].strip()
                    for model, column in model_columns.items()
                    if row.get(column, "").strip()
                },
            })
        return items

    json_manifest = dataset_dir / "manifest.json"
    if json_manifest.exists():
        payload = json.loads(json_manifest.read_text(encoding="utf-8"))
        if isinstance(payload, list) and payload:
            return payload

    return DEFAULT_BENCHMARK_SAMPLES


BENCHMARK_SAMPLES = load_benchmark_samples()


def unique_benchmark_samples(samples: list[dict]) -> list[dict]:
    return [sample for sample in samples if not sample.get("duplicate_of")]


def available_optional_models(samples: list[dict]) -> list[str]:
    base_models = {
        "Intron Sahara v2.5",
        "OpenAI Whisper Tiny",
        "Meta Wav2Vec2 Base 960h (English)",
    }
    optional_models = []
    for sample in samples:
        for model in sample.get("hypotheses", {}):
            if (
                model not in base_models
                and model.startswith(("OpenAI ", "Google Gemini "))
                and model not in optional_models
            ):
                optional_models.append(model)
    available = []
    for model in optional_models:
        counts = [bool(sample.get("hypotheses", {}).get(model)) for sample in samples]
        if any(counts) and not all(counts):
            raise ValueError(f"Partial hypotheses exist for {model}; complete all samples or clear that provider column.")
        if counts and all(counts):
            available.append(model)
    return available


def validate_benchmark_samples(samples: list[dict], models: list[str]) -> None:
    if not samples:
        raise ValueError("No benchmark samples are available.")
    incomplete = [
        item["id"]
        for item in samples
        if not item.get("reference")
        or ("target_terms" in item and not item.get("target_terms"))
        or (
            "reference_verified" in item
            and not item["reference_verified"]
            and not item.get("verified_gold_standard")
        )
        or any(not item.get("hypotheses", {}).get(model) for model in models)
    ]
    if incomplete:
        sample_ids = ", ".join(incomplete[:5])
        suffix = "..." if len(incomplete) > 5 else ""
        raise ValueError(
            f"Cannot calculate benchmark metrics: {len(incomplete)} sample(s) lack "
            f"a verified reference transcript, target terms, or model hypothesis ({sample_ids}{suffix})."
        )

def run_afriswitch_pilot(root: Path) -> None:
    """Validate the imported pilot and report reference coverage only."""
    manifest_dir = root / "manifests"
    metadata_path = root / "import_metadata.json"
    if not manifest_dir.is_dir() or not metadata_path.is_file():
        raise FileNotFoundError(
            f"AfriSwitch import not found at {root}. Run afriswitch_import.py first."
        )

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    configs = {}
    total_duration = 0.0
    for manifest_path in sorted(manifest_dir.glob("*.csv")):
        rows = list(csv.DictReader(manifest_path.open(encoding="utf-8", newline="")))
        missing_audio = sum(
            not (root / row["local_audio"]).is_file()
            for row in rows
        )
        duration = sum(float(row["duration"]) for row in rows if row.get("duration"))
        switches = sum(int(row["num_switch_points"]) for row in rows if row.get("num_switch_points"))
        configs[manifest_path.stem] = {
            "utterances": len(rows),
            "audio_files": len(rows) - missing_audio,
            "missing_audio": missing_audio,
            "duration_seconds": round(duration, 2),
            "switch_points": switches,
        }
        total_duration += duration

    report = {
        "dataset_id": metadata["dataset_id"],
        "dataset_revision": metadata["dataset_revision"],
        "split": metadata["split"],
        "license": metadata["license"],
        "configs": configs,
        "total_utterances": sum(item["utterances"] for item in configs.values()),
        "total_duration_seconds": round(total_duration, 2),
        "evaluation_status": "reference_only",
        "note": "No model hypotheses were supplied; WER and model rankings are intentionally not reported.",
    }
    output_path = root / "afriswitch_pilot_report.json"
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"Pilot report exported to {output_path}")

async def run_benchmark():
    models = ["Intron Sahara v2.5", "OpenAI Whisper Tiny", "Meta Wav2Vec2 Base 960h (English)"]
    scoring_samples = unique_benchmark_samples(BENCHMARK_SAMPLES)
    manifest_path = Path(os.getenv("BENCHMARK_DATASET_DIR", "./benchmark_data")) / "manifest.csv"
    uses_target_terms = manifest_path.is_file()
    recall_key = "mean_target_term_recall" if uses_target_terms else "mean_lexicon_entity_recall"
    models.extend(available_optional_models(scoring_samples))
    validate_benchmark_samples(scoring_samples, models)

    print("============================================================")
    print("Starting Multi-Model Speech Recognition Benchmark...")
    print("Models: Intron Sahara v2.5 | OpenAI Whisper Tiny | Meta Wav2Vec2 Base 960h (English)")
    print("============================================================")

    results = {m: {"wers": [], "target_recalls": [], "mwers": []} for m in models}

    for item in scoring_samples:
        ref = item["reference"]
        for model_name in models:
            hyp = item["hypotheses"][model_name]
            wer = calculate_wer(ref, hyp)
            entity_recall = calculate_entity_recall(
                ref,
                hyp,
                item.get("target_terms") if uses_target_terms else None,
            )
            mwer = calculate_mwer(
                ref,
                hyp,
                item.get("target_terms") if uses_target_terms else None,
            )
            results[model_name]["wers"].append(wer)
            results[model_name]["target_recalls"].append(entity_recall)
            results[model_name]["mwers"].append(mwer)

    summary = {}
    print("\n============================================================")
    print("FINAL BENCHMARK RESULTS")
    print("============================================================")

    for m in models:
        mean_wer = fmean(results[m]["wers"])
        mean_target_recall = fmean(results[m]["target_recalls"])
        mean_mwer = fmean(results[m]["mwers"])
        summary[m] = {
            "mean_normalized_wer": round(mean_wer, 4),
            "mean_wer": round(mean_wer, 4),
            recall_key: round(mean_target_recall, 4),
            "mean_mwer": round(mean_mwer, 4),
            "sample_count": len(scoring_samples),
        }
        print(f"Model: {m}")
        print(f"  - Mean Normalized WER: {summary[m]['mean_normalized_wer'] * 100:.2f}%")
        print(f"  - {'Target-Term' if uses_target_terms else 'Lexicon Entity'} Recall: {mean_target_recall * 100:.2f}%")
        print(f"  - Mean M-WER: {summary[m]['mean_mwer'] * 100:.2f}%\n")

    with open(OUTPUT_REPORT_PATH, "w") as f:
        json.dump(summary, f, indent=2)

    if manifest_path.is_file():
        report_title = "# Clinical Audio Dataset Benchmark Report"
        evidence_note = (
            f"Results were scored from {len(scoring_samples)} manifest-selected recordings against verified references. "
            "Model checkpoints and inference settings are recorded in `benchmark_data/inference_metadata.json`."
        )
        intron_status = "Measured hosted ASR"
        whisper_status = "Measured local ASR"
        wav2vec_status = "English-only local baseline; checkpoint in inference metadata"
        recall_label = "Mean Target-Term Recall"
        recall_method = (
            "For each recording, the fraction of semicolon-separated manifest target terms "
            "matched by normalized tokens; parenthetical bilingual alternatives are accepted."
        )
    else:
        report_title = "# Fixture Speech Recognition Benchmark Report"
        evidence_note = (
            "This is a reproducible software fixture, not an independent audio benchmark. "
            "Hypotheses are embedded in `benchmark_suite.py`; do not present these values as production performance."
        )
        intron_status = "Fixture reference"
        whisper_status = "Fixture baseline"
        wav2vec_status = "Fixture baseline"
        recall_label = "Mean Fixed-Lexicon Entity Recall"
        recall_method = "Recall of the fixed English clinical keyword list in the reference."

    model_status = {
        "Intron Sahara v2.5": intron_status,
        "OpenAI Whisper Tiny": whisper_status,
        "Meta Wav2Vec2 Base 960h (English)": wav2vec_status,
    }
    for model in models:
        if model.startswith(("OpenAI ", "Google Gemini ")):
            model_status.setdefault(model, "Measured hosted ASR")
    report_rows = []
    for model in models:
        values = summary[model]
        report_rows.append(
            f"| {model} | {values['mean_normalized_wer'] * 100:.2f}% | "
            f"{values[recall_key] * 100:.2f}% | "
            f"{values['mean_mwer'] * 100:.2f}% | "
            f"{model_status.get(model, 'Measured ASR')} |"
        )
    model_table_rows = "\n".join(report_rows)

    md_content = f"""{report_title}

> **Evidence status:** {evidence_note}

| Model | Normalized WER ↓ | {recall_label} ↑ | M-WER ↓ | Status |
| :--- | :---: | :---: | :---: | :--- |
{model_table_rows}

### Evaluation Methodology
1. **Normalized WER**: Clinical text normalization standardizes punctuation, common units, and selected transliterations before whitespace-token Levenshtein scoring (using `jiwer` when installed).
2. **{recall_label}**: {recall_method} Clinical aliases may match English, Amharic, and transliterated variants.
3. **M-WER**: `1 - target-term recall`, calculated per sample then averaged; lower is better.
4. **Fairness**: No demographic or subgroup fairness metric is computed in this benchmark.

The separate 15-case clinical validation baseline reported 56.38% mean WER,
44.33% target-term recall, and critical-term misses in 6 cases. That result is
for clinician review only and does not support autonomous clinical use.
"""
    with open(OUTPUT_MARKDOWN_PATH, "w") as f:
        f.write(md_content)

    print(f"Report exported to {OUTPUT_REPORT_PATH} and {OUTPUT_MARKDOWN_PATH}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the fixture benchmark or validate the AfriSwitch pilot.")
    parser.add_argument(
        "--afriswitch-pilot",
        action="store_true",
        help="Generate a reference-only report from the imported AfriSwitch pilot.",
    )
    parser.add_argument(
        "--afriswitch-root",
        default=str(AFRISWITCH_ROOT),
        help="Path to the imported AfriSwitch directory.",
    )
    args = parser.parse_args()
    if args.afriswitch_pilot:
        run_afriswitch_pilot(Path(args.afriswitch_root))
    else:
        asyncio.run(run_benchmark())
