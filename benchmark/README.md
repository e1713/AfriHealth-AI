# AfriHealth AI benchmark

This directory contains the benchmark protocol, dataset card, annotation and
metric definitions, reproducibility notes, limitations, challenge mapping,
entity schema, case manifest, and reporting templates.

## Source and evidence status

The canonical source is the user-provided [Google Sheet](https://docs.google.com/spreadsheets/d/1IQOdmAQxuiU2MgAqCAQ91rG-8TIS3UB_/edit),
exported to [XLSX](metadata/GROUND_TRUTH_SOURCE.xlsx) and a normalized
[CSV](metadata/GROUND_TRUTH_SOURCE.csv). It contains 100 unique cases, populated
normalized transcripts and medical entities, source speaker/domain fields, and
`review_status=verified` for every case. The source raw-transcript column is
blank. The manifest projects this source for evaluation. The legacy DOCX differs
from the canonical normalized transcript on 16 cases and the PDF on 19; the
sheet takes precedence.

All 100 audio filenames match files in both `raw_audio/` and `cleaned_audio/`;
the manifest stores cleaned-audio SHA-256 checksums. Five name-like source
speaker labels are pseudonymized in repository exports; speaker assignment
review remains pending. Domains are source-provided. Code-switch labels remain
provisional Unicode-script-share estimates and are not token-level audio labels.
Consent, de-identification, licensing, retention, and hosted-inference approval
are not supplied by the sheet and remain unknown.

## Files

- [BENCHMARK_PROTOCOL.md](BENCHMARK_PROTOCOL.md)
- [DATASET_CARD.md](DATASET_CARD.md)
- [ANNOTATION_GUIDELINES.md](ANNOTATION_GUIDELINES.md)
- [EVALUATION_METRICS.md](EVALUATION_METRICS.md)
- [REPRODUCIBILITY_GUIDE.md](REPRODUCIBILITY_GUIDE.md)
- [BENCHMARK_LIMITATIONS.md](BENCHMARK_LIMITATIONS.md)
- [SCORING_RUBRIC_ALIGNMENT.md](SCORING_RUBRIC_ALIGNMENT.md)
- [schemas/CLINICAL_ENTITY_SCHEMA.json](schemas/CLINICAL_ENTITY_SCHEMA.json)
- [metadata/BENCHMARK_MANIFEST.csv](metadata/BENCHMARK_MANIFEST.csv)
- [metadata/SPEAKER_METADATA.md](metadata/SPEAKER_METADATA.md)
- [RESULTS_TEMPLATE.md](RESULTS_TEMPLATE.md)
- [MODEL_RECOMMENDATION_TEMPLATE.md](MODEL_RECOMMENDATION_TEMPLATE.md)
- [reporting/PRESENTATION_SLIDES.md](reporting/PRESENTATION_SLIDES.md)
- [GROUND_TRUTH_VERIFICATION_REPORT.md](../GROUND_TRUTH_VERIFICATION_REPORT.md)
- [BENCHMARK_CERTIFICATION_REPORT.md](../BENCHMARK_CERTIFICATION_REPORT.md)
- [AUDIO_ALIGNMENT_REPORT.md](../AUDIO_ALIGNMENT_REPORT.md)
- [SPEAKER_DOMAIN_AUDIT.md](../SPEAKER_DOMAIN_AUDIT.md)
- [CODESWITCH_READINESS_REPORT.md](../CODESWITCH_READINESS_REPORT.md)
- [BENCHMARK_EXECUTION_READINESS.md](../BENCHMARK_EXECUTION_READINESS.md)

## Quick validation

From the repository root:

```bash
python validate_metadata.py
```

This validates the medical vocabulary and master manifest structure. It does not
independently verify the underlying spreadsheet or the truth of external
evidence references. It rejects unsupported positive consent, de-identification,
approval, or verification states and warns when required labels remain pending.
Spreadsheet-to-manifest reconciliation is covered by
`tests/test_benchmark_docs.py`.
