# Benchmark Certification Report

## Dataset Integrity

- Canonical source: Google Sheet export at `benchmark/metadata/GROUND_TRUTH_SOURCE.xlsx` and normalized `GROUND_TRUTH_SOURCE.csv`.
- 100 unique case IDs, CS-01 through CS-100; zero duplicate, missing, or unexpected IDs.
- Source `review_status=verified` for 100/100 rows.
- Manifest source projection matches all 100 canonical normalized transcripts, audio filenames, pseudonymized speaker labels, domains, and medical-entity/focus-term values.
- The source raw-transcript column is blank. Do not claim this release preserves verbatim transcripts.
- Legacy asset differences: DOCX differs on 16 references; PDF differs on 19. The sheet is canonical.

## Audio Integrity

All 100 source audio filenames exist in both `raw_audio/` and `cleaned_audio/`. SHA-256 was computed for each cleaned WAV; all 100 computed values match the manifest. The supplied evidence states audio and transcript alignment were reviewed manually. Reviewer identity/date and source recording provenance are not recorded, so this is not independent proof of licensing or consent.

## Transcript Integrity

All 100 normalized transcripts are populated and marked `verified` in the canonical source. The supplied review-process statement says transcripts were manually reviewed and manually aligned to audio. The normalized strings are copied unchanged to the manifest except whitespace handling by the CSV reader. No separate raw transcript is present. No independent reviewer log, review date, adjudication record, or annotator-agreement statistic was supplied.

## Reference Consistency

The validator compares source and manifest IDs, normalized transcript, filename, pseudonymized speaker value, domain, medical entities, verification method, notes, dataset version, preparer, reviewer, and review date. Current source/manifest comparisons pass for all 100 cases. Legacy DOCX/PDF records are not used to overwrite the canonical source.

## Validation Results

- Canonical source: 100 rows, unique expected IDs, 100 `verified` review statuses.
- Audio mapping: 100/100 present in raw and cleaned folders.
- Cleaned audio checksums: 100/100 match.
- Manifest/source synchronization: 100/100 pass.
- `python validate_metadata.py`: passes structural and consistency validation.
- `python -m unittest discover -s tests -v`: 117 tests passed after Priority 2 changes.
- `python validate_metadata.py`: passes with warnings for missing reviewer/date, unknown governance approvals, pending speaker review, and provisional code-switch labels.
- No model inference was run in this phase.

## Known Limitations

- `reviewer` and `review_date` are blank because not provided. `prepared_by=Ermias` records preparation attribution, not reviewer identity.
- Consent, de-identification, licensing, retention, and hosted provider approval are `unknown` for every record.
- Speaker labels are pseudonymized, but speaker assignment review is pending.
- Domains and medical entities are source-provided; clinical correctness and criticality have not been independently re-adjudicated.
- Language mix is source-labeled Amharic-English. Manifest code-switch categories remain provisional script-share estimates; token-level language labels are absent.
- No live paired model outputs, WER/CER aggregates, latency measurements, clinical safety results, or CEAS were produced.

## Governance Status

Transcript/audio alignment: source-attested manual review, with reviewer/date audit trail unavailable. Dataset version: `v1.0`. Preparation: Ermias. Consent and de-identification: unverified/unknown. Hosted inference: blocked until per-case approvals and evidence references are supplied. Speaker assignment: pending independent review.

## Benchmark Readiness Assessment

**Readiness level: Source-attested reference certification; conditionally ready for controlled benchmark preparation. Not cleared for hosted inference or clinical use.** The reference source, manifest, audio mapping, and checksums are synchronized, and manual transcript/audio/alignment review is attested by the supplied process statement. Reviewer identity/date are absent, so the attestation chain is not independently auditable. Proceeding to model execution requires documented rights/consent, de-identification, per-provider approval for hosted APIs, and separate review of speaker assignments and code-switch labels for subgroup/fairness analysis. No numeric readiness score is assigned because no official certification rubric was supplied; this report does not certify clinical validity or model performance.
