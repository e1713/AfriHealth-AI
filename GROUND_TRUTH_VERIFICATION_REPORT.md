# Ground Truth Verification Report

## Dataset Overview

| Measure | Coverage | Result |
| --- | ---: | --- |
| Total cases | 100/100 | Unique IDs CS-01 through CS-100 |
| Source review status | 100/100 | Source `review_status=verified` |
| Canonical normalized transcript | 100/100 | Populated; copied into manifest |
| Verbatim/raw transcript | 0/100 | Source `raw_transcript` field is blank |
| Audio mapping | 100/100 | Source filenames map to raw and cleaned WAV files |
| Audio checksum | 100/100 | SHA-256 matches each cleaned WAV |
| Speaker label coverage | 100/100 | Five pseudonymized source labels; assignment-specific review pending |
| Domain coverage | 100/100 | 73 distinct source-provided domain labels |
| Medical entity coverage | 100/100 | 244 entity mentions; 223 distinct strings under comma/semicolon split |
| Language pair | 100/100 | Source label `Amharic-English` |

Audio-script inspection found 97 transcripts containing both Ethiopic-script and Latin-script letters and 3 containing Latin-script letters only; no transcript was Ethiopic-only under this simple script test. This is a descriptive text characteristic, not a token-level language annotation or an ASR performance result.

## Verification Methodology

The canonical Google Sheet export is `benchmark/metadata/GROUND_TRUTH_SOURCE.xlsx`; the normalized, case-table export is the companion CSV. The manifest retains each source row mapping and uses `normalized_transcript` as the reference. The verified source status is `review_status=verified` for all rows.

The following methodology was supplied for this certification phase and is recorded as benchmark evidence:

- Transcripts were reviewed manually.
- Audio was reviewed manually.
- Audio-to-transcript alignment was reviewed manually.
- Benchmark preparation was performed by Ermias.

The manifest and exports record `verification_method=manual_review`, `dataset_version=v1.0`, and `prepared_by=Ermias`. Reviewer identity, review date, independent reviewer logs, adjudication records, and consent records were not supplied; those fields remain blank/unknown. Ermias is recorded as preparer only, not assumed to be the reviewer.

Audio integrity was checked locally by confirming each source filename exists in both audio directories and comparing a computed SHA-256 for `cleaned_audio/<filename>` against the manifest checksum. This establishes local file/checksum consistency, not original recording provenance, licensing, or participant permission.

## Verification Evidence and Limits

Transcript and alignment verification is **source-attested**: the sheet marks every row verified and the user supplied that the transcript/audio/alignment reviews were manual. This repository does not independently reproduce the manual review or identify its reviewer/date. The evidence supports using the normalized transcript column as the frozen reference for controlled benchmark preparation, subject to those audit-trail gaps.

The source raw-transcript field is empty. Therefore this release verifies the supplied normalized reference strings, not a separately preserved verbatim transcript. The legacy DOCX differs from the canonical source on 16 cases and the PDF on 19; the spreadsheet is the designated primary source.

Speaker labels and domain values are supplied by the source. Speaker labels are pseudonymized in repository copies. The source has a general row-level review status but no separate speaker-assignment review field; speaker-to-case assignments are therefore marked pending independent review. Domains and medical entities are source-provided and have not been independently clinically re-adjudicated.

## Remaining Limitations

- Reviewer identity/date and signed review logs are not available.
- Consent, de-identification, source rights, retention terms, and hosted-provider approvals are unknown.
- Speaker assignment review is pending; source speaker proportions are uneven.
- Code-switch categories in the manifest remain provisional script-share estimates, not audio-adjudicated token labels.
- No live model inference or accuracy score was generated in this certification phase.
- The source `verified` status and supplied manual-review statement are not a clinical safety, efficacy, or regulatory certification.
