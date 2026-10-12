"""Score private clinical ASR results and emit a privacy-safe aggregate report."""

import argparse
import json
import re
from pathlib import Path


CRITICAL_TERMS = {
    "CS-02": ["Amoxicillin", "500mg", "TID"],
    "CS-05": ["125mg/5mL", "PO TID"],
    "CS-06": ["Metformin", "BID"],
    "CS-09": ["38 weeks", "ruptured membranes"],
    "CS-11": ["GeneXpert", "TB"],
    "CS-14": ["Ceftriaxone"],
    "CS-15": ["meningitis"],
}


CLINICAL_ALIASES = {
    "headache": ("headache", "ras mathat", "ras matat", "rasmathat", "ራስ ምታት"),
    "fever": ("fever", "tksat", "ትኩሳት"),
    "paracetamol": ("paracetamol", "acetaminophen"),
    "cough": ("cough", "ሳል"),
    "shortness of breath": ("shortness of breath", "dyspnea", "difficulty breathing", "ትንፋሽ ማጠር"),
    "diarrhea": ("diarrhea", "diarrhoea", "ተቅማጥ"),
    "vomiting": ("vomiting", "emesis", "ማስታወክ"),
    "hypertension": ("hypertension", "high blood pressure", "የደም ግፊት"),
    "amoxicillin": ("amoxicillin", "amoxacillin"),
    "metformin": ("metformin",),
    "malaria": ("malaria", "ወባ"),
    "obstetric history": ("g3p2", "gravida 3 para 2"),
    "right lower quadrant": ("rlq", "right lower quadrant"),
    "intravenous saline": ("iv saline", "iv normal saline", "normal saline"),
}


def normalize_clinical_text(text: str) -> str:
    normalized = (text or "").lower()
    normalized = re.sub(r"\bras\s*matat\b|\brasmathat\b|\bras\s*mathat\b", "ras mathat", normalized)
    normalized = re.sub(r"(\d+(?:\.\d+)?)\s*mg\s*/\s*(\d+(?:\.\d+)?)\s*ml\b", r"\1 milligrams per \2 milliliters", normalized)
    normalized = re.sub(r"(\d+(?:\.\d+)?)\s*mg\s*/\s*dl\b", r"\1 milligrams per deciliter", normalized)
    normalized = re.sub(r"(\d+(?:\.\d+)?)\s*mg\b", r"\1 milligrams", normalized)
    normalized = re.sub(r"(\d+(?:\.\d+)?)\s*ml\b", r"\1 milliliters", normalized)
    normalized = re.sub(r"(\d+(?:\.\d+)?)\s*mcg\b", r"\1 micrograms", normalized)
    normalized = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"\1 percent", normalized)
    normalized = re.sub(r"\bmmhg\b", "millimeters of mercury", normalized)
    normalized = re.sub(r"[\u1360-\u136f]", " ", normalized)
    normalized = re.sub(r"[^\w\s\u1200-\u137f]", " ", normalized, flags=re.UNICODE)
    return " ".join(normalized.split())


def tokens(value: str) -> list[str]:
    return normalize_clinical_text(value).split()


def wer(reference: str, hypothesis: str) -> float:
    expected = tokens(reference)
    actual = tokens(hypothesis)
    previous = list(range(len(actual) + 1))
    for row, expected_token in enumerate(expected, start=1):
        current = [row]
        for column, actual_token in enumerate(actual, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[column] + 1,
                    previous[column - 1] + (expected_token != actual_token),
                )
            )
        previous = current
    return previous[-1] / max(1, len(expected))


def _target_alternatives(target_term: str) -> list[str]:
    alternatives = []
    for part in target_term.split(";"):
        parenthetical = re.findall(r"\(([^()]*)\)", part)
        primary = re.sub(r"\s*\([^()]*\)", "", part).strip()
        alternatives.extend(term for term in (primary, *parenthetical) if term.strip())
    return alternatives


def _contains_term_tokens(normalized_text: str, normalized_term: str) -> bool:
    term_tokens = set(normalized_term.split())
    return bool(term_tokens) and term_tokens.issubset(set(normalized_text.split()))


def contains_term(hypothesis: str, term: str) -> bool:
    normalized_hypothesis = normalize_clinical_text(hypothesis)
    terms = _target_alternatives(term)
    for target in terms:
        normalized_target = normalize_clinical_text(target)
        if not normalized_target:
            continue
        candidates = {normalized_target}
        for canonical, aliases in CLINICAL_ALIASES.items():
            normalized_aliases = {normalize_clinical_text(alias) for alias in aliases}
            if normalized_target in normalized_aliases or any(
                _contains_term_tokens(normalized_target, alias) for alias in normalized_aliases
            ):
                candidates.update(normalized_aliases)
                candidates.add(normalize_clinical_text(canonical))
        if any(_contains_term_tokens(normalized_hypothesis, candidate) for candidate in candidates if candidate):
            return True
    return False


def calculate_target_term_recall(
    reference: str,
    hypothesis: str,
    target_terms: list[str],
) -> float:
    terms = [term.strip() for term in target_terms if term.strip()]
    if not terms:
        raise ValueError("target_terms must contain at least one clinical term")
    reference_terms = [term for term in terms if contains_term(reference, term)]
    if not reference_terms:
        raise ValueError("No target terms matched the reference transcript")
    matched_terms = sum(contains_term(hypothesis, term) for term in reference_terms)
    return matched_terms / len(reference_terms)


def calculate_mwer(reference: str, hypothesis: str, target_terms: list[str]) -> float:
    return 1.0 - calculate_target_term_recall(reference, hypothesis, target_terms)


def evaluate(results_path: Path, model_name: str) -> dict:
    private_results = json.loads(results_path.read_text(encoding="utf-8"))
    cases = []
    for item in private_results:
        response_data = item.get("response", {}).get("data", {})
        hypothesis = item.get("transcript") or response_data.get("audio_transcript", "")
        reference = item.get("reference_transcript", "")
        target_terms = [
            term.strip().strip('"')
            for term in item.get("target_terms", "").split(";")
            if term.strip()
        ]
        target_recall = calculate_target_term_recall(reference, hypothesis, target_terms)
        mwer = calculate_mwer(reference, hypothesis, target_terms)
        critical_terms = CRITICAL_TERMS.get(item["case_id"], [])
        critical_misses = [
            term for term in critical_terms if not contains_term(hypothesis, term)
        ]
        cases.append(
            {
                "case_id": item["case_id"],
                "wer": round(wer(reference, hypothesis), 4),
                "target_term_recall": round(target_recall, 4),
                "mwer": round(mwer, 4),
                "critical_term_miss_count": len(critical_misses),
            }
        )

    if not cases:
        raise ValueError("The private result file contains no cases.")
    return {
        "report_type": "clinical_asr_validation_aggregate",
        "report_version": "1.2",
        "evaluation_method": "normalized token-level WER, clinical alias target-term recall, and M-WER (1 - target-term recall)",
        "source": "reviewed simulated clinical recording results",
        "cases_evaluated": len(cases),
        "models": {
            model_name: {
                "cases": len(cases),
                "mean_normalized_wer": round(
                    sum(case["wer"] for case in cases) / len(cases), 4
                ),
                "mean_word_error_rate": round(
                    sum(case["wer"] for case in cases) / len(cases), 4
                ),
                "mean_target_term_recall": round(
                    sum(case["target_term_recall"] for case in cases) / len(cases), 4
                ),
                "mean_mwer": round(sum(case["mwer"] for case in cases) / len(cases), 4),
                "cases_with_critical_term_misses": sum(
                    case["critical_term_miss_count"] > 0 for case in cases
                ),
            }
        },
        "privacy": {
            "raw_audio": "excluded",
            "full_transcripts": "excluded",
            "provider_file_ids": "excluded",
            "per_case_error_details": "excluded",
        },
        "interpretation": {
            "status": "baseline_for_clinician_review",
            "autonomous_clinical_use": False,
            "note": "Critical-term misses require clinician review and must not be silently corrected by the application.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results",
        default=r"C:\Users\kingr\Desktop\clinical-validation-inputs\upload_results.json",
        help="Private upload result JSON; do not commit this file.",
    )
    parser.add_argument(
        "--output",
        default="clinical_validation_model_report.json",
        help="Aggregate output path.",
    )
    parser.add_argument(
        "--model-name",
        default="intron_sahara_v2.5",
        help="Stable model identifier for the aggregate report.",
    )
    args = parser.parse_args()
    report = evaluate(Path(args.results).resolve(), args.model_name)
    output_path = Path(args.output).resolve()
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(report["models"], indent=2))
    print(f"Aggregate report written to {output_path}")


if __name__ == "__main__":
    main()
