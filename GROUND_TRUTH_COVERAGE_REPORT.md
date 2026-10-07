# Ground Truth Coverage Report

## Canonical Source

The canonical source is the accessible Google Sheet:

[Ground Truth Spreadsheet](https://docs.google.com/spreadsheets/d/1IQOdmAQxuiU2MgAqCAQ91rG-8TIS3UB_/edit)

Repository copies are [GROUND_TRUTH_SOURCE.xlsx](benchmark/metadata/GROUND_TRUTH_SOURCE.xlsx) and [GROUND_TRUTH_SOURCE.csv](benchmark/metadata/GROUND_TRUTH_SOURCE.csv). The repository copies pseudonymize five name-like speaker labels and resolve audio hyperlink formulas to their displayed filenames. The CSV is a normalized case-table export from the XLSX, without the spreadsheet's summary/preamble rows. No identity mapping is stored.

## Coverage

| Check | Result | Notes |
| --- | --- | --- |
| Expected records | 100 | CS-01 through CS-100 |
| Unique IDs | 100/100 | No duplicates |
| Missing/unexpected IDs | 0/0 | Source and manifest ID sets match |
| Source review status | 100/100 `verified` | Supports reference review promotion |
| Normalized transcript | 100/100 populated | Canonical manifest transcript field |
| Raw transcript | 0/100 populated | Source raw-transcript column is blank; no raw transcript is inferred |
| Transcript match to current manifest | 100/100 | Exact after whitespace normalization |
| Matching audio filenames | 100/100 | Matches both `raw_audio/` and `cleaned_audio/` |
| Cleaned audio checksums | 100/100 | SHA-256 values computed and recorded in the manifest |
| Focus terms/entities | 100/100 | Spreadsheet medical-entity field matches existing manifest focus terms |
| Speaker labels | 100/100 | Five labels pseudonymized in repository files; assignment review remains pending |
| Clinical domains | 100/100 | Populated from source; not independently re-adjudicated |
| Language mix | 100/100 | Source reports Amharic-English; finer switch categories remain provisional |
| Consent/de-identification/provider approval | 0/100 affirmative evidence | All remain `unknown`; live hosted inference is blocked |

## Reconciliation

- All 100 source case IDs are unique and match the manifest.
- All source `audio_filename` values match files in both audio directories.
- All canonical normalized transcripts match the active manifest after import.
- All source medical entities match the manifest focus-term field.
- The prior manifest had blank speaker IDs and clinical domains for all 100 rows; after import, pseudonymized speakers and source domains match all 100 source rows (zero current mapping mismatches). Speaker assignment review remains pending.
- The prior manifest and checked-in DOCX differ from the canonical spreadsheet on 16 normalized transcripts: CS-08, CS-11, CS-14, CS-15, CS-21, CS-28, CS-43, CS-46, CS-47, CS-49, CS-54, CS-61, CS-62, CS-75, CS-77, and CS-78. The spreadsheet is the primary source and takes precedence.
- The PDF contains all 100 expected IDs and differs from the canonical normalized transcript on 19 cases: CS-08, CS-11, CS-14, CS-15, CS-16, CS-21, CS-28, CS-37, CS-43, CS-46, CS-47, CS-49, CS-54, CS-61, CS-62, CS-75, CS-77, CS-78, and CS-81. CS-16, CS-37, and CS-81 are PDF-only mismatches versus the DOCX.
- The sheet's general row review status does not separately attest speaker-to-case assignments. Those values are retained as pseudonyms but marked `pending_review`.

## Interpretation

Coverage and file/checksum consistency do not establish consent, recording rights, de-identification, speaker identity, clinical correctness of domains/entities, or hosted-provider authorization. The reports and mock pipeline do not constitute live model performance evidence.
