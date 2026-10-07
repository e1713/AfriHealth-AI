# Dataset Card: AfriHealth AI Clinical Speech Benchmark

## Dataset Summary

The benchmark contains 100 Amharic-English clinical cases with normalized
reference transcripts, audio filename mappings, medical-entity strings,
source-provided clinical domains, and five pseudonymized speaker labels. All
source rows are marked `review_status=verified`. Matching raw/cleaned WAV files
are present and cleaned-file SHA-256 values are recorded. This is an ASR
research/evaluation resource, not a clinically validated system or patient-care
dataset release. Consent and external-use rights remain unknown.

## Summary

| Field | Description |
| --- | --- |
| Intended name | AfriHealth AI Clinical Code-Switched Speech Benchmark |
| Source corpus scope | 100 reference cases, IDs CS-01 through CS-100 |
| Languages | Amharic and English, including code-switched clinical phrases |
| Speakers | Five source speaker labels are present and pseudonymized in repository exports; speaker-to-case assignment review remains pending |
| Domains | Clinical domain values are populated for all 100 source cases; clinical correctness has not been independently re-adjudicated |
| Modalities | Verified normalized transcript and medical-entity fields in the Google Sheet; the source raw-transcript column is blank; matching WAV files exist in raw and cleaned folders |
| Primary task | Clinical-domain ASR comparison against frozen references |
| Secondary task | Recall of annotated clinical terms/entities |
| Status | All 100 source rows say `review_status=verified`; consent/provider governance remains unknown; speaker and code-switch review remain incomplete |

## Composition and provenance

The canonical source is the user-provided [Google Sheet](https://docs.google.com/spreadsheets/d/1IQOdmAQxuiU2MgAqCAQ91rG-8TIS3UB_/edit),
exported as [XLSX](metadata/GROUND_TRUTH_SOURCE.xlsx) and normalized
[CSV](metadata/GROUND_TRUTH_SOURCE.csv). All 100 rows contain a
`normalized_transcript` and `review_status=verified`. The XLSX raw-transcript
field is blank in all rows. The [manifest](metadata/BENCHMARK_MANIFEST.csv) is
the evaluation projection of that source. The previous DOCX differs from the
canonical normalized transcript in 16 cases and the PDF in 19; see
[GROUND_TRUTH_AUDIT_REPORT.md](../GROUND_TRUTH_AUDIT_REPORT.md).

The spreadsheet is canonical; the manifest is its source-linked projection.
Matching-name WAV files exist in `raw_audio/` and `cleaned_audio/` for all 100
rows, and the manifest records SHA-256 checksums for cleaned WAVs. The sheet's
review status supports reference alignment, but does not establish recording
rights or consent. Consent, de-identification, and hosted-inference approval
remain `unknown`. Source speaker labels are pseudonymized in the repository;
speaker-to-case review is pending.

## Verification Methodology

User-supplied benchmark evidence states that transcripts, audio, and
audio-transcript alignment were reviewed manually. The source sheet records
`review_status=verified` for 100/100 rows. Local verification also confirms
source IDs, normalized transcript/source consistency, matching audio filenames,
and cleaned-WAV SHA-256 values. Benchmark preparation was performed by Ermias.

The exports record `verification_method=manual_review`, `dataset_version=v1.0`,
and `prepared_by=Ermias`. `reviewer` and `review_date` are blank because that
information and supporting review logs were not supplied. Preparation
attribution is not a reviewer identity. The validator confirms metadata
consistency; it cannot independently witness manual listening or the external
review process.

## Language and annotation

The text includes Ethiopic-script Amharic and Latin-script English/clinical
terms. Script-based code-switch labels in the manifest are automatically
estimated from text only; they are not human language-identification labels.
They must be reviewed and can fail on borrowed terms, transliteration,
abbreviations, numerals, and named entities.

## Known Limitations

- Normalized references are supplied and marked verified; raw transcripts and
  independent annotator/adjudication logs are absent.
- Reviewer identity/date are not recorded.
- Speaker-to-case assignments are source-populated but pending
  assignment-specific review; speaker counts are imbalanced.
- Domain and entity labels are source-provided and have not been separately
  clinically re-adjudicated for correctness or criticality.
- Token-level code-switch labels, switch boundaries, and inter-annotator
  agreement are unavailable.
- Consent, de-identification, licensing, retention, and hosted-inference
  approval are unknown. Hosted model calls must remain blocked until approved.
- A 100-case, five-speaker dataset does not support robust population or
  demographic fairness claims.

## Bias Considerations

The speaker distribution is uneven (13, 27, 15, 40, and 5 cases across the five
pseudonyms). No demographic attributes should be inferred from pseudonyms or
audio. Three normalized references contain Latin letters without Ethiopic
letters under the simple script check; verify whether those cases represent
English-only examples or missing Amharic content before code-switch subgroup
analysis. Script-share heuristics can misclassify borrowed terms, numerals,
abbreviations, and transliterations.

## Intended use

- Engineering evaluation of clinical-domain ASR and entity-capture behavior.
- Error analysis for terminology, medication/dose strings, negation, numbers,
  and language switching.
- Human-reviewed research comparison with documented model versions.

## Recommended Use

- Controlled Amharic-English ASR comparison using the frozen normalized
  references and matching canonical audio.
- Error analysis for medical terminology, medications, doses, negation, and
  code-switching after clinical label review.
- Local mock-pipeline and reproducibility testing without treating mock outputs
  as model results.

## Out-of-scope uses

- Diagnosis, treatment selection, prescribing, triage decisions, or patient
  management.
- Clinical efficacy or safety certification.
- Demographic fairness claims or population-level generalization.
- Evaluating speaker identity, emotion, or protected attributes.
- Treating all focus terms as critical safety terms without clinician review.

## Unsupported Uses

- Claims of clinical safety/efficacy, population generalization, or demographic
  fairness.
- Hosted inference or external distribution until consent, rights,
  de-identification, retention, and provider approvals are evidenced per case.
- Treating source domains/entities as independently clinically adjudicated.

## Benchmark Scope

The active language scope is Amharic-English clinical speech. The source
language-pair field is constant and does not provide token-level language
annotations. The manifest's script-based code-switch categories are provisional.
The canonical references are verified according to the supplied source status;
speaker assignment and code-switch subgroup annotations remain pending. No live
model score or CEAS is included in this dataset release.

## Consent, privacy, and maintenance

The accessible corpus materials do not establish per-recording consent,
de-identification, licensing, or retention status. Verify these for every audio
source before inference; hosted inference is blocked unless all required
affirmative states cite evidence. The five-speaker target should use
non-identifying codes only; do not store names, contact details, or biometric
voiceprints in the benchmark manifest.

Preserve the source `review_status` evidence and source row mapping when updating
references. The legacy DOCX differs on 16 cases and the PDF on 19; neither
overrides the canonical sheet. Do not introduce a competing per-case reference
source.
