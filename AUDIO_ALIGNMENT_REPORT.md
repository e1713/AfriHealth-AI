# Audio Alignment Report

## Scope

Compared the canonical source `audio_filename` values with `raw_audio/` and `cleaned_audio/`, then verified each cleaned WAV against the manifest's SHA-256. The user supplied that audio and transcript alignment was reviewed manually; no reviewer identity, review date, or per-case signed alignment log was supplied.

## Results

| Check | Result |
| --- | ---: |
| Source records reviewed | 100/100 |
| Audio filenames mapped | 100/100 |
| Raw WAV files present | 100/100 |
| Cleaned WAV files present | 100/100 |
| SHA-256 checksums recomputed and matched | 100/100 |
| Audio/transcript matching | 100/100 source rows marked `verified`; manual alignment review attested by user |
| Unmatched source records | 0 |
| Unmatched audio filenames | 0 |
| Alignment coverage | 100% source-attested; reviewer/date documentary coverage not available |

## Method

1. Read the `audio_filename` from each row of the canonical XLSX/CSV case table.
2. Confirm the same filename exists in both audio folders.
3. Compute SHA-256 from `cleaned_audio/<filename>` and compare to `audio_checksum_sha256` in the manifest.
4. Read source `review_status`; all rows state `verified`.
5. Record the supplied assertion that audio and transcript alignment were manually reviewed.

## Interpretation and Limitations

Checksum equality establishes local file consistency, not the source recording's licensing, provenance, participant consent, or external chain of custody. `review_status=verified` and the supplied manual-review statement support alignment status, but reviewer identity/date and underlying review records were not supplied. No claim is made that the repository independently reproduced human listening review. See `GROUND_TRUTH_AUDIT_REPORT.md` for legacy DOCX/PDF discrepancies.
