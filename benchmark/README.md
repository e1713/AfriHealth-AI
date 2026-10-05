# AfriHealth AI benchmark

This directory contains the benchmark protocol, dataset card, annotation and
metric definitions, reproducibility notes, limitations, challenge mapping,
entity schema, case manifest, and reporting templates.

## Source and evidence status

The 100 case transcripts and focus terms in
[`metadata/BENCHMARK_MANIFEST.csv`](metadata/BENCHMARK_MANIFEST.csv) were
transcribed from the user-provided Google Docs plain-text export:
[AfriHealth AI Benchmark Corpus, CS-01–CS-100](https://docs.google.com/document/d/1KwAs-2KAjv5gUEJwFk86JjrNQGoDcABE/export?format=txt).
This provides source text but does not, by itself, establish independent
expert verification, audio availability, speaker assignment, or domain
annotation. The user also provided a [PDF reference on Google Drive](https://drive.google.com/file/d/13H07n7dPwI6nUx3nZ17cI-4RDM9RFHCM/view);
its binary contents were not used to populate the manifest. The named DOCX
was not present in the local checkout.

Speaker IDs and per-case medical domains are intentionally blank until
supported by approved source metadata. Code-switch labels are provisional
Unicode-script-share estimates: Ethiopic vs Latin lexical-token share, with
60% thresholds for the two "mostly" categories; annotators must confirm them
before analysis. The estimate does not determine whether Latin words are
clinical terms and is not an audio-derived label.
The 100-row manifest is a corpus mapping, not proof that 100 audio recordings
are present or that the references are gold-standard transcripts.

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

## Quick validation

From the repository root:

```bash
python validate_metadata.py
```

This validates the medical vocabulary and master manifest structure. It does not
independently verify annotations in the benchmark manifest. The manifest's 100
rows, IDs, provenance/status fields, and required transcript/focus-term values
are covered by `tests/test_benchmark_docs.py`.
