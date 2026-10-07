# Ground Truth Audit Report

## Findings

- Anonymous Google Sheets exports were accessible for both CSV and XLSX; each returned HTTP 200. The XLSX case table contains 100 unique rows, CS-01 through CS-100.
- Every source row has `review_status=verified`, a populated `normalized_transcript`, an audio filename, a speaker label, a clinical domain, and medical entities. The `raw_transcript` column is blank for all 100 rows.
- The existing manifest and local DOCX matched each other but disagreed with the primary sheet's normalized transcript on 16 cases: CS-08, CS-11, CS-14, CS-15, CS-21, CS-28, CS-43, CS-46, CS-47, CS-49, CS-54, CS-61, CS-62, CS-75, CS-77, and CS-78.
- The checked-in PDF contains all 100 expected IDs; text extraction parsed 100 records. Its transcript text differs from the canonical sheet on 19 cases: CS-08, CS-11, CS-14, CS-15, CS-16, CS-21, CS-28, CS-37, CS-43, CS-46, CS-47, CS-49, CS-54, CS-61, CS-62, CS-75, CS-77, CS-78, and CS-81. CS-16, CS-37, and CS-81 are additional to the DOCX mismatch set.
- All source audio filename labels resolve to files in both `raw_audio/` and `cleaned_audio/`. The workbook represented filenames using `HYPERLINK()` formulas; repository exports normalize these to the displayed `CS-NN.wav` values.
- Five name-like source speaker labels were present. The XLSX/CSV copies and manifest use pseudonyms; the identity mapping is not retained in the repository.
- The source supplies speaker and clinical-domain values, but its single `review_status` field does not provide separate speaker-assignment or domain-adjudication status. Speaker assignments therefore remain pending independent review; domains are marked source-provided.
- The prior manifest had blank speaker IDs and clinical-domain fields for all 100 cases; after import both fields match the canonical source on all rows. Speaker assignment review remains pending despite the source mapping.
- The source has no consent, de-identification, licensing, retention, or hosted-inference approval fields. Those manifest states remain `unknown`.

## Corrections Made

- Saved the source as `benchmark/metadata/GROUND_TRUTH_SOURCE.xlsx` and a clean, 100-row case-table `benchmark/metadata/GROUND_TRUTH_SOURCE.csv`.
- Pseudonymized source speaker labels in both repository exports. Converted audio link formulas to the visible audio filenames; the source URL remains the external provenance reference.
- Replaced all manifest reference transcripts with the primary source `normalized_transcript` and set `reference_review_status=verified_against_audio` only where the corresponding sheet row says `review_status=verified`.
- Added source-row evidence references for transcript review, speaker labels, audio filenames, and domains. Speaker review itself remains pending.
- Confirmed all 100 filenames exist under `raw_audio/` and `cleaned_audio/`; calculated SHA-256 checksums for the cleaned WAV files and retained checksum evidence references.
- Preserved existing focus terms because all 100 match the spreadsheet medical-entity values. Preserved provisional switch categories because the source only labels the pair Amharic-English and does not provide adjudicated token-level switch labels.
- Created [GROUND_TRUTH_COVERAGE_REPORT.md](GROUND_TRUTH_COVERAGE_REPORT.md), updated metadata validation expectations, and aligned documentation/UI statements with the canonical source.

## Canonical Source and Precedence

Use the Google Sheet's `normalized_transcript` as the reference field. The older DOCX and PDF are legacy transcript assets; neither overrides the sheet on mismatching cases. The source raw-transcript column is empty, so no verbatim raw transcript should be claimed. Repository XLSX/CSV copies are pseudonymized derivatives, not byte-for-byte downloads.

## Remaining Risks

- Consent, source rights, de-identification, retention, and hosted-provider authorization are not documented in the spreadsheet; all remain unknown. Do not use these files for hosted inference or identifiable-patient use until per-case evidence is recorded.
- Speaker IDs are pseudonymized, but assignment-to-case review and source identity governance are still pending. No identity key is included in the repository.
- The source row review field verifies the reference according to the provided dataset, but the repository cannot independently validate the external review process or the underlying audio provenance.
- Clinical domains and medical entities are source-provided but have not been independently re-adjudicated for clinical correctness or criticality.
- Code-switch categories remain script-share estimates; token-level labels and CEAS subgroup prerequisites are not met.
- No live model outputs or validated model comparison were produced by this audit. Mock metrics remain pipeline-only.
