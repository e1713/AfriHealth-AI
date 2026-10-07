# Live Inference Readiness

## Status: Blocked Pending Evidence

This report supersedes earlier readiness notes that treated transcript
extraction or file presence as evidence of audio verification, consent, or
hosted-inference approval.

## Current Evidence

| Item | Repository state | Interpretation |
| --- | --- | --- |
| Manifest | 100 rows, CS-01 through CS-100 | Source corpus mapping is present |
| WAV files | Matching filenames are present in `raw_audio/` and `cleaned_audio/`; manifest has 100 SHA-256 checksums | Workspace file/name match is verified; licensing, provenance, and participant permission are not established |
| Reference text | Canonical Google Sheet normalized transcript | All 100 rows have `review_status=verified`; the manifest records source-row evidence |
| Consent and de-identification | `unknown` for all 100 rows; evidence references blank | No affirmative claim is supported by the checked-in case metadata |
| Hosted inference approval | `unknown` for all 100 rows; evidence references blank | Hosted inference is blocked |
| Audio checksums | Recorded for all 100 cleaned WAVs with checksum evidence references | Runner verifies uploaded bytes against the manifest checksum |
| Speaker assignments | Five pseudonymized source labels and mappings are present | Assignment-specific review remains pending |
| Code-switch labels | Provisional script-share estimates | Human audio review and adjudication remain outstanding |

## Gate Requirements

Before hosted inference, update each case only from controlled evidence and
populate the matching evidence-reference fields for consent,
de-identification, and provider approval. Preserve the sheet's verified status
and source-row evidence for references. Speaker assignment and code-switch
states require separate review. The runner compares the recorded SHA-256 with
the cleaned WAV before upload. Run `python validate_metadata.py` after updates.
The validator
checks required values and evidence-reference presence; a qualified reviewer
must still verify the referenced records.

The import helper `parse_docx_references.py` only imports DOCX source text and
resets review to `pending_review`; it is not the canonical source importer and
cannot replace the verified spreadsheet values.
Do not use identifiable or unapproved recordings with hosted providers.

