# Benchmark Metadata Audit Report

## Findings

- The original manifest and `approvals.csv` asserted affirmative consent, de-identification, and hosted approval for all rows without evidence. Those fields have been reset to `unknown` and remain so.
- The provided Google Sheet is anonymously accessible and has 100 unique rows, all marked `review_status=verified`. Its populated `normalized_transcript` is now the canonical reference.
- The primary source differs from the legacy DOCX on 16 normalized transcripts and the PDF on 19. The spreadsheet takes precedence; exact IDs are listed in [GROUND_TRUTH_AUDIT_REPORT.md](GROUND_TRUTH_AUDIT_REPORT.md).
- The original workbook used `HYPERLINK()` formulas for audio filenames. The repository export resolves their displayed filenames; all 100 match files in both audio directories and have cleaned-audio SHA-256 checksums.
- The source provides speaker labels and clinical domains. Five name-like speaker labels are pseudonymized in repository exports. Speaker-to-case review remains pending because the sheet has no speaker-specific review field.
- The source does not document consent, de-identification, licensing, retention, or hosted-inference approval. Code-switch classes remain provisional; the source only states the Amharic-English pair.

## Corrections Made

- Saved pseudonymized XLSX and clean CSV source copies and made the sheet canonical for the manifest.
- Promoted 100 reference rows to `verified_against_audio` based on the corresponding spreadsheet row's explicit `review_status=verified`; updated transcripts from `normalized_transcript` and recorded source-row evidence.
- Matched all 100 source audio filenames to raw and cleaned audio; computed cleaned-audio checksums and recorded checksum evidence.
- Populated pseudonymized speaker IDs and source-provided domains. Speaker assignments remain `pending_review`; domain status is source-provided, not independently adjudicated.
- Kept consent, de-identification, and hosted approval `unknown`; no affirmative claims were inferred from the spreadsheet.
- Changed `parse_docx_references.py` so importing source text resets review to pending and clears old review evidence.
- Hardened `validate_metadata.py` to reject unsupported status values, affirmative governance claims without evidence, verified references without audio/review evidence and a valid SHA-256, hosted approval without consent/de-identification/audio evidence, and verified speaker or code-switch claims without evidence. It reports unresolved states as warnings.
- Hardened `apply_governance_flags.py`, `inference_engine.py`, and `clinical_validation_upload.py` to require evidence-backed approvals and compare approved checksums with the exact cleaned audio before hosted inference.
- Changed the live benchmark API to default references to unverified, label such scores provisional, require review evidence and a matching audio SHA-256 for attested reference scoring, and block hosted sample uploads without consent, de-identification, and provider-approval evidence. The UI now presents these evidence inputs and computes the uploaded audio checksum.
- Updated the evaluator so references count as verified only with review evidence, verified audio presence, checksum evidence, and a valid SHA-256.
- Created [GROUND_TRUTH_COVERAGE_REPORT.md](GROUND_TRUTH_COVERAGE_REPORT.md) and [GROUND_TRUTH_AUDIT_REPORT.md](GROUND_TRUTH_AUDIT_REPORT.md); aligned project documentation to the canonical source.
- Added regression tests for unsupported positive claims, review-state resets, missing/mismatched checksum evidence, hosted-upload blocking, evaluator status, and this report.
- Verification: `python -m unittest discover -s tests -v` passes all 117 tests. `python validate_metadata.py` passes structural validation and reports seven unresolved-evidence/annotation warnings, including the missing reviewer identity and review date.

## Current Dataset Status

| Dimension | Active manifest state | Audit interpretation |
| --- | --- | --- |
| Reference/audio review | 100/100 `verified` in the canonical source and `verified_against_audio` in the manifest | Source review status supports reference promotion; legacy DOCX differs on 16 cases and PDF on 19 |
| Audio files/checksums | 100/100 filenames match raw and cleaned files; 100 cleaned WAV checksums recorded | Presence and local content hashes verified; rights/provenance remain unknown |
| Speaker labels | 100 pseudonymized labels from five source labels | Speaker-to-case assignment review remains pending |
| Clinical domains | 100 source-provided values | Not independently re-adjudicated |
| Code-switch annotation | All manifest classes provisional; source language mix is Amharic-English | Token-level labels and subgroup analysis remain unavailable |
| Consent | `unknown` for 100/100 | No affirmative consent evidence in the sheet |
| De-identification | `unknown` for 100/100 | No per-case de-identification evidence in the sheet |
| Hosted inference approval | `unknown` for 100/100 | Hosted inference remains blocked |
| Raw transcript | Blank for 100/100 in the source | Canonical reference is normalized transcript; no verbatim raw text is claimed |

The validator warns for 100 provisional code-switch labels, unknown consent,
unknown de-identification, unknown hosted-inference approval, and 100 speaker
assignments pending independent review. Reference status and checksums pass.

## Remaining Risks

- Establish consent, source rights, de-identification, retention terms, and provider-transmission approval per recording before hosted inference or patient-data use.
- Independently review speaker-to-case assignments and adjudicate code-switch labels; do not treat a generic row review flag as speaker-specific verification.
- Review source-provided clinical domains and medical entities for clinical correctness and criticality before scoring their recall.
- The validator checks evidence-reference presence and field consistency, not the truth or legal sufficiency of external evidence. Human governance review remains mandatory.
- No live model performance comparison is available. Keep the historical 15-case report separate from the active spreadsheet-backed benchmark.
