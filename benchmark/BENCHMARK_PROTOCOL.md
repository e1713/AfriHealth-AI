# Benchmark Protocol

## Objective and scope

Evaluate automatic speech recognition (ASR) and downstream clinical-entity
capture on a planned 100-case Amharic-English code-switched clinical corpus.
This is a research and engineering comparison of transcripts against
case-specific references. It is not a diagnostic, treatment, or prescribing
system evaluation.

The sole active source is
[`metadata/BENCHMARK_MANIFEST.csv`](metadata/BENCHMARK_MANIFEST.csv), which
contains source reference text and focus terms for CS-01–CS-100. Availability
of corresponding audio, speaker identities, and independent expert sign-off
must be established before calling a 100-case run complete.

The manifest's `code_switch_category` is a provisional estimate based on
lexical tokens in the written transcript: at least 60% Ethiopic-script tokens
is `Mostly Amharic`; at least 60% Latin-script tokens is
`Mostly English Clinical Terms`; otherwise it is `Balanced Mix`. These
categories must be adjudicated from audio before use as ground truth.

## Model tiers

Tier assignments describe intended comparison groups, not claims of equal
capability or completed evaluation.

| Tier | Systems | Evaluation status |
| --- | --- | --- |
| Tier 1 (primary) | Sahara/Intron, Google Gemini, OpenAI Whisper | Compare only with exact provider, checkpoint/API version, language settings, decoding options, date, and hosted/local status recorded. Existing repository evidence includes Intron Sahara v2.5, `gemini-flash-latest`, and `openai/whisper-tiny`; those are not interchangeable with future versions. |
| Tier 2 (additional baselines) | Wav2Vec2, SpeechBrain, NVIDIA NeMo | Candidate framework/model family names only. Record exact checkpoint and language coverage. SpeechBrain and NeMo are not evidenced as evaluated in the current repository. |

The repository defines a six-adapter evaluation path through
[`../inference_engine.py`](../inference_engine.py). Current mock outputs verify
data flow only and provide no accuracy evidence. Whisper, Wav2Vec2,
SpeechBrain, and NeMo adapters remain placeholders; do not present them as
measured results.

## Dataset and split policy

- Use one manifest row per unique case and one designated canonical audio file
  per case.
- Keep alternate takes and duplicates out of the primary score; record their
  relationship instead of silently counting them as independent samples.
- Freeze case membership, source-reference version, normalization rules,
  target terms, and exclusions before model inference.
- If tuning prompts or decoding on this corpus, use a documented development
  subset and keep a separate held-out evaluation subset. With only 100 cases,
  report exact counts and avoid claims of statistical generalization.
- Preserve the source audio. Standardized derivatives must have reproducible
  settings and links back to source filenames.
- Do not send recordings to hosted APIs unless consent, de-identification,
  authorization, and applicable data-processing terms have been verified.

## Inference procedure

For each case/model pair, record:

1. Input filename and cryptographic checksum; sample rate, channel count, and
   duration.
2. Exact model/provider/checkpoint/version, endpoint or library version, and
   run timestamp.
3. Language/task hints, prompt, decoding parameters, and preprocessing.
4. Request start/end times, retry count, status, and any error.
5. Raw hypothesis in access-controlled storage and a redacted aggregate
   reporting path.

Run each system on the same canonical audio. Do not silently omit failed cases
or score a different subset per model. Report coverage, failures, and the
paired sample count with every metric. Hosted systems can change without a
stable version; record the provider's version identifier when available and
the retrieval date otherwise.

## Scoring and review

Report normalized word error rate (WER), medical-term recall, critical-term
miss rate, clinical-entity recall, code-switch accuracy when token-level
language labels exist, and latency. Formal definitions are in
[`EVALUATION_METRICS.md`](EVALUATION_METRICS.md).

References, focus terms, alias lists, entity spans, and critical-term labels
must be frozen before viewing model hypotheses. Resolve disagreements through
the annotation policy; do not let a model output rewrite its own reference.
Always include raw counts and missing-data status alongside percentages.

## Safety and governance

- Keep direct identifiers and raw recordings out of public reports and source
  control.
- Store consent, de-identification, provenance, annotator, and access
  information separately from public aggregate outputs.
- A qualified human reviewer must approve clinical annotations; model output
  is never ground truth.
- Report serious omissions as safety-relevant errors, but do not interpret
  benchmark scores as clinical efficacy or authorization for autonomous care.
