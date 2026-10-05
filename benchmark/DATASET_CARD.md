# Dataset Card: AfriHealth AI Clinical Speech Benchmark

## Summary

| Field | Description |
| --- | --- |
| Intended name | AfriHealth AI Clinical Code-Switched Speech Benchmark |
| Source corpus scope | 100 reference cases, IDs CS-01 through CS-100 |
| Languages | Amharic and English, including code-switched clinical phrases |
| Speakers | Project brief describes five speakers; case-to-speaker assignments and speaker-level source evidence were not present in the accessible corpus export |
| Domains | Clinical scenarios; case-level domain labels were not supplied in the accessible export |
| Modalities | Reference text and focus-term strings are available in the provided Google Docs export; audio availability must be verified per case |
| Primary task | Clinical-domain ASR comparison against frozen references |
| Secondary task | Recall of annotated clinical terms/entities |
| Status | Source corpus mapped; not a verified 100-audio gold-standard release |

## Composition and provenance

The case text and focus terms were taken from the user-provided
[Google Docs corpus export](https://docs.google.com/document/d/1KwAs-2KAjv5gUEJwFk86JjrNQGoDcABE/export?format=txt).
The [master manifest](metadata/BENCHMARK_MANIFEST.csv) retains source status
and annotation status. The source provides batch headings, but not reliable
case-level speaker or medical-domain metadata.

The master manifest is the only active clinical benchmark source. Do not
infer that filenames listed in it correspond to available or licensed audio,
or that the source reference text matches an audio recording, without checking
provenance, consent, and checksums.

## Language and annotation

The text includes Ethiopic-script Amharic and Latin-script English/clinical
terms. Script-based code-switch labels in the manifest are automatically
estimated from text only; they are not human language-identification labels.
They must be reviewed and can fail on borrowed terms, transliteration,
abbreviations, numerals, and named entities.

## Intended use

- Engineering evaluation of clinical-domain ASR and entity-capture behavior.
- Error analysis for terminology, medication/dose strings, negation, numbers,
  and language switching.
- Human-reviewed research comparison with documented model versions.

## Out-of-scope uses

- Diagnosis, treatment selection, prescribing, triage decisions, or patient
  management.
- Clinical efficacy or safety certification.
- Demographic fairness claims or population-level generalization.
- Evaluating speaker identity, emotion, or protected attributes.
- Treating all focus terms as critical safety terms without clinician review.

## Consent, privacy, and maintenance

The accessible corpus text does not establish per-recording consent,
de-identification, licensing, or retention status. Verify these for every audio
source before local or hosted inference. The five-speaker target should use
non-identifying codes only; do not store names, contact details, or biometric
voiceprints in the benchmark manifest.

Before scoring, independently verify each reference against its audio and
record the review outcome in the master manifest. Do not introduce a
parallel per-case reference source.
