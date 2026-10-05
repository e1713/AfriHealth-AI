# Benchmark Results (Template)

> **Status:** Template. Replace only with reproducible run data. Do not report
> model scores as measured until all stated inclusion and reference criteria
> are met.

## Run identification

| Field | Value |
| --- | --- |
| Run ID / date (UTC) | TBD |
| Dataset version / source | TBD |
| Eligible cases / available audio | TBD / TBD |
| Verified references | TBD |
| Scoring code commit | TBD |
| Normalization / alias version | TBD |
| Environment / hardware | TBD |

## Model-level results

| Model / exact checkpoint | Tier | Cases attempted | Cases scored | WER ↓ | Medical-term recall ↑ | Critical-term miss rate ↓ | Entity recall ↑ | Code-switch accuracy ↑ | Median latency (s) | p95 latency (s) | Failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sahara / Intron (exact version: TBD) | 1 | — | — | — | — | — | — | — | — | — | — |
| Gemini (exact model: TBD) | 1 | — | — | — | — | — | — | — | — | — | — |
| Whisper (exact checkpoint: TBD) | 1 | — | — | — | — | — | — | — | — | — | — |
| Wav2Vec2 (exact checkpoint: TBD) | 2 | — | — | — | — | — | — | — | — | — | — |
| SpeechBrain (exact checkpoint: TBD) | 2 | — | — | — | — | — | — | — | — | — | — |
| NVIDIA NeMo (exact checkpoint: TBD) | 2 | — | — | — | — | — | — | — | — | — | — |

## Per-case matrix

| Case ID | Reference status | Audio status | Model | WER | Target terms matched / total | Critical misses / total | Entity TP / FN | Latency (s) | Error/status note |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| CS-01 | — | — | — | — | — | — | — | — | — |

Store the full matrix and transcripts in an access-controlled artifact. Do not
publish sensitive per-case text.

## Error and coverage summary

- Total reference critical-term mentions: TBD
- Total critical-term misses: TBD
- Cases with one or more critical misses: TBD / TBD
- Cases excluded and predeclared reason: TBD
- Requests failed/timed out: TBD
- Model outputs unavailable: TBD
- Domain/speaker/code-switch labels reviewed: TBD

## Interpretation and limitations

Describe paired sample coverage, source/reference version, confidence
intervals if methodologically justified, model/version limitations, and
whether results are simulated or audio-grounded. State explicitly that ASR
metrics do not establish diagnostic accuracy, clinical efficacy, or autonomous
clinical suitability.
