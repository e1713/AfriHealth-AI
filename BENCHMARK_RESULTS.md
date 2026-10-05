# AfriHealth AI Benchmark Results

## Current evidence status

The active benchmark source is the 100-case manifest at
[`benchmark/metadata/BENCHMARK_MANIFEST.csv`](benchmark/metadata/BENCHMARK_MANIFEST.csv).
It contains source reference text and focus terms, but references have not
been independently verified against audio. Speaker assignments are missing,
and code-switch labels are provisional.

No validated live ASR accuracy comparison or Clinical Equity-Adjusted ASR
Score (CEAS) is currently available. Mock runs produce synthetic transcripts
and simulated latency for pipeline testing only. Mock accuracy metrics are
intentionally unscored.

The embedded five-case application fixture is demo content, not a speech
benchmark.

See [benchmark/EVALUATION_METRICS.md](benchmark/EVALUATION_METRICS.md) for
metric definitions and CEAS prerequisites, and
[benchmark/BENCHMARK_LIMITATIONS.md](benchmark/BENCHMARK_LIMITATIONS.md) for
the corpus limitations.

<!-- BEGIN AUTO-GENERATED EVALUATION SUMMARY -->
## Current Evaluation Pipeline Summary

> Generated from `results/final_evaluation_metrics.csv` at 2026-10-05 23:00 UTC. The authoritative source corpus contains 100 cases; references and labels remain under review.

| Model | Status | Live outputs | Mock outputs | Failed | Mean WER | Medical-term recall | Critical miss rate | Live mean latency (s) | Simulated mean latency (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sahara | mock_only_accuracy_not_scored | 0 | 100 | 0 | N/A | N/A | N/A | N/A | 1.321 |
| Gemini | mock_only_accuracy_not_scored | 0 | 100 | 0 | N/A | N/A | N/A | N/A | 1.225 |
| Whisper | mock_only_accuracy_not_scored | 0 | 100 | 0 | N/A | N/A | N/A | N/A | 1.280 |
| Wav2Vec2 | mock_only_accuracy_not_scored | 0 | 100 | 0 | N/A | N/A | N/A | N/A | 1.214 |
| SpeechBrain | mock_only_accuracy_not_scored | 0 | 100 | 0 | N/A | N/A | N/A | N/A | 1.292 |
| NeMo | mock_only_accuracy_not_scored | 0 | 100 | 0 | N/A | N/A | N/A | N/A | 1.282 |

**Interpretation:** Mock outputs are synthetic pipeline fixtures. Accuracy and critical-term metrics are intentionally `N/A` for mock-only runs; simulated latency is not measured inference latency.

Code-switch category breakdown is available in `results/figures/codeswitch_breakdown.png` only when live outputs can be joined to manifest categories. Those categories are provisional script-share estimates until human confirmation.
<!-- END AUTO-GENERATED EVALUATION SUMMARY -->
