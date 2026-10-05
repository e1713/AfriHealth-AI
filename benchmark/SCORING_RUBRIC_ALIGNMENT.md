# Sahara Challenge Scoring Rubric Alignment

This is a project evidence map, not an official score or certification.
Challenge weights and judging criteria should be taken from the current
organizer-published rubric; no weights are assumed here.

| Challenge category | Benchmark design/evidence | Gaps and honest interpretation |
| --- | --- | --- |
| Benchmark Quality | One 100-case source manifest, explicit normalization, medical focus terms, formal WER/recall/critical-miss/latency definitions, six-model inference schema, and result templates. Current pipeline artifacts: [BENCHMARK_RESULTS.md](../BENCHMARK_RESULTS.md), [metadata/BENCHMARK_MANIFEST.csv](metadata/BENCHMARK_MANIFEST.csv), [inference_engine.py](../inference_engine.py), and [evaluator.py](../evaluator.py). | The manifest contains source text, not audio-verified gold transcripts; no validated live model comparison is currently available. Audio, reference adjudication, speaker labels, code-switch label confirmation, and broader model coverage remain incomplete. |
| Healthcare Impact | Clinical speech vocabulary and clinically relevant error analysis, with human review and no autonomous-care claims. | These are simulated/reference test cases. Metrics do not establish workflow impact, clinical efficacy, or improved patient outcomes. |
| Responsible AI | Consent/de-identification/hosted-inference gates, clinician review, disclosed critical-term errors, and a proposed multidimensional CEAS design combining overall recognition accuracy with worst-speaker robustness and worst-code-switch-category consistency. The formula, weights, reporting requirements, and prerequisites are specified in [EVALUATION_METRICS.md](EVALUATION_METRICS.md). | CEAS is a project-proposed, unvalidated metric inspired by Fairness-Adjusted ASR Score work; it is not an exact reproduction or demographic fairness claim. It cannot be calculated until references and speaker/category labels are adjudicated and subgroup minimums are met. Repository controls do not establish production-grade clinician identity, dataset consent, retention governance, or provider approval. |
| Technical Execution | Reproducible scripts, explicit model tiers, standardized audio procedure, the authoritative manifest, entity schema, resumable inference outputs, and scoring definitions. | The mock pipeline verifies data flow only. Tier 2 SpeechBrain/NeMo adapters and full code-switch/entity-span scoring require implementation and evidence. |

## Judge-ready evidence checklist

- Identify corpus version and case count separately from audio count.
- Show paired model results on the same verified cases.
- Include error counts and coverage, not percentages alone.
- Show critical-term misses with a clinician-reviewed denominator.
- Label unverified source text, inferred metadata, and simulated cases explicitly.
- Do not claim demographic fairness or CEAS performance: speaker assignments
  are missing and code-switch labels are provisional.
- Avoid safety and clinical efficacy claims unsupported by this dataset and
  evaluation.
