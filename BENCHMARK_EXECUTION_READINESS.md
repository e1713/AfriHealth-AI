# Benchmark Execution Readiness

## Assessment

**Overall: Prepare locally; do not start multi-model inference yet.** The canonical references, case IDs, audio mappings, and cleaned-audio checksums are synchronized. Manual transcript/audio/alignment review is user-attested. However, consent, de-identification, source rights, and provider-transfer approval remain unknown for all 100 cases, so hosted inference is blocked. This report does not authorize external data transfer.

| Model | Adapter state | Readiness | Blockers |
| --- | --- | --- | --- |
| Sahara / Intron | Hosted provider adapter implemented | **Blocked** | Per-case consent, de-identification, source rights, and Intron hosted-use approval are unknown; verify securely before setting flags/evidence |
| Gemini | Hosted provider adapter implemented | **Blocked** | Per-case consent, de-identification, source rights, and Gemini hosted-use approval are unknown; verify securely before setting flags/evidence |
| Whisper | Clinical pipeline adapter remains a placeholder | **Not executable in this pipeline** | Implement/validate an exact Whisper checkpoint and Amharic-English settings; separately establish data rights and review environment |

## Ready Components

- 100 unique reference cases and verified normalized transcripts from source `review_status=verified`.
- 100 matching raw and cleaned WAV files; 100 cleaned-file SHA-256 checksums match manifest values.
- Medical-entity/focus terms and source domain metadata are populated.
- Validation rejects manifest drift from canonical source, unsupported verification claims, and hosted approval without evidence.
- Mock pipeline and scoring tests pass; mock results are not model-performance evidence.

## Required Before Execution

1. Obtain and record per-case consent, de-identification review, source rights, retention requirements, and approval to transmit audio to each selected provider. Keep sensitive evidence in approved restricted storage; store only controlled references in the manifest.
2. Record reviewer identity and review date from the actual review record if available. They are blank today; do not infer either from the preparer field.
3. Independently review pseudonymized speaker-to-case assignments and code-switch labels before subgroup evaluation or CEAS.
4. Confirm provider contracts, data residency/retention, API keys, model version, language hints, decode settings, and endpoint behavior. Secrets must be entered through secure secret management, not repository files.
5. Run a small approved pilot only after gates pass; record paired case coverage, failures, latency, model/version and output provenance. Do not mix mock and live metrics.
6. Implement the Whisper adapter before claiming three-model execution in the shared clinical pipeline.

## Decision

The repository is ready for controlled local reproducibility checks and planning, but **not yet ready for Sahara or Gemini hosted uploads, and not ready for Whisper execution through the clinical pipeline**. No model inference was run for this certification task.
